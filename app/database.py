import logging
import json
import hashlib
import secrets
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import DATABASE_URL

logger = logging.getLogger("recruit_arena.db")

def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a random salt."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return f"{salt}${pwd_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verifies a password against the stored salt$hash."""
    try:
        salt, pwd_hash = stored_hash.split('$', 1)
        check_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
        return secrets.compare_digest(pwd_hash, check_hash)
    except Exception:
        return False

def get_connection():
    """Returns a new psycopg2 connection to Supabase pooler."""
    return psycopg2.connect(DATABASE_URL, connect_timeout=10)

def init_db():
    """Creates tables in Supabase clean database and seeds initial questions."""
    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS recruit_game_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            room_code VARCHAR(30) NOT NULL UNIQUE,
            title VARCHAR(255) DEFAULT 'Zoho Recruit: Cyber-Talent Arena',
            status VARCHAR(50) DEFAULT 'LOBBY',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            ended_at TIMESTAMP WITH TIME ZONE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS recruit_participants (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id UUID REFERENCES recruit_game_sessions(id) ON DELETE CASCADE,
            room_code VARCHAR(30) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            role_or_area VARCHAR(255),
            nickname VARCHAR(100) NOT NULL,
            avatar VARCHAR(50) DEFAULT 'cyber_scout',
            score INT DEFAULT 0,
            correct_answers INT DEFAULT 0,
            total_answered INT DEFAULT 0,
            streak INT DEFAULT 0,
            final_rank INT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS recruit_questions (
            id VARCHAR(50) PRIMARY KEY,
            order_num INT NOT NULL,
            type VARCHAR(50) NOT NULL, -- 'ORDER_SEQUENCE', 'CHOICE', 'SCENARIO', 'SPEED_TRIAL'
            category VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            question_text TEXT NOT NULL,
            options JSONB NOT NULL,
            correct_answer JSONB NOT NULL,
            explanation TEXT,
            time_limit_sec INT DEFAULT 25,
            points_base INT DEFAULT 1000
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS recruit_answers (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id UUID REFERENCES recruit_game_sessions(id) ON DELETE CASCADE,
            participant_id UUID REFERENCES recruit_participants(id) ON DELETE CASCADE,
            question_id VARCHAR(50) REFERENCES recruit_questions(id) ON DELETE SET NULL,
            chosen_answer JSONB NOT NULL,
            is_correct BOOLEAN NOT NULL,
            response_time_ms INT NOT NULL,
            points_awarded INT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_participants_room ON recruit_participants(room_code);
        CREATE INDEX IF NOT EXISTS idx_participants_session ON recruit_participants(session_id);
        CREATE INDEX IF NOT EXISTS idx_answers_session ON recruit_answers(session_id);
        """,
        """
        CREATE TABLE IF NOT EXISTS recruit_users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'facilitator',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS recruit_topics (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            badge VARCHAR(100),
            description TEXT,
            default_pin VARCHAR(30),
            created_by VARCHAR(100) DEFAULT 'system',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        """
        ALTER TABLE recruit_topics ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
        ALTER TABLE recruit_questions ADD COLUMN IF NOT EXISTS topic_id VARCHAR(50) DEFAULT 'zoho_recruit';
        CREATE INDEX IF NOT EXISTS idx_questions_topic ON recruit_questions(topic_id);
        """
    ]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for ddl in ddl_statements:
                cur.execute(ddl)

            # Seed default users if empty
            cur.execute("SELECT COUNT(*) FROM recruit_users;")
            if cur.fetchone()[0] == 0:
                default_admin_pwd = hash_password("AdminCun2026*")
                default_facil_pwd = hash_password("Facilitador2026*")
                cur.execute("""
                    INSERT INTO recruit_users (username, email, password_hash, full_name, role)
                    VALUES 
                    (%s, %s, %s, %s, 'admin'),
                    (%s, %s, %s, %s, 'facilitator');
                """, (
                    "admin", "admin@cun.edu.co", default_admin_pwd, "Administrador CUN",
                    "facilitador", "facilitador@cun.edu.co", default_facil_pwd, "Facilitador CUN"
                ))
                logger.info("Default admin and facilitator users seeded.")

            # Seed initial topics
            from app.questions_data import TRAINING_TOPICS
            for tid, tdata in TRAINING_TOPICS.items():
                cur.execute("""
                    INSERT INTO recruit_topics (id, name, badge, description, default_pin, created_by)
                    VALUES (%s, %s, %s, %s, %s, 'system')
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        badge = EXCLUDED.badge,
                        description = EXCLUDED.description,
                        default_pin = EXCLUDED.default_pin;
                """, (tid, tdata["name"], tdata["badge"], tdata["description"], tdata["default_pin"]))

            # Synchronize questions with all topics defined in TRAINING_TOPICS
            from app.questions_data import get_all_questions
            all_questions = get_all_questions()
            for q in all_questions:
                q_topic_id = q.get("topic_id")
                if not q_topic_id:
                    if q["id"].startswith("zr-"):
                        q_topic_id = "zoho_recruit"
                    elif q["id"].startswith("sst-"):
                        q_topic_id = "sst_cun"
                    elif q["id"].startswith("onb-"):
                        q_topic_id = "onboarding_cun"
                    else:
                        q_topic_id = "zoho_recruit"

                cur.execute("""
                    INSERT INTO recruit_questions 
                    (id, topic_id, order_num, type, category, title, question_text, options, correct_answer, explanation, time_limit_sec, points_base)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        topic_id = EXCLUDED.topic_id,
                        order_num = EXCLUDED.order_num,
                        type = EXCLUDED.type,
                        category = EXCLUDED.category,
                        title = EXCLUDED.title,
                        question_text = EXCLUDED.question_text,
                        options = EXCLUDED.options,
                        correct_answer = EXCLUDED.correct_answer,
                        explanation = EXCLUDED.explanation,
                        time_limit_sec = EXCLUDED.time_limit_sec,
                        points_base = EXCLUDED.points_base;
                """, (
                    q["id"],
                    q_topic_id,
                    q["order_num"],
                    q["type"],
                    q["category"],
                    q["title"],
                    q["question_text"],
                    json.dumps(q["options"]),
                    json.dumps(q.get("correct_order") or q.get("correct_answer")),
                    q.get("explanation", ""),
                    q.get("time_limit_sec", 25),
                    q.get("points_base", 1000)
                ))
            logger.info(f"Synchronized {len(all_questions)} multi-topic questions with database.")
        conn.commit()
        logger.info("Supabase database tables successfully initialized.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing Supabase database: {e}")
        raise e
    finally:
        conn.close()

def create_or_get_session(room_code: str, title: str = "Zoho Recruit: Cyber-Talent Arena"):
    """Inserts or retrieves a game session."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO recruit_game_sessions (room_code, title, status)
                VALUES (%s, %s, 'LOBBY')
                ON CONFLICT (room_code) DO UPDATE SET status = 'LOBBY', ended_at = NULL
                RETURNING *;
            """, (room_code, title))
            session = cur.fetchone()
            conn.commit()
            return session
    finally:
        conn.close()

def update_session_title(room_code: str, title: str):
    """Updates the title/topic of a session in Supabase."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE recruit_game_sessions
                SET title = %s
                WHERE room_code = %s;
            """, (title, room_code))
            conn.commit()
    finally:
        conn.close()

def register_participant(room_code: str, full_name: str, email: str, role_or_area: str, nickname: str, avatar: str):
    """Registers a participant and links them to the session."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM recruit_game_sessions WHERE room_code = %s", (room_code,))
            sess = cur.fetchone()
            session_id = sess["id"] if sess else None

            cur.execute("""
                INSERT INTO recruit_participants 
                (session_id, room_code, full_name, email, role_or_area, nickname, avatar, score, correct_answers, total_answered, streak)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 0, 0, 0, 0)
                RETURNING *;
            """, (session_id, room_code, full_name, email, role_or_area, nickname, avatar))
            part = cur.fetchone()
            conn.commit()
            return part
    finally:
        conn.close()

