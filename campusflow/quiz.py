QUESTIONS = [
    {
        "question": "What should happen when a ticket ID does not exist?",
        "options": {
            "A": "Create a ticket automatically",
            "B": "Report that the ticket was not found",
            "C": "Delete the other tickets",
            "D": "Return the first ticket",
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
        "question": "What does a combined filter do?",
        "options": {
            "A": "Matches tickets that satisfy all supplied filters",
            "B": "Deletes tickets that do not match",
            "C": "Returns only the newest ticket",
            "D": "Ignores the title filter",
        },
        "answer": "A",
    },
    {
        "question": "Why should a failed note save be handled safely?",
        "options": {
            "A": "To silently discard all tickets",
            "B": "To mark every ticket resolved",
            "C": "To skip all future validation",
            "D": "To avoid leaving an unsaved note in memory",
        },
        "answer": "D",
    },
    {
        "question": (
            "The JSON file contains two tickets with the same ID. What "
            "should loading do?"
        ),
        "options": {
            "A": "Keep both",
            "B": "Replace memory with the duplicates",
            "C": "Reject the load without changing current memory",
            "D": "Rename the IDs silently",
        },
        "answer": "C",
    },
    {
        "question": "Why keep quiz scoring separate from displaying questions?",
        "options": {
            "A": "So the score can never be calculated",
            "B": "So invalid answers become correct",
            "C": "So scoring can be tested independently",
            "D": "So the question bank must be duplicated",
        },
        "answer": "C",
    },
]


def score_answers(answers):
    """Return the number of correct answers out of six."""
    if len(answers) != 6:
        raise ValueError("Exactly six answers are required.")

    return sum(
        answer == question["answer"]
        for answer, question in zip(answers, QUESTIONS)
    )
