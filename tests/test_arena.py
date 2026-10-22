import unittest
import asyncio
from app.questions_data import ZOHO_RECRUIT_QUESTIONS
from app.game_manager import GameManager, Room
from app.database import get_connection, get_session_export_rows

class TestZohoRecruitCyberArena(unittest.TestCase):

    def test_question_bank_structure(self):
        """Verifies all questions have required fields and valid options."""
        self.assertGreaterEqual(len(ZOHO_RECRUIT_QUESTIONS), 10)
        
        sequence_questions = [q for q in ZOHO_RECRUIT_QUESTIONS if q["type"] == "ORDER_SEQUENCE"]
        self.assertGreaterEqual(len(sequence_questions), 3, "Must have at least 3 ORDER_SEQUENCE questions")

        for q in ZOHO_RECRUIT_QUESTIONS:
            self.assertIn("id", q)
            self.assertIn("title", q)
            self.assertIn("question_text", q)
            self.assertIn("options", q)
            self.assertEqual(len(q["options"]), 4 if q["type"] != "SPEED_TRIAL" else 2)
            
            if q["type"] == "ORDER_SEQUENCE":
                self.assertIn("correct_order", q)
                self.assertEqual(len(q["correct_order"]), 4)
            else:
                self.assertIn("correct_answer", q)

    def test_database_connection_and_tables(self):
        """Verifies that Supabase tables exist and can be queried."""
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                tables = [r[0] for r in cur.fetchall()]
                for expected_table in ['recruit_game_sessions', 'recruit_participants', 'recruit_questions', 'recruit_answers']:
                    self.assertIn(expected_table, tables)
        finally:
            conn.close()

    def test_order_sequence_evaluation_and_scoring(self):
        """Tests that correct order sequence awards points and updates streak."""
        gm = GameManager()
        room = gm.get_or_create_room("TEST_ROOM")
        
        # Register two players
        p_wrong = asyncio.run(gm.register_player(
            room_code="TEST_ROOM",
            full_name="Carlos Gomez",
            email="carlos@cun.edu.co",
            role_or_area="Talento Humano",
            nickname="Operador_A",
            avatar="talent_hunter"
        ))

        p_correct = asyncio.run(gm.register_player(
            room_code="TEST_ROOM",
            full_name="Mariana Ruiz",
            email="mariana@cun.edu.co",
            role_or_area="Seleccion CUN",
            nickname="Operador_B",
            avatar="quantum_ai"
        ))

        self.assertEqual(p_wrong["score"], 0)
        self.assertEqual(p_correct["score"], 0)

        # Launch Q1 (ORDER_SEQUENCE)
        asyncio.run(gm.start_game("TEST_ROOM"))
        self.assertEqual(room.current_question["type"], "ORDER_SEQUENCE")

        # Player 1 submits WRONG order
        wrong_order = ["opt_D", "opt_C", "opt_B", "opt_A"]
        asyncio.run(gm.submit_answer("TEST_ROOM", p_wrong["id"], wrong_order))
        
        self.assertEqual(p_wrong["score"], 0)
        self.assertEqual(p_wrong["streak"], 0)

        # Player 2 submits CORRECT order
        correct_order = room.current_question["correct_order"]
        asyncio.run(gm.submit_answer("TEST_ROOM", p_correct["id"], correct_order))

        self.assertGreater(p_correct["score"], 500)
        self.assertEqual(p_correct["streak"], 1)

    def test_multi_topic_switching(self):
        """Verifies multi-topic catalog and room topic switching."""
        from app.questions_data import TRAINING_TOPICS, get_all_topics
        topics = get_all_topics()
        self.assertGreaterEqual(len(topics), 3)

        gm = GameManager()
        room = gm.get_or_create_room("ROOM_TOPIC_TEST")
        self.assertEqual(room.topic_id, "zoho_recruit")

        # Change topic to SST
        success = asyncio.run(gm.change_topic("ROOM_TOPIC_TEST", "sst_cun"))
        self.assertTrue(success)
        self.assertEqual(room.topic_id, "sst_cun")
        self.assertIn("Seguridad", room.title)
        self.assertEqual(len(room.questions), 10)
        self.assertTrue(room.questions[0]["id"].startswith("sst-"))

        # Change topic to Onboarding
        success = asyncio.run(gm.change_topic("ROOM_TOPIC_TEST", "onboarding_cun"))
        self.assertTrue(success)
        self.assertEqual(room.topic_id, "onboarding_cun")
        self.assertIn("Cultura", room.title)
        self.assertEqual(len(room.questions), 10)
        self.assertTrue(room.questions[0]["id"].startswith("onb-"))

if __name__ == "__main__":
    unittest.main()
