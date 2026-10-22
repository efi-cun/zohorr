import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import DATABASE_URL

logger = logging.getLogger("recruit_arena.db")

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
        """
    ]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for ddl in ddl_statements:
                cur.execute(ddl)
            
            # Seed questions if empty
            cur.execute("SELECT COUNT(*) FROM recruit_questions;")
            count = cur.fetchone()[0]
            if count == 0:
                from app.questions_data import ZOHO_RECRUIT_QUESTIONS
                for q in ZOHO_RECRUIT_QUESTIONS:
                    cur.execute("""
                        INSERT INTO recruit_questions 
                        (id, order_num, type, category, title, question_text, options, correct_answer, explanation, time_limit_sec, points_base)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                        q["id"],
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
                logger.info(f"Seeded {len(ZOHO_RECRUIT_QUESTIONS)} Zoho Recruit questions into database.")
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
