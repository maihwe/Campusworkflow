"""Read-only search, filtering and result ordering for CampusFlow.

Engineer B owns this module. Every function takes the ticket collection as
an argument and returns a new list, so a search can never modify the stored
tickets. Nothing here reads input or prints output, which keeps the search
rules independently testable from the CLI menu in ``main.py``.
"""

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
    """Return the numeric part of an ID such as ``T010`` or ``N002``.

    Ticket and note IDs are ordered by this number so that a text ID such as
    ``T10`` never sorts before ``T2``. Raises ValueError when the ID does not
    use the expected prefix-plus-digits shape.
    """
    if (
        not isinstance(identifier, str)
        or not re.fullmatch(r"[A-Za-z]\d{3,}", identifier)
    ):
        raise ValueError("Identifier must use the format T001 or N001")

    return int(identifier[1:])


def normalize_title_filter(title):
    """Turn a title filter into search text, or None when it is not supplied.

    A missing or blank title means "do not filter by title". Matching is
    case-insensitive, so the caller's text is casefolded here once.
    """
    if title is None:
        return None

    if not isinstance(title, str):
        raise ValueError("Title filter must be text")

    text = title.strip()

    if not text:
        return None

    return text.casefold()


def normalize_choice_filter(value, valid_values, label):
    """Turn an optional filter value into the canonical stored value.

    None and blank text mean "do not filter by this field". The comparison is
    case-insensitive but the returned value is always one of the canonical
    values, so ``network`` becomes the stored ``Network``.
    """
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

    raise ValueError(
        f"{label} must be one of: {', '.join(valid_values)}"
    )


def title_matches(ticket, search_text):
    """Return True when the search text appears inside the ticket title."""
    title = ticket.get("title")

    return isinstance(title, str) and search_text in title.casefold()


def search_tickets(
    tickets,
    title=None,
    category=None,
    status=None,
    priority=None,
):
    """Return the tickets that match every supplied filter.

    Filters are combined with logical AND: a ticket is returned only when it
    matches all of the filters that were supplied. Unsupplied (None or blank)
    filters are ignored. The input list and the tickets inside it are never
    modified. Invalid filter values raise ValueError before any matching work
    is done.
    """
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

        if (
            category_filter is not None
            and ticket.get("category") != category_filter
        ):
            continue

        if (
            status_filter is not None
            and ticket.get("status") != status_filter
        ):
            continue

        if (
            priority_filter is not None
            and ticket.get("priority") != priority_filter
        ):
            continue

        results.append(ticket)

    return results


def sort_by_priority_then_id(tickets):
    """Return a new list ordered by priority, then by numeric ticket ID.

    Priority order is critical > high > medium > low. Tickets that share a
    priority are ordered by the numeric part of their ID, so ``T002`` comes
    before ``T010``. This is the optional view for search results; it does not
    replace the original Open Work Queue.
    """
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


def sort_notes_by_id(notes):
    """Return a new list of notes ordered by note ID, such as N001, N002."""
    if not isinstance(notes, list):
        raise ValueError("Notes must be a list")

    for note in notes:
        if not isinstance(note, dict) or "note_id" not in note:
            raise ValueError("Each note must be a dictionary with a note_id")

    return sorted(notes, key=lambda note: numeric_part(note["note_id"]))
