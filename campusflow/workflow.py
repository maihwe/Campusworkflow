
def assign_ticket(ticket, assignee):
    if not isinstance(ticket, dict):
        raise ValueError("Ticket must be a dictionary")

    required_fields = ["status", "assigned_to"]
    for field in required_fields:
        if field not in ticket:
            raise ValueError(f"Ticket is missing required field: {field}")

    if ticket["status"] not in ["open", "in_progress", "resolved"]:
        raise ValueError("Invalid ticket status")

    if ticket["status"] == "resolved":
        raise ValueError("Reopen the ticket before modifying it")

    if not isinstance(assignee, str) or not assignee.strip():
        raise ValueError("Assignee name is required")

    ticket["assigned_to"] = assignee.strip()
    return ticket


def start_ticket(ticket):
    if not isinstance(ticket, dict):
        raise ValueError("Ticket must be a dictionary")

    if "status" not in ticket or "assigned_to" not in ticket:
        raise ValueError("Ticket is missing required fields")

    if ticket["status"] != "open":
        raise ValueError("Only open tickets can be started")

    if not ticket["assigned_to"]:
        raise ValueError("Assign the ticket before starting it")

    ticket["status"] = "in_progress"
    return ticket


def resolve_ticket(ticket):
    if not isinstance(ticket, dict):
        raise ValueError("Ticket must be a dictionary")

    if "status" not in ticket:
        raise ValueError("Ticket is missing required fields")

    if ticket["status"] != "in_progress":
        raise ValueError("Only in-progress tickets can be resolved")

    ticket["status"] = "resolved"
    return ticket


def reopen_ticket(ticket):
    if not isinstance(ticket, dict):
        raise ValueError("Ticket must be a dictionary")

    if "status" not in ticket:
        raise ValueError("Ticket is missing required fields")

    if ticket["status"] != "resolved":
        raise ValueError("Only resolved tickets can be reopened")

    ticket["status"] = "open"
    return ticket


def get_unresolved_tickets(tickets):
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be a list")

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary")

        if "status" not in ticket or "priority" not in ticket or "id" not in ticket:
            raise ValueError("Ticket is missing required fields")

        if ticket["status"] not in ["open", "in_progress", "resolved"]:
            raise ValueError("Invalid ticket status")

        if ticket["priority"] not in priority_order:
            raise ValueError("Invalid ticket priority")

        if not isinstance(ticket["id"], int) or isinstance(ticket["id"], bool) or ticket["id"] <= 0:
            raise ValueError("Ticket ID must be a positive integer")

    unresolved = [
        ticket for ticket in tickets
        if ticket["status"] != "resolved"
    ]

    return sorted(
        unresolved,
        key=lambda ticket: (
            priority_order[ticket["priority"]],
            ticket["id"],
        ),
    )

