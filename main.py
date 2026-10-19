import re
from pathlib import Path

from campusflow.service import TicketService
from campusflow.storage import TicketStorage
from campusflow.reports import generate_report
from campusflow.search import (
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    VALID_STATUSES,
    search_tickets,
    sort_by_priority_then_id,
    sort_notes_by_id,
)
from campusflow.understanding_check import (
    EXPLANATION_MINIMUM,
    LETTERS,
    question_bank,
    score_answers,
)


DATA_FILE = Path(__file__).parent / "data" / "tickets.json"


def read_integer(prompt, minimum=0):
    while True:
        try:
            value = int(input(prompt))
            if value < minimum:
                print(f"Enter a number greater than or equal to {minimum}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number.")


def read_ticket_id(prompt="Ticket ID: "):
    ticket_id = input(prompt).strip().upper()
    if not re.fullmatch(r"T\d{3,}", ticket_id):
        raise ValueError("Ticket ID must use the format T001")
    return ticket_id


def show_ticket(ticket):
    print("\n--- Ticket Details ---")
    print(f"ID: {ticket['id']}")
    print(f"Title: {ticket['title']}")
    print(f"Category: {ticket['category']}")
    print(f"Urgency: {ticket['urgency']}")
    print(f"Affected users: {ticket['affected_users']}")
    print(f"Priority: {ticket['priority']}")
    print(f"Status: {ticket['status']}")
    print(f"Assigned to: {ticket['assigned_to'] or 'Unassigned'}")


def create_new_ticket(service):
    title = input("Problem title: ").strip()
    category = input("Category: ").strip()
    urgency = input("Urgency (high/medium/low): ").strip().lower()
    affected_users = read_integer("Number of affected users: ", minimum=1)

    tickets = service.get_all()
    ticket_id = "T{:03d}".format(
        max((int(ticket["id"][1:]) for ticket in tickets), default=0) + 1
    )

    ticket = service.create(
        ticket_id, title, category, urgency, affected_users
    )
    print(f"\nTicket {ticket['id']} created successfully.")
    show_ticket(ticket)


def list_tickets(service):
    tickets = service.get_all()

    if not tickets:
        print("\nNo tickets have been created yet.")
        return

    for ticket in tickets:
        print(
            f"{ticket['id']} | {ticket['priority']} | "
            f"{ticket['status']} | {ticket['title']} | "
            f"Assigned to: {ticket['assigned_to'] or 'Nobody'}"
        )


def find_ticket(service):
    ticket_id = read_ticket_id()
    show_ticket(service.get(ticket_id))


def read_search_title():
    """Read search text. Return None when the user cancels."""
    while True:
        title = input("Search title or part of title (0 to cancel): ").strip()

        if title == "0":
            return None

        if title:
            return title

        print("Search title cannot be empty.")


def read_filter_option(prompt, valid_values, label):
    """Read an optional filter; an empty answer means no filter."""
    while True:
        value = input(prompt).strip()

        if not value:
            return None

        for allowed in valid_values:
            if allowed.casefold() == value.casefold():
                return allowed

        print(
            f"Invalid {label} '{value}'. Choose "
            f"{', '.join(valid_values)}, or press Enter to skip."
        )


def print_search_results(tickets, heading):
    """Display search results without changing ticket records."""
    if not tickets:
        print("\nNo tickets matched the supplied search and filters.")
        return

    print(f"\n--- {heading} ({len(tickets)} found) ---")

    for ticket in tickets:
        print(
            f"{ticket['id']} | {ticket['title']} | "
            f"{ticket['category']} | {ticket['priority']} | "
            f"{ticket['status']} | "
            f"Assigned to: {ticket['assigned_to'] or 'Unassigned'}"
        )


def search_tickets_by_title(service, sort_by_priority=False):
    """Search tickets with optional category, status and priority filters."""
    title = read_search_title()

    if title is None:
        print("Search cancelled.")
        return

    category = read_filter_option(
        "Category (Network/Hardware/Software/Other, or Enter to skip): ",
        VALID_CATEGORIES,
        "category",
    )

    status = read_filter_option(
        "Status (open/in_progress/resolved/closed, or Enter to skip): ",
        VALID_STATUSES,
        "status",
    )

    priority = read_filter_option(
        "Priority (critical/high/medium/low, or Enter to skip): ",
        VALID_PRIORITIES,
        "priority",
    )

    tickets = search_tickets(
        service.get_all(),
        title=title,
        category=category,
        status=status,
        priority=priority,
    )

    if sort_by_priority:
        tickets = sort_by_priority_then_id(tickets)
        print_search_results(tickets, "Search Results (priority order)")
        return

    print_search_results(tickets, "Search Results")


