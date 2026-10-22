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