def record_answer(session_id: str, participant_id: str, question_id: str, chosen_answer, is_correct: bool, response_time_ms: int, points_awarded: int, new_streak: int, new_score: int):
    """Records an individual answer and updates participant totals."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO recruit_answers 
                (session_id, participant_id, question_id, chosen_answer, is_correct, response_time_ms, points_awarded)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (session_id, participant_id, question_id, json.dumps(chosen_answer), is_correct, response_time_ms, points_awarded))

            cur.execute("""
                UPDATE recruit_participants
                SET score = %s,
                    streak = %s,
                    correct_answers = correct_answers + (CASE WHEN %s THEN 1 ELSE 0 END),
                    total_answered = total_answered + 1
                WHERE id = %s;
            """, (new_score, new_streak, is_correct, participant_id))
            conn.commit()
    finally:
        conn.close()

def finish_session_in_db(room_code: str, ranked_players: list):
    """Marks session as finished and updates final rankings."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE recruit_game_sessions
                SET status = 'FINISHED', ended_at = NOW()
                WHERE room_code = %s;
            """, (room_code,))

            for rank, p in enumerate(ranked_players, start=1):
                cur.execute("""
                    UPDATE recruit_participants
                    SET final_rank = %s
                    WHERE id = %s;
                """, (rank, p["id"]))
            conn.commit()
    finally:
        conn.close()

def get_session_export_rows(room_code: str):
    """Retrieves all participants for export."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    p.final_rank AS "Puesto",
                    p.full_name AS "Nombre Completo",
                    p.email AS "Correo",
                    p.role_or_area AS "Cargo / Area",
                    p.nickname AS "Nickname",
                    p.score AS "Puntaje Total",
                    p.correct_answers AS "Aciertos",
                    p.total_answered AS "Total Preguntas",
                    ROUND((p.correct_answers::numeric / NULLIF(p.total_answered, 0)) * 100, 1) AS "Efectividad_Porcentaje",
                    p.created_at AS "Fecha Registro"
                FROM recruit_participants p
                WHERE p.room_code = %s
                ORDER BY p.score DESC;
            """, (room_code,))
            return cur.fetchall()
    finally:
        conn.close()

# ==============================================================================
# AUTHENTICATION & USER MANAGEMENT
# ==============================================================================

def authenticate_user(username: str, password: str):
    """Authenticates username & password, returns user dict without password_hash or None."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, username, email, password_hash, full_name, role, is_active, created_at
                FROM recruit_users
                WHERE LOWER(username) = LOWER(%s);
            """, (username.strip(),))
            user = cur.fetchone()
            if not user:
                return None
            if not user["is_active"]:
                return {"error": "Usuario desactivado. Contacta al administrador."}
            if not verify_password(password, user["password_hash"]):
                return None
            
            # Remove hash before returning
            del user["password_hash"]
            user["id"] = str(user["id"])
            user["created_at"] = user["created_at"].isoformat() if user.get("created_at") else None
            return user
    finally:
        conn.close()

def get_user_by_id(user_id: str):
    """Fetches user by UUID."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, username, email, full_name, role, is_active, created_at
                FROM recruit_users
                WHERE id = %s;
            """, (user_id,))
            user = cur.fetchone()
            if user:
                user["id"] = str(user["id"])
                user["created_at"] = user["created_at"].isoformat() if user.get("created_at") else None
            return user
    finally:
        conn.close()

def get_all_users():
    """Returns all users in the system."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, username, email, full_name, role, is_active, created_at
                FROM recruit_users
                ORDER BY created_at DESC;
            """, ())
            rows = cur.fetchall()
            for r in rows:
                r["id"] = str(r["id"])
                r["created_at"] = r["created_at"].isoformat() if r.get("created_at") else None
            return rows
    finally:
        conn.close()

def create_user(username: str, email: str, password: str, full_name: str, role: str = "facilitator"):
    """Creates a new admin or facilitator."""
    role = role.lower().strip()
    if role not in ["admin", "facilitator"]:
        role = "facilitator"
    pwd_hash = hash_password(password)
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO recruit_users (username, email, password_hash, full_name, role)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, username, email, full_name, role, is_active, created_at;
            """, (username.strip(), email.strip(), pwd_hash, full_name.strip(), role))
            user = cur.fetchone()
            conn.commit()
            if user:
                user["id"] = str(user["id"])
                user["created_at"] = user["created_at"].isoformat() if user.get("created_at") else None
            return user
    finally:
        conn.close()

