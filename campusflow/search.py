"""Read-only search, filtering and sorting helpers for CampusFlow."""

import re

from campusflow.tickets import VALID_CATEGORIES

VALID_STATUSES = ("open", "in_progress", "resolved", "closed")
VALID_PRIORITIES = ("critical", "high", "medium", "low")

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def numeric_part(identifier):
    """Return the numeric part of a ticket or note ID."""
    if (
        not isinstance(identifier, str)
        or not re.fullmatch(r"[A-Za-z]\d{3,}", identifier)
    ):
        raise ValueError("Identifier must use the format T001 or N001")

    return int(identifier[1:])


def normalize_title_filter(title):
    """Normalize an optional title search."""
    if title is None:
        return None
    if not isinstance(title, str):
        raise ValueError("Title filter must be text")

    text = title.strip()
    return text.casefold() if text else None


def normalize_choice_filter(value, valid_values, label):
    """Validate an optional choice and return its canonical value."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} filter must be text")

    text = value.strip()
    if not text:
        return None

    for allowed in valid_values:
        if allowed.casefold() == text.casefold():
            return allowed

    raise ValueError(f"{label} must be one of: {', '.join(valid_values)}")


def title_matches(ticket, search_text):
    """Check whether a title contains the normalized search text."""
    title = ticket.get("title")
    return isinstance(title, str) and search_text in title.casefold()


def search_tickets(
    tickets,
    title=None,
    category=None,
    status=None,
    priority=None,
):
    """Return tickets matching every supplied search filter."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be a list")

    search_text = normalize_title_filter(title)
    category_filter = normalize_choice_filter(
        category, VALID_CATEGORIES, "Category"
    )
    status_filter = normalize_choice_filter(
        status, VALID_STATUSES, "Status"
    )
    priority_filter = normalize_choice_filter(
        priority, VALID_PRIORITIES, "Priority"
    )

    results = []

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary")

        if search_text is not None and not title_matches(ticket, search_text):
            continue
        if category_filter is not None and ticket.get("category") != category_filter:
            continue
        if status_filter is not None and ticket.get("status") != status_filter:
            continue
        if priority_filter is not None and ticket.get("priority") != priority_filter:
            continue

        results.append(ticket)

    return results


def filter_tickets(
    tickets,
    title=None,
    category=None,
    status=None,
    priority=None,
    assigned_to=None,
):
    """Filter tickets while preserving the existing assigned_to interface."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be a list")

    results = search_tickets(
        tickets,
        title=title,
        category=category,
        status=status,
        priority=priority,
    )

    if assigned_to is not None:
        results = [
            ticket for ticket in results
            if ticket.get("assigned_to") == assigned_to
        ]

    return results


def sort_by_priority_then_id(tickets):
    """Sort tickets by priority, then by numeric ticket ID."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be a list")

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary")
        if ticket.get("priority") not in PRIORITY_ORDER:
            raise ValueError("Invalid ticket priority")

    return sorted(
        tickets,
        key=lambda ticket: (
            PRIORITY_ORDER[ticket["priority"]],
            numeric_part(ticket["id"]),
        ),
    )


def sort_by_priority(tickets):
    """Keep the original sorting function name for compatibility."""
    return sort_by_priority_then_id(tickets)


def sort_notes_by_id(notes):
    """Return notes ordered by their numeric note IDs."""
    if not isinstance(notes, list):
        raise ValueError("Notes must be a list")

    for note in notes:
        if not isinstance(note, dict) or "note_id" not in note:
            raise ValueError("Each note must be a dictionary with a note_id")

    return sorted(notes, key=lambda note: numeric_part(note["note_id"]))
