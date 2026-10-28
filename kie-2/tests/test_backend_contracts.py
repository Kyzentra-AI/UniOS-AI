import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestBackendKIEGatewayContracts(unittest.TestCase):
    """Integration test suite validating exact contracts from Backend Section 14.1 & 14.2."""

    def setUp(self):
        self.client = TestClient(app)

    def test_section_14_1_interpret_endpoint(self):
        """Verify Section 14.1 POST /api/v1/kie/learn/interpret (AI-1)."""
        payload = {
            "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
            "learner_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
            "topic": "Binary Search Trees",
            "user_intent": "Explain tree traversals with visual analogies and code snippets",
            "references": [
                {
                    "module": "Data Structures - Module 3",
                    "heading": "Binary Search Tree Properties & Traversals",
                    "content": "A Binary Search Tree is a node-based binary tree data structure where each left child key is less than the parent and each right child key is greater.",
                    "page": 45,
                }
            ],
            "context": {
                "learner_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                "learner": {
                    "primary_goal": "Master Data Structures for Technical Interviews",
                    "target_skills": ["Binary Trees", "Recursion", "Algorithms"],
                    "skills": ["Python", "Arrays", "Linked Lists"],
                    "projects": ["CLI Task Manager"],
                    "research": "None",
                    "experience": "Intermediate Python programmer",
                    "inferred_context": {
                        "strength": "Iterative algorithms",
                        "weakness": "Recursive call stack mental models",
                    },
                },
                "education": {
                    "academic_status": "BACHELOR",
                    "university": "Apex Institute of Technology",
                    "degree_program": "B.Tech Computer Science",
                    "domain": "Computer Science & Engineering",
                    "current_year": "2nd Year",
                    "graduation_year": 2026,
                    "subjects": ["Data Structures", "Discrete Mathematics"],
                },
                "preferences": {
                    "daily_study_hours": "2_3",
                    "learning_depth": "DEEP",
                },
                "syllabus": {
                    "subjects": [
                        {
                            "name": "Data Structures",
                            "topics": ["Arrays", "Linked Lists", "Binary Trees", "Graphs"],
                        }
                    ]
                },
                "roadmap": {
                    "scope": "ACADEMIC",
                    "semesters": [],
                    "missions": [],
                },
                "recent_history": [
                    {
                        "id": "e4f8d2b1-6a3c-4e89-b1d5-8f0a2c3d4e5f",
                        "event_type": "SESSION_STARTED",
                        "entity_type": "LESSON",
                        "entity_id": "lesson-bst-101",
                        "payload": {},
                        "created_at": "2026-10-12T10:15:00Z",
                    }
                ],
                "memory_summary": {
                    "mastered_concepts": ["Linked Lists traversal", "Time complexity Big-O"],
                    "struggling_concepts": ["Recursive backtracking base conditions"],
                    "recommended_pacing": "Moderate with scaffolding",
                },
                "scope": "ACADEMIC",
            },
        }

        resp = self.client.post("/api/v1/kie/learn/interpret", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Validate Section 14.1.2 fields
        self.assertIn("intent_category", data)
        self.assertIn("pedagogical_strategy", data)
        self.assertIn("knowledge_gaps_identified", data)
        self.assertIsInstance(data["knowledge_gaps_identified"], list)
        self.assertGreaterEqual(len(data["knowledge_gaps_identified"]), 1)
        self.assertIn("target_difficulty", data)
        self.assertIn("recommended_block_flow", data)
        self.assertIn("key_concepts_to_cover", data)
        self.assertIn("metadata", data)

    def test_section_14_2_lesson_generate_endpoint(self):
        """Verify Section 14.2 POST /api/v1/kie/lesson/generate (AI-2)."""
        payload = {
            "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
            "learner_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
            "topic": "Binary Search Trees",
            "lesson_id": "lesson-bst-101",
            "interpreted_data": {
                "intent_category": "CODE_WALKTHROUGH",
                "pedagogical_strategy": "ANALOGY_THEN_CODE",
                "knowledge_gaps_identified": [
                    "recursion_call_stack_frames",
                    "tree_pointer_mutation",
                ],
                "target_difficulty": "INTERMEDIATE",
                "recommended_block_flow": [
                    "TEXT",
                    "CODE",
                    "INTERACTIVE",
                    "QUIZ",
                ],
                "key_concepts_to_cover": [
                    "BST ordering invariant (Left < Node < Right)",
                    "In-order DFS traversal yields sorted output",
                    "Recursive vs iterative stack implementation",
                ],
                "metadata": {
                    "scaffolding_level": "HIGH",
                    "estimated_read_minutes": 10,
                },
            },
            "references": [
                {
                    "module": "Data Structures - Module 3",
                    "heading": "Binary Search Tree Properties & Traversals",
                    "content": "A Binary Search Tree is a node-based binary tree data structure where each left child key is less than the parent and each right child key is greater.",
                    "page": 45,
                }
            ],
            "context": {
                "learner_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                "learner": {
                    "primary_goal": "Master Data Structures for Technical Interviews",
                    "skills": ["Python", "Arrays"],
                },
                "education": {
                    "academic_status": "BACHELOR",
                    "degree_program": "B.Tech Computer Science",
                },
                "scope": "ACADEMIC",
            },
        }

        resp = self.client.post("/api/v1/kie/lesson/generate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Validate Section 14.2.2 deserialization contract
        self.assertEqual(data["id"], "lesson-bst-101")
        self.assertIn("title", data)
        self.assertIn("objective", data)
        self.assertIn("prerequisites", data)
        self.assertIn("blocks", data)
        self.assertIsInstance(data["blocks"], list)
        self.assertGreaterEqual(len(data["blocks"]), 3)

        # Validate checkpoint block tracking: lesson.blocks[-1].id
        last_block = data["blocks"][-1]
        self.assertIn("id", last_block)
        self.assertTrue(len(last_block["id"]) > 0)

        # Validate LessonBlock structure
        block_types = [b["type"] for b in data["blocks"]]
        self.assertIn("TEXT", block_types)

        for b in data["blocks"]:
            self.assertIn("id", b)
            self.assertIn("type", b)
            self.assertIn(b["type"], ["TEXT", "CODE", "INTERACTIVE", "QUIZ", "VIDEO"])
            # Validate optional fields are present in serialized json (or null)
            self.assertIn("title", b)
            self.assertIn("content", b)


if __name__ == "__main__":
    unittest.main()
