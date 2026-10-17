"""Engineering Understanding Check for CampusFlow.

Engineer B owns this module. The question bank is the ``QUESTIONS`` data
structure and the scoring rules live in ``score_answers``. Scoring never
contains question text or correct answers of its own, so the bank can change
without touching the marking logic.

The module is deliberately free of ``input()`` and ``print()`` so that scoring
can be tested on its own; the CLI menu in ``main.py`` handles the interaction.
Explanations are recorded for mentor discussion and are never auto-graded.
"""

LETTERS = ("A", "B", "C", "D")

EXPLANATION_MINIMUM = 2

QUESTIONS = [
    {
        "id": "Q1",
        "scenario": (
            "Ticket T001 is open and unassigned. A user tries to move it to "
            "in_progress."
        ),
        "options": {
            "A": "Accept the change and mark it in_progress.",
            "B": "Reject the change and preserve all ticket data.",
            "C": "Resolve the ticket automatically.",
            "D": "Remove the ticket from the collection.",
        },
        "answer": "B",
    },
    {
        "id": "Q2",
        "scenario": "The application has zero tickets.",
        "options": {
            "A": "The report crashes with a division error.",
            "B": "The resolution percentage shows 100%.",
            "C": "The resolution percentage shows 0%.",
            "D": "The report divides by one without explanation.",
        },
        "answer": "C",
    },
    {
        "id": "Q3",
        "scenario": (
            "A search supplies title='wifi', category='Network' and "
            "status='open'."
        ),
        "options": {
            "A": "Any record matching at least one of the filters.",
            "B": "Only records matching all the supplied filters.",
            "C": "All network records, whatever their status.",
            "D": "All open records, whatever their category.",
        },
        "answer": "B",
    },
    {
        "id": "Q4",
        "scenario": "A resolved ticket receives an 'Add follow-up note' action.",
        "options": {
            "A": "Append the note anyway.",
            "B": "Delete the earlier notes and add the new one.",
            "C": "Reject the note until the ticket is reopened.",
            "D": "Change the status silently and add the note.",
        },
        "answer": "C",
    },
    {
        "id": "Q5",
        "scenario": (
            "The JSON data file contains two tickets with the same ticket ID."
        ),
        "options": {
            "A": "Keep both tickets in memory.",
            "B": "Replace memory with the duplicated records.",
            "C": "Reject the load without changing current memory.",
            "D": "Rename the duplicate IDs silently.",
        },
        "answer": "C",
    },
    {
        "id": "Q6",
        "scenario": (
            "A pull request changes ticket validation but adds no "
            "negative-case tests."
        ),
        "options": {
            "A": "Approve it because it runs without errors.",
            "B": "Request focused tests and reasoning before approval.",
            "C": "Merge it immediately.",
            "D": "Ask an AI tool to approve it.",
        },
        "answer": "B",
    },
]


def question_bank():
    """Return the six scenario questions as a fresh list of copies."""
    return [
        {
            "id": question["id"],
            "scenario": question["scenario"],
            "options": dict(question["options"]),
            "answer": question["answer"],
        }
        for question in QUESTIONS
    ]


def normalize_answer(answer):
    """Return 'A'-'D' for a submitted answer, or None when it is not valid."""
    if not isinstance(answer, str):
        return None

    letter = answer.strip().upper()

    if letter in LETTERS:
        return letter

    return None


def score_answers(answers, questions=None):
    """Score submitted answer letters against the question bank.

    ``answers`` is a list of submissions in question order. Each entry may be
    an answer letter (any case) or None when the learner skips a question.
    Exactly one entry is required for each question; a list with the wrong
    number of entries raises ValueError. A skipped or invalid answer is marked
    incorrect. One point is awarded per correct answer, so the score ranges
    from 0 to the number of questions.

    The caller may pass its own ``questions`` list, which shows that marking
    is driven by the bank rather than hard-coded in this function.
    """
    bank = QUESTIONS if questions is None else questions

    if not isinstance(bank, list):
        raise ValueError("Questions must be a list")

    if not isinstance(answers, list):
        raise ValueError("Answers must be a list")

    if len(answers) != len(bank):
        raise ValueError("There must be one answer per question")

    score = 0
    results = []

    for question, answer in zip(bank, answers):
        submitted = normalize_answer(answer)
        correct = submitted == question["answer"]

        if correct:
            score += 1

        results.append(
            {
                "id": question["id"],
                "answer": submitted,
                "correct_answer": question["answer"],
                "correct": correct,
            }
        )

    return {
        "score": score,
        "total": len(bank),
        "results": results,
    }
