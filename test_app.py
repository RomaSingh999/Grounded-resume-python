import unittest

from app import app
from grounded import Index, answer, build_facts, load_resume


class GroundingTests(unittest.TestCase):
    def setUp(self):
        self.index = Index(build_facts(load_resume()))
        self.client = app.test_client()

    def test_answers_from_resume(self):
        r = answer("Where did she study?", self.index)
        self.assertTrue(r["grounded"])
        self.assertIn("Chandigarh University", r["answer"])
        self.assertTrue(r["sources"])

    def test_skills_question(self):
        r = answer("Does she know FastAPI?", self.index)
        self.assertTrue(r["grounded"])
        self.assertIn("FastAPI", r["answer"])

    def test_work_history(self):
        r = answer("Where has she worked?", self.index)
        self.assertIn("YNV Technologies", r["answer"])

    def test_refuses_unknown(self):
        for q in ["What is her salary expectation?", "Does she know Kubernetes?",
                  "What is her favourite movie?"]:
            r = answer(q, self.index)
            self.assertFalse(r["grounded"], q)
            self.assertEqual(r["sources"], [])

    def test_todo_never_leaks(self):
        for q in ["What is her email?", "Tell me about her projects", "Tell me about YNV"]:
            self.assertNotIn("TODO", answer(q, self.index)["answer"])

    def test_partial_answer_flags_unknown(self):
        r = answer("Does she know Python and Kubernetes?", self.index)
        self.assertTrue(r["grounded"])
        self.assertIn("kubernetes", r["answer"].lower())
        self.assertIn("does not mention", r["answer"])

    def test_empty_question(self):
        self.assertFalse(answer("", self.index)["grounded"])

    def test_routes(self):
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertNotIn(b"TODO", page.data)
        self.assertIn(b"Roma Singh", page.data)
        res = self.client.post("/api/chat", json={"question": "Which skills does she have?"})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["grounded"])
        self.assertEqual(self.client.get("/health").status_code, 200)


if __name__ == "__main__":
    unittest.main()