def read_required_text(prompt, message):
    """Read text that must not be blank."""
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print(message)


def read_note_message():
    """Read a note message between 5 and 300 characters."""
    while True:
        message = input("Note message (5-300 characters): ").strip()

        if 5 <= len(message) <= 300:
            return message

        print("The note message must be between 5 and 300 characters.")


def add_follow_up_note(service):
    """Add a follow-up note through the TicketService."""
    ticket_id = read_ticket_id()
    ticket = service.get(ticket_id)

    print(f"\nAdding a follow-up note to {ticket_id} ({ticket['status']}).")

    author = read_required_text(
        "Note author: ",
        "The note author cannot be blank.",
    )
    message = read_note_message()

    try:
        note = service.add_note(ticket_id, author, message)
    except ValueError as error:
        print(f"Note was not added: {error}")
        return

    print(
        f"\nNote {note['note_id']} added to "
        f"{ticket_id} by {note['author']}."
    )


def view_ticket_notes(service):
    """Display a ticket's notes in note ID order."""
    ticket_id = read_ticket_id()
    ticket = service.get(ticket_id)
    notes = sort_notes_by_id(service.get_notes(ticket_id))

    if not notes:
        print(f"\nNo follow-up notes recorded for {ticket_id}.")
        return

    print(f"\n--- Notes for {ticket_id}: {ticket['title']} ---")

    for note in notes:
        print(f"{note['note_id']} | {note['author']}: {note['message']}")


def read_answer_letter(question_id):
    """Read a valid answer letter, prompting again for invalid input."""
    while True:
        answer = input(
            f"Your answer for {question_id} (A/B/C/D): "
        ).strip().upper()

        if answer in LETTERS:
            return answer

        print("Invalid choice. Please answer with A, B, C or D.")


def collect_explanations(questions, answers):
    """Collect and save explanations without grading their wording."""
    question_ids = [question["id"] for question in questions]
    question_by_id = {
        question["id"]: question for question in questions
    }
    answer_by_id = dict(zip(question_ids, answers))

    print(
        f"\nExplain at least {EXPLANATION_MINIMUM} of your answers. "
        "The explanations are for mentor discussion and are not auto-graded."
    )

    while True:
        raw = input(
            f"Which {EXPLANATION_MINIMUM} or more question IDs will you "
            "explain? (for example Q1,Q3): "
        )

        chosen = []

        for part in raw.replace(",", " ").split():
            question_id = part.strip().upper()

            if question_id in question_ids and question_id not in chosen:
                chosen.append(question_id)

        if len(chosen) >= EXPLANATION_MINIMUM:
            break

        print(
            f"Please choose at least {EXPLANATION_MINIMUM} valid question IDs "
            f"from: {', '.join(question_ids)}"
        )

    explanations = []

    for question_id in chosen:
        while True:
            explanation = input(
                f"Explain your answer to {question_id}: "
            ).strip()

            if explanation:
                break

            print("A short explanation is required for this check.")

        question = question_by_id[question_id]
        explanations.append(
            f"Question: {question_id}\n"
            f"Scenario: {question['scenario']}\n"
            f"Answer selected: {answer_by_id[question_id]}\n"
            f"Explanation: {explanation}\n"
            f"{'-' * 40}\n"
        )

    explanation_file = (
        Path(__file__).parent / "data" / "quiz_explanations.txt"
    )
    explanation_file.parent.mkdir(parents=True, exist_ok=True)

    with explanation_file.open("a", encoding="utf-8") as file:
        file.write("\n".join(explanations) + "\n")

    print(f"\nExplanations saved to {explanation_file}.")
    print("Explanations are saved for review and are not auto-graded.")


def run_understanding_check():
    """Run the Engineering Understanding Check."""
    questions = question_bank()

    print("\n--- Engineering Understanding Check ---")
    print("Answer each scenario with A, B, C or D.")

    answers = []

    for question in questions:
        print(f"\n{question['id']}. {question['scenario']}")

        for letter, option_text in question["options"].items():
            print(f"   {letter}. {option_text}")

        answers.append(read_answer_letter(question["id"]))

    result = score_answers(answers)

    print("\n--- Understanding Check Result ---")

    for item in result["results"]:
        if item["correct"]:
            print(f"{item['id']}: correct")
        else:
            print(
                f"{item['id']}: incorrect "
                f"(submitted {item['answer'] or 'no answer'}, "
                f"correct answer {item['correct_answer']})"
            )

    print(f"Score: {result['score']}/{result['total']}")

    collect_explanations(questions, answers)


