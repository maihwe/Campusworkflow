
class TicketStorage:
    def __init__(self):
        self.tickets = {}

    def add_ticket(self, ticket):
        ticket_id = ticket["id"]

        if ticket_id in self.tickets:
            raise ValueError("Ticket ID already exists")

        self.tickets[ticket_id] = ticket
        return ticket

    def get_ticket(self, ticket_id):
        return self.tickets.get(ticket_id)

    def get_all_tickets(self):
        return list(self.tickets.values())

    
   
    def update_status(self, ticket_id, new_status):
        ticket = self.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        allowed_statuses = ("open", "in_progress", "closed")

        if new_status not in allowed_statuses:
            raise ValueError("Invalid ticket status")

        current_status = ticket["status"]

        if current_status == "open" and new_status == "closed":
            raise ValueError(
                "Ticket must be in progress before it can be closed"
            )

        ticket["status"] = new_status
        return ticket

    def assign_ticket(self, ticket_id, staff_name):
        ticket = self.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        if not isinstance(staff_name, str) or not staff_name.strip():
            raise ValueError("Staff name must be a non-empty string")

        ticket["assigned_to"] = staff_name.strip()
        return ticket


    def filter_tickets(self, status=None, priority=None, category=None, assigned_to=None):
        results = self.get_all_tickets()

        if status is not None:
            results = [
                ticket for ticket in results
                if ticket["status"] == status
            ]

        if priority is not None:
            results = [
                ticket for ticket in results
                if ticket["priority"] == priority
            ]

        if category is not None:
            results = [
                ticket for ticket in results
                if ticket["category"] == category
            ]

        if assigned_to is not None:
            results = [
                ticket for ticket in results
                if ticket["assigned_to"] == assigned_to
            ]

        return results