def update_user_status(user_id: str, is_active: bool):
    """Activates or deactivates a user."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE recruit_users
                SET is_active = %s
                WHERE id = %s;
            """, (is_active, user_id))
            conn.commit()
            return True
    finally:
        conn.close()

def delete_user(user_id: str):
    """Deletes a user if not the last admin."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT role FROM recruit_users WHERE id = %s;", (user_id,))
            row = cur.fetchone()
            if not row:
                return False
            if row[0] == "admin":
                cur.execute("SELECT COUNT(*) FROM recruit_users WHERE role = 'admin' AND is_active = TRUE;")
                if cur.fetchone()[0] <= 1:
                    raise ValueError("No se puede eliminar el único administrador activo del sistema.")
            cur.execute("DELETE FROM recruit_users WHERE id = %s;", (user_id,))
            conn.commit()
            return True
    finally:
        conn.close()

# ==============================================================================
# TOPICS & EVALUATIONS CRUD
# ==============================================================================

def get_all_topics_from_db(include_hidden: bool = True):
    """Returns topics list with count of questions."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    t.id, 
                    t.name, 
                    t.badge, 
                    t.description, 
                    t.default_pin, 
                    t.created_by,
                    t.created_at,
                    COALESCE(t.is_active, TRUE) AS is_active,
                    COUNT(q.id) AS question_count
                FROM recruit_topics t
                LEFT JOIN recruit_questions q ON t.id = q.topic_id
                GROUP BY t.id, t.name, t.badge, t.description, t.default_pin, t.created_by, t.created_at, t.is_active
                ORDER BY t.created_at ASC;
            """)
            rows = cur.fetchall()
            for r in rows:
                r["created_at"] = r["created_at"].isoformat() if r.get("created_at") else None
                r["question_count"] = int(r.get("question_count") or 0)
                r["is_active"] = bool(r.get("is_active", True))
            if not include_hidden:
                return [r for r in rows if r["is_active"]]
            return rows
    finally:
        conn.close()

def get_topic_from_db(topic_id: str):
    """Fetches a full topic including all its questions."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, badge, description, default_pin, created_by, created_at, COALESCE(is_active, TRUE) AS is_active
                FROM recruit_topics
                WHERE id = %s;
            """, (topic_id,))
            topic = cur.fetchone()
            if not topic:
                return None
            topic["is_active"] = bool(topic.get("is_active", True))
            
            cur.execute("""
                SELECT id, topic_id, order_num, type, category, title, question_text, options, correct_answer, explanation, time_limit_sec, points_base
                FROM recruit_questions
                WHERE topic_id = %s
                ORDER BY order_num ASC, id ASC;
            """, (topic_id,))
            questions = cur.fetchall()
            # Normalize JSON fields
            for q in questions:
                if isinstance(q.get("options"), str):
                    q["options"] = json.loads(q["options"])
                if isinstance(q.get("correct_answer"), str):
                    try:
                        q["correct_answer"] = json.loads(q["correct_answer"])
                    except Exception:
                        pass
                if q["type"] == "ORDER_SEQUENCE":
                    q["correct_order"] = q.get("correct_answer") if isinstance(q.get("correct_answer"), list) else []

            topic["questions"] = questions
            topic["created_at"] = topic["created_at"].isoformat() if topic.get("created_at") else None
            return topic
    finally:
        conn.close()

def save_topic(topic_id: str, name: str, badge: str, description: str, default_pin: str, created_by: str = "admin"):
    """Inserts or updates a topic."""
    topic_id = topic_id.lower().strip().replace(" ", "_")
    default_pin = default_pin.upper().strip()
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO recruit_topics (id, name, badge, description, default_pin, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    badge = EXCLUDED.badge,
                    description = EXCLUDED.description,
                    default_pin = EXCLUDED.default_pin
                RETURNING *;
            """, (topic_id, name.strip(), badge.strip(), description.strip(), default_pin, created_by))
            topic = cur.fetchone()
            conn.commit()
            if topic:
                topic["created_at"] = topic["created_at"].isoformat() if topic.get("created_at") else None
            return topic
    finally:
        conn.close()

