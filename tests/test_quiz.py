import unittest

from campusflow.quiz import QUESTIONS, score_answers


class TestEngineeringQuiz(unittest.TestCase):
    def test_question_bank_contains_six_questions(self):
        self.assertEqual(len(QUESTIONS), 6)

    def test_answer_key_matches_documented_bank(self):
        self.assertEqual(
            [question["answer"] for question in QUESTIONS],
            ["B", "C", "B", "C", "C", "B"],
        )

    def test_all_correct_answers_score_six(self):
        answers = [question["answer"] for question in QUESTIONS]
        self.assertEqual(score_answers(answers), 6)

    def test_all_wrong_answers_score_zero(self):
        answers = [
            next(
                letter
                for letter in ("A", "B", "C", "D")
                if letter != question["answer"]
            )
            for question in QUESTIONS
        ]
        self.assertEqual(score_answers(answers), 0)

    def test_partial_score(self):
        answers = [question["answer"] for question in QUESTIONS]
        answers[0] = next(
            letter for letter in ("A", "B", "C", "D")
            if letter != QUESTIONS[0]["answer"]
        )
        self.assertEqual(score_answers(answers), 5)

    def test_wrong_number_of_answers_is_rejected(self):
        with self.assertRaises(ValueError):
            score_answers(["A", "B"])


if __name__ == "__main__":
    unittest.main()