def assign_ticket(service):
    ticket_id = read_ticket_id()
    staff_name = input("Staff member's name: ").strip()
    show_ticket(service.assign(ticket_id, staff_name))


def change_status(service, action):
    ticket_id = read_ticket_id()

    actions = {
        "start": service.start,
        "resolve": service.resolve,
        "reopen": service.reopen,
        "close": service.close,
    }

    show_ticket(actions[action](ticket_id))


def list_unresolved(service):
    """Display open tickets, sorted by priority and numeric ID."""
    tickets = [
        ticket for ticket in service.get_all()
        if ticket["status"] == "open"
    ]

    tickets.sort(
        key=lambda ticket: (
            {
                "critical": 0,
                "high": 1,
                "medium": 2,
                "low": 3,
            }[ticket["priority"]],
            int(ticket["id"][1:]),
        )
    )

    if not tickets:
        print("\nThere are no open tickets.")
        return

    print("\n--- Open Work Queue (highest priority first) ---")

    for ticket in tickets:
        print(
            f"{ticket['id']} | {ticket['priority']} | "
            f"{ticket['status']} | {ticket['title']}"
        )


def show_report(service):
    report = generate_report(service.get_all())

    print("\n--- CampusFlow Report ---")
    print(f"Total tickets: {report['total']}")

    print("\nBy status:")
    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")

    print("\nBy priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")

    print("\nBy category:")
    for category, count in report["by_category"].items():
        print(f"  {category}: {count}")

    print(
        f"\nUnresolved tickets (open + in_progress): "
        f"{report['unresolved_count']}"
    )
    print(f"Resolved tickets: {report['resolved_count']}")
    print(
        f"Resolution percentage: "
        f"{report['resolution_percentage']:.1f}%"
    )

    print(f"\nTotal affected users: {report['total_affected_users']}")
    print(
        f"Affected users on closed tickets: "
        f"{report['closed_affected_users']}"
    )



def confirm_exit():
    while True:
        answer = input(
            "Are you sure you want to end the program? y/n: "
        ).strip().lower()

        if answer == "y":
            print("Thank you for using CampusFlow.")
            return True

        if answer == "n":
            print("Exit cancelled. Returning to the application...")
            return False

        print("Invalid response. Please enter y or n.")


def main():
    storage = TicketStorage(DATA_FILE)
    service = TicketService(storage)

    actions = {
        "1": ("Create ticket", lambda: create_new_ticket(service)),
        "2": ("List all tickets", lambda: list_tickets(service)),
        "3": ("View ticket details", lambda: find_ticket(service)),
        "4": ("Assign ticket", lambda: assign_ticket(service)),
        "5": ("Start ticket work", lambda: change_status(service, "start")),
        "6": ("Resolve ticket", lambda: change_status(service, "resolve")),
        "7": ("Reopen ticket", lambda: change_status(service, "reopen")),
        "8": ("Close ticket", lambda: change_status(service, "close")),
        "9": ("View open work queue", lambda: list_unresolved(service)),
        "10": ("Generate report", lambda: show_report(service)),
        "11": (
            "Search tickets by title",
            lambda: search_tickets_by_title(service),
        ),
        "12": (
            "Search tickets sorted by priority",
            lambda: search_tickets_by_title(service, sort_by_priority=True),
        ),
        "13": ("Add follow-up note", lambda: add_follow_up_note(service)),
        "14": ("View ticket notes", lambda: view_ticket_notes(service)),
        "15": (
            "Engineering Understanding Check",
            run_understanding_check,
        ),
    }

    while True:
        print("\n========== CampusFlow ==========")

        for number, (label, _) in actions.items():
            print(f"{number}. {label}")

        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            if confirm_exit():
                break
            continue

        if choice not in actions:
            print("Invalid option. Please choose from the menu.")
            continue

        try:
            actions[choice][1]()
        except (ValueError, KeyError) as error:
            print(f"Operation failed: {error}")
        except OSError as error:
            print(f"File operation failed: {error}")


if __name__ == "__main__":
    main()