def delete_topic(topic_id: str):
    """Deletes topic and its questions."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM recruit_questions WHERE topic_id = %s;", (topic_id,))
            cur.execute("DELETE FROM recruit_topics WHERE id = %s;", (topic_id,))
            conn.commit()
            return True
    finally:
        conn.close()

def toggle_topic_visibility(topic_id: str, is_active: Optional[bool] = None) -> bool:
    """Toggles or sets the active/visible status of a topic."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if is_active is None:
                cur.execute("""
                    UPDATE recruit_topics 
                    SET is_active = NOT COALESCE(is_active, TRUE) 
                    WHERE id = %s
                    RETURNING is_active;
                """, (topic_id,))
            else:
                cur.execute("""
                    UPDATE recruit_topics 
                    SET is_active = %s 
                    WHERE id = %s
                    RETURNING is_active;
                """, (is_active, topic_id))
            row = cur.fetchone()
            conn.commit()
            return bool(row[0]) if row else True
    finally:
        conn.close()

def get_questions_by_topic(topic_id: str):
    """Retrieves all questions belonging to a topic."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, topic_id, order_num, type, category, title, question_text, options, correct_answer, explanation, time_limit_sec, points_base
                FROM recruit_questions
                WHERE topic_id = %s
                ORDER BY order_num ASC, id ASC;
            """, (topic_id,))
            questions = cur.fetchall()
            for q in questions:
                if isinstance(q.get("options"), str):
                    q["options"] = json.loads(q["options"])
                if isinstance(q.get("correct_answer"), str):
                    try:
                        q["correct_answer"] = json.loads(q["correct_answer"])
                    except Exception:
                        pass
                if q["type"] == "ORDER_SEQUENCE":
                    q["correct_order"] = q.get("correct_answer") if isinstance(q.get("correct_answer"), list) else []
            return questions
    finally:
        conn.close()

