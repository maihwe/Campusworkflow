
QUESTIONS = [
    {
        "question": (
            "Ticket T001 is open and unassigned. A user tries to move it "
            "to in_progress. What should happen?"
        ),
        "options": {
            "A": "Accept the change",
            "B": "Reject it and preserve all ticket data",
            "C": "Resolve it automatically",
            "D": "Remove the ticket",
        },
        "answer": "B",
    },
    {
        "question": (
            "The application has zero tickets. What should the resolution "
            "percentage display?"
        ),
        "options": {
            "A": "Crash",
            "B": "100%",
            "C": "0%",
            "D": "Divide by one without explanation",
        },
        "answer": "C",
    },
    {
        "question": (
            "Search supplies title='wifi', category='Network' and "
            "status='open'. Which records should match?"
        ),
        "options": {
            "A": "Records matching any one filter",
            "B": "Only records matching all supplied filters",
            "C": "All Network records",
            "D": "All open records",
        },
        "answer": "B",
    },
    {
        "question": (
            "A resolved ticket receives an 'Add follow-up note' action. "
            "What should happen?"
        ),
        "options": {
            "A": "Append the note anyway",
            "B": "Delete the earlier notes",
            "C": "Reject the note until the ticket is reopened",
            "D": "Change the status silently",
        },
        "answer": "C",
    },
    {
        "question": (
            "The JSON file contains two tickets with the same ticket ID. "
            "What should loading do?"
        ),
        "options": {
            "A": "Keep both tickets",
            "B": "Replace memory with the duplicates",
            "C": "Reject the load without changing current memory",
            "D": "Rename the IDs silently",
        },
        "answer": "C",
    },
    {
        "question": (
            "A pull request changes validation but adds no negative-case "
            "tests. What is the best review action?"
        ),
        "options": {
            "A": "Approve it because it runs",
            "B": "Request focused tests and reasoning",
            "C": "Merge it immediately",
            "D": "Ask AI to approve it",
        },
        "answer": "B",
    },
]


def score_answers(answers):
    """Return the number of correct answers out of six."""
    if len(answers) != len(QUESTIONS):
        raise ValueError("Exactly six answers are required.")

    return sum(
        answer == question["answer"]
        for answer, question in zip(answers, QUESTIONS)
    )
