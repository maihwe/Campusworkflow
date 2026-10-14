
def generate_report(tickets):
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be a list")

    by_status = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
        "closed": 0,
    }

    by_priority = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    by_category = {
        "Network": 0,
        "Hardware": 0,
        "Software": 0,
        "Other": 0,
    }

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary")

        status = ticket.get("status")
        priority = ticket.get("priority")
        category = ticket.get("category")

        if status not in by_status:
            raise ValueError("Invalid ticket status")

        if priority not in by_priority:
            raise ValueError("Invalid ticket priority")

        if category not in by_category:
            raise ValueError("Invalid ticket category")

        by_status[status] += 1
        by_priority[priority] += 1
        by_category[category] += 1

    total = len(tickets)
    resolved_count = by_status["resolved"]
    unresolved_count = by_status["open"] + by_status["in_progress"]

    resolution_percentage = (
        resolved_count / total * 100 if total > 0 else 0
    )

    total_affected_users = sum(
        ticket.get("affected_users", 0) for ticket in tickets
    )

    closed_affected_users = sum(
        ticket.get("affected_users", 0)
        for ticket in tickets
        if ticket.get("status") == "closed"
    )

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
        "unresolved_count": unresolved_count,
        "resolved_count": resolved_count,
        "resolution_percentage": resolution_percentage,
        "total_affected_users": total_affected_users,
        "closed_affected_users": closed_affected_users,
    }