def save_question(q_data: dict):
    """Inserts or updates a question in recruit_questions."""
    q_id = q_data.get("id") or f"{q_data.get('topic_id', 'topic')}-{q_data.get('order_num', 1)}-{secrets.token_hex(2)}"
    topic_id = q_data.get("topic_id", "zoho_recruit")
    order_num = int(q_data.get("order_num", 1))
    q_type = q_data.get("type", "CHOICE")
    category = q_data.get("category", "GENERAL")
    title = q_data.get("title", "Pregunta")
    question_text = q_data.get("question_text", "")
    options = q_data.get("options", [])
    correct = q_data.get("correct_order") if q_type == "ORDER_SEQUENCE" else q_data.get("correct_answer")
    explanation = q_data.get("explanation", "")
    time_limit_sec = int(q_data.get("time_limit_sec", 25))
    points_base = int(q_data.get("points_base", 1000))

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO recruit_questions
                (id, topic_id, order_num, type, category, title, question_text, options, correct_answer, explanation, time_limit_sec, points_base)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    topic_id = EXCLUDED.topic_id,
                    order_num = EXCLUDED.order_num,
                    type = EXCLUDED.type,
                    category = EXCLUDED.category,
                    title = EXCLUDED.title,
                    question_text = EXCLUDED.question_text,
                    options = EXCLUDED.options,
                    correct_answer = EXCLUDED.correct_answer,
                    explanation = EXCLUDED.explanation,
                    time_limit_sec = EXCLUDED.time_limit_sec,
                    points_base = EXCLUDED.points_base
                RETURNING *;
            """, (
                q_id, topic_id, order_num, q_type, category, title, question_text,
                json.dumps(options), json.dumps(correct), explanation, time_limit_sec, points_base
            ))
            saved = cur.fetchone()
            conn.commit()
            return saved
    finally:
        conn.close()

def delete_question(question_id: str):
    """Deletes a question by ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM recruit_questions WHERE id = %s;", (question_id,))
            conn.commit()
            return True
    finally:
        conn.close()

