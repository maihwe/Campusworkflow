
QUESTIONS = [
    {
        "question": (
            "Ticket T001 is open and unassigned. A user tries to move it "
            "to in_progress. What should happen?"
        ),
        "options": {
            "A": "Accept the change",
            "B": "Reject it and preserve all data",
            "C": "Resolve it automatically",
            "D": "Remove the ticket",
        },
        "answer": "B",
    },
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
        "question": "Why save ticket notes to JSON storage?",
        "options": {
            "A": "To make notes disappear after exit",
            "B": "To change every ticket's priority",
            "C": "To preserve notes when the application restarts",
            "D": "To prevent users from viewing notes",
        },
        "answer": "C",
    },
    {
        "question": (
            "Search with title='wifi', category='Network' and status='open'. "
            "Which records should match?"
        ),
        "options": {
            "A": "Any record matching one filter",
            "B": "Only records matching all supplied filters",
            "C": "All Network records",
            "D": "All open records",
        },
        "answer": "B",
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
        "question": "A resolved ticket receives 'Add note'. What should happen?",
        "options": {
            "A": "Append the note anyway",
            "B": "Delete the old notes",
            "C": "Reject until the ticket is reopened",
            "D": "Change the status silently",
        },
        "answer": "C",
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
        "question": "What should the program do when a menu choice is invalid?",
        "options": {
            "A": "Exit immediately every time",
            "B": "Explain the choice is invalid and ask again",
            "C": "Run a random menu action",
            "D": "Clear the ticket storage",
        },
        "answer": "B",
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
    """Return the number of correct answers out of twelve."""
    if len(answers) != len(QUESTIONS):
        raise ValueError("Exactly twelve answers are required.")

    return sum(
        answer == question["answer"]
        for answer, question in zip(answers, QUESTIONS)
    )
