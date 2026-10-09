
def calculate_priority(urgency, affected_users):
    if urgency not in ("high", "medium", "low"):
        raise ValueError("Invalid urgency")

    if type(affected_users) is not int or affected_users < 0:
        raise ValueError("affected_users must be a non-negative integer")
    if urgency == "high" and affected_users >= 10:
        return "critical"
    elif urgency == "high" or affected_users >= 10:
        return "high"
    elif urgency == "medium" or affected_users >= 3:
        return "medium"
    else:
        return "low"
    
def create_ticket(ticket_id, title, category, urgency, affected_users):
    if type(ticket_id) is not int or ticket_id <= 0:
        raise ValueError("ticket_id must be a positive integer")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must be a non-empty string")

    if not isinstance(category, str) or not category.strip():
        raise ValueError("category must be a non-empty string")
        
    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
    }

    return ticket