def get_sessions_history():
    """Retrieves all past sessions with stats."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    s.id,
                    s.room_code,
                    s.title,
                    s.status,
                    s.created_at,
                    s.ended_at,
                    COUNT(p.id) AS total_participants,
                    COALESCE(ROUND(AVG(p.score), 0), 0) AS avg_score,
                    COALESCE(MAX(p.score), 0) AS max_score
                FROM recruit_game_sessions s
                LEFT JOIN recruit_participants p ON s.id = p.session_id
                GROUP BY s.id, s.room_code, s.title, s.status, s.created_at, s.ended_at
                ORDER BY s.created_at DESC;
            """)
            rows = cur.fetchall()
            for r in rows:
                r["id"] = str(r["id"])
                r["created_at"] = r["created_at"].isoformat() if r.get("created_at") else None
                r["ended_at"] = r["ended_at"].isoformat() if r.get("ended_at") else None
                r["total_participants"] = int(r.get("total_participants") or 0)
                r["avg_score"] = int(r.get("avg_score") or 0)
                r["max_score"] = int(r.get("max_score") or 0)
            return rows
    finally:
        conn.close()

# ==============================================================================
# PARTICIPANTS & COMPREHENSIVE ANALYTICS
# ==============================================================================

def get_all_participants(topic_filter: Optional[str] = None, search: Optional[str] = None):
    """Retrieves all evaluated participants with session title and performance."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT 
                    p.id,
                    p.session_id,
                    p.room_code,
                    p.full_name,
                    p.email,
                    p.role_or_area,
                    p.nickname,
                    p.avatar,
                    p.score,
                    p.correct_answers,
                    p.total_answered,
                    p.streak,
                    p.final_rank,
                    p.created_at,
                    COALESCE(s.title, 'Evaluación General') AS evaluation_title,
                    COALESCE(ROUND((p.correct_answers::numeric / NULLIF(p.total_answered, 0)) * 100, 1), 0) AS effectiveness_percent
                FROM recruit_participants p
                LEFT JOIN recruit_game_sessions s ON p.session_id = s.id
                WHERE 1=1
            """
            params = []
            if search and search.strip():
                s_param = f"%{search.strip()}%"
                query += " AND (p.full_name ILIKE %s OR p.email ILIKE %s OR p.role_or_area ILIKE %s OR p.nickname ILIKE %s)"
                params.extend([s_param, s_param, s_param, s_param])
            if topic_filter and topic_filter.strip() and topic_filter.strip().lower() != "all":
                t_param = f"%{topic_filter.strip()}%"
                query += " AND (s.room_code ILIKE %s OR s.title ILIKE %s)"
                params.extend([t_param, t_param])
            query += " ORDER BY p.created_at DESC;"

            cur.execute(query, tuple(params) if params else None)
            rows = cur.fetchall()
            for r in rows:
                r["id"] = str(r["id"])
                if r.get("session_id"):
                    r["session_id"] = str(r["session_id"])
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].isoformat()
                r["score"] = int(r.get("score") or 0)
                r["correct_answers"] = int(r.get("correct_answers") or 0)
                r["total_answered"] = int(r.get("total_answered") or 0)
                r["effectiveness_percent"] = float(r.get("effectiveness_percent") or 0.0)
            return rows
    finally:
        conn.close()

