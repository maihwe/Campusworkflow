
from campusflow.tickets import create_ticket
from campusflow.storage import TicketStorage


class TicketService:
    def __init__(self, storage=None):
        if storage is None:
            storage = TicketStorage()

        self.storage = storage

    def create(self, ticket_id, title, category, urgency, affected_users):
        ticket = create_ticket(
            ticket_id,
            title,
            category,
            urgency,
            affected_users,
        )

        return self.storage.add_ticket(ticket)

    def get(self, ticket_id):
        ticket = self.storage.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        return ticket

    def assign(self, ticket_id, staff_name):
        return self.storage.assign_ticket(ticket_id, staff_name)

    def update_status(self, ticket_id, new_status):
        return self.storage.update_status(ticket_id, new_status)

    def filter(self, status=None, priority=None, category=None, assigned_to=None):
        return self.storage.filter_tickets(
            status=status,
            priority=priority,
            category=category,
            assigned_to=assigned_to,
        )

    def get_all(self):
        return self.storage.get_all_tickets()