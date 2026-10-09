
def generate_report(tickets):
    by_status = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
    }

    by_priority = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary")

        status = ticket.get("status")
        priority = ticket.get("priority")

        if status not in by_status:
            raise ValueError("Invalid ticket status")

        if priority not in by_priority:
            raise ValueError("Invalid ticket priority")

        by_status[status] += 1
        by_priority[priority] += 1

    return {
        "total": len(tickets),
        "by_status": by_status,
        "by_priority": by_priority,
    }