def get_participant_detail_with_answers(participant_id: str):
    """Retrieves single participant details along with breakdown of their submitted answers."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    p.id,
                    p.session_id,
                    p.room_code,
                    p.full_name,
                    p.email,
                    p.role_or_area,
                    p.nickname,
                    p.avatar,
                    p.score,
                    p.correct_answers,
                    p.total_answered,
                    p.created_at,
                    COALESCE(s.title, 'Evaluación General') AS evaluation_title,
                    COALESCE(ROUND((p.correct_answers::numeric / NULLIF(p.total_answered, 0)) * 100, 1), 0) AS effectiveness_percent
                FROM recruit_participants p
                LEFT JOIN recruit_game_sessions s ON p.session_id = s.id
                WHERE p.id::text = %s;
            """, (participant_id,))
            part = cur.fetchone()
            if not part:
                return None
            part["id"] = str(part["id"])
            if part.get("session_id"):
                part["session_id"] = str(part["session_id"])
            if part.get("created_at"):
                part["created_at"] = part["created_at"].isoformat()
            part["score"] = int(part.get("score") or 0)
            part["correct_answers"] = int(part.get("correct_answers") or 0)
            part["total_answered"] = int(part.get("total_answered") or 0)
            part["effectiveness_percent"] = float(part.get("effectiveness_percent") or 0.0)

            cur.execute("""
                SELECT 
                    a.id,
                    a.question_id,
                    COALESCE(q.title, a.question_id) AS question_title,
                    COALESCE(q.question_text, '') AS question_text,
                    COALESCE(q.category, 'GENERAL') AS category,
                    COALESCE(q.type, 'CHOICE') AS question_type,
                    a.chosen_answer,
                    q.correct_answer,
                    a.is_correct,
                    a.response_time_ms,
                    a.points_awarded,
                    a.created_at
                FROM recruit_answers a
                LEFT JOIN recruit_questions q ON a.question_id = q.id
                WHERE a.participant_id::text = %s
                ORDER BY a.created_at ASC;
            """, (participant_id,))
            answers = cur.fetchall()
            for ans in answers:
                ans["id"] = str(ans["id"])
                if ans.get("created_at"):
                    ans["created_at"] = ans["created_at"].isoformat()
                if isinstance(ans.get("chosen_answer"), str):
                    try:
                        ans["chosen_answer"] = json.loads(ans["chosen_answer"])
                    except Exception:
                        pass
                if isinstance(ans.get("correct_answer"), str):
                    try:
                        ans["correct_answer"] = json.loads(ans["correct_answer"])
                    except Exception:
                        pass
            part["answers"] = answers
            return part
    finally:
        conn.close()

def get_analytics_dashboard_data():
    """Calculates comprehensive platform analytics: participation, scores, topics, and question difficulty."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. Global Metrics
            cur.execute("""
                SELECT 
                    COUNT(p.id) AS total_participants,
                    COALESCE(ROUND(AVG(p.score), 0), 0) AS avg_score,
                    COALESCE(MAX(p.score), 0) AS max_score,
                    COALESCE(SUM(p.correct_answers), 0) AS total_correct_answers,
                    COALESCE(SUM(p.total_answered), 0) AS total_answered,
                    COALESCE(ROUND((SUM(p.correct_answers)::numeric / NULLIF(SUM(p.total_answered), 0)) * 100, 1), 0) AS global_accuracy_percent,
                    COUNT(CASE WHEN (p.correct_answers::numeric / NULLIF(p.total_answered, 0)) >= 0.7 THEN 1 END) AS approved_count
                FROM recruit_participants p;
            """)
            glob = cur.fetchone() or {}
            total_p = int(glob.get("total_participants") or 0)
            approved = int(glob.get("approved_count") or 0)
            approval_rate = round((approved / total_p * 100), 1) if total_p > 0 else 0.0

            # 2. Topic / Session Breakdown
            cur.execute("""
                SELECT 
                    COALESCE(s.title, 'Evaluación General') AS topic_title,
                    COUNT(p.id) AS participants_count,
                    COALESCE(ROUND(AVG(p.score), 0), 0) AS avg_score,
                    COALESCE(MAX(p.score), 0) AS top_score,
                    COALESCE(ROUND(AVG((p.correct_answers::numeric / NULLIF(p.total_answered, 0)) * 100), 1), 0) AS avg_accuracy
                FROM recruit_participants p
                LEFT JOIN recruit_game_sessions s ON p.session_id = s.id
                GROUP BY s.title
                ORDER BY participants_count DESC;
            """)
            topic_stats = cur.fetchall()
            for ts in topic_stats:
                ts["participants_count"] = int(ts.get("participants_count") or 0)
                ts["avg_score"] = int(ts.get("avg_score") or 0)
                ts["top_score"] = int(ts.get("top_score") or 0)
                ts["avg_accuracy"] = float(ts.get("avg_accuracy") or 0.0)

            # 3. Top Leaderboard (Cuadro de Honor)
            cur.execute("""
                SELECT 
                    p.id,
                    p.full_name,
                    p.email,
                    p.role_or_area,
                    p.nickname,
                    p.avatar,
                    p.score,
                    p.correct_answers,
                    p.total_answered,
                    COALESCE(ROUND((p.correct_answers::numeric / NULLIF(p.total_answered, 0)) * 100, 1), 0) AS effectiveness_percent,
                    COALESCE(s.title, 'Evaluación') AS topic_title
                FROM recruit_participants p
                LEFT JOIN recruit_game_sessions s ON p.session_id = s.id
                ORDER BY p.score DESC, p.correct_answers DESC
                LIMIT 10;
            """)
            top_p = cur.fetchall()
            for tp in top_p:
                tp["id"] = str(tp["id"])
                tp["score"] = int(tp.get("score") or 0)
                tp["correct_answers"] = int(tp.get("correct_answers") or 0)
                tp["total_answered"] = int(tp.get("total_answered") or 0)
                tp["effectiveness_percent"] = float(tp.get("effectiveness_percent") or 0.0)

            # 4. Question Difficulty Diagnosis (Hardest & Most Failed)
            cur.execute("""
                SELECT 
                    q.id,
                    q.title,
                    q.category,
                    COUNT(a.id) AS attempts_count,
                    SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) AS correct_count,
                    COALESCE(ROUND((SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(a.id), 0)) * 100, 1), 0) AS correct_percent,
                    COALESCE(ROUND(AVG(a.response_time_ms) / 1000.0, 1), 0) AS avg_time_sec
                FROM recruit_answers a
                JOIN recruit_questions q ON a.question_id = q.id
                GROUP BY q.id, q.title, q.category
                ORDER BY correct_percent ASC, attempts_count DESC
                LIMIT 8;
            """)
            q_stats = cur.fetchall()
            for qs in q_stats:
                qs["attempts_count"] = int(qs.get("attempts_count") or 0)
                qs["correct_count"] = int(qs.get("correct_count") or 0)
                qs["correct_percent"] = float(qs.get("correct_percent") or 0.0)
                qs["avg_time_sec"] = float(qs.get("avg_time_sec") or 0.0)

            return {
                "total_participants": total_p,
                "avg_score": int(glob.get("avg_score") or 0),
                "max_score": int(glob.get("max_score") or 0),
                "total_answered": int(glob.get("total_answered") or 0),
                "global_accuracy_percent": float(glob.get("global_accuracy_percent") or 0.0),
                "approval_rate": approval_rate,
                "topic_breakdown": topic_stats,
                "top_participants": top_p,
                "question_stats": q_stats
            }
    finally:
        conn.close()

def get_all_participants_export_rows():
    """Retrieves all participants across all evaluations for CSV/Excel export."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY p.score DESC) AS "No",
                    p.full_name AS "Nombre Completo",
                    p.email AS "Correo Institucional",
                    p.role_or_area AS "Cargo o Area",
                    p.nickname AS "Nickname",
                    COALESCE(s.title, 'Evaluacion General') AS "Evaluacion",
                    p.score AS "Puntaje Total",
                    p.correct_answers AS "Aciertos",
                    p.total_answered AS "Total Preguntas",
                    COALESCE(ROUND((p.correct_answers::numeric / NULLIF(p.total_answered, 0)) * 100, 1), 0) AS "Efectividad Porcentaje",
                    CASE 
                        WHEN (p.correct_answers::numeric / NULLIF(p.total_answered, 0)) >= 0.8 THEN 'Excelente'
                        WHEN (p.correct_answers::numeric / NULLIF(p.total_answered, 0)) >= 0.6 THEN 'Aprobado'
                        ELSE 'Requiere Refuerzo'
                    END AS "Resultado",
                    TO_CHAR(p.created_at, 'YYYY-MM-DD HH24:MI') AS "Fecha Realizacion"
                FROM recruit_participants p
                LEFT JOIN recruit_game_sessions s ON p.session_id = s.id
                ORDER BY p.score DESC;
            """)
            return cur.fetchall()
    finally:
        conn.close()
