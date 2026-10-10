import json
from pathlib import Path

class TicketStorage:
    def __init__(self, file_path=None):
        self.file_path = Path(file_path) if file_path is not None else None
        self.tickets = {}

        if self.file_path is not None and self.file_path.exists():
            self._load()

    def _load(self):
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                saved_tickets = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON in {self.file_path}: {error}"
            ) from error

        if not isinstance(saved_tickets, list):
            raise ValueError("JSON storage must contain a list of tickets")

        for ticket in saved_tickets:
            if not isinstance(ticket, dict) or "id" not in ticket:
                raise ValueError("Invalid ticket data in JSON storage")

            ticket_id = ticket["id"]

            if type(ticket_id) is not int or ticket_id <= 0:
                raise ValueError("Ticket ID must be a positive integer")

            if ticket_id in self.tickets:
                raise ValueError(f"Duplicate ticket ID in JSON storage: {ticket_id}")

            self.tickets[ticket_id] = ticket

    def _save(self):
        if self.file_path is None:
            return

        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(self.get_all_tickets(), file, indent=2)
            file.write("\n")

    def add_ticket(self, ticket):
        ticket_id = ticket["id"]

        if ticket_id in self.tickets:
            raise ValueError("Ticket ID already exists")

        self.tickets[ticket_id] = ticket
        self._save()
        return ticket

    def get_ticket(self, ticket_id):
        return self.tickets.get(ticket_id)

    def get_all_tickets(self):
        return list(self.tickets.values())

    
   
    
    def update_status(self, ticket_id, new_status):
        ticket = self.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        allowed_transitions = {
            "open": ("in_progress",),
            "in_progress": ("resolved",),
            "resolved": ("open", "closed"),
            "closed": (),
        }

        if new_status not in allowed_transitions:
            raise ValueError("Invalid ticket status")

        current_status = ticket["status"]

        if current_status == "closed":
            raise ValueError("Closed tickets cannot be changed")

        if new_status not in allowed_transitions[current_status]:
            raise ValueError(
                f"Cannot change ticket status from {current_status} to {new_status}"
            )

        if new_status == "in_progress" and not ticket.get("assigned_to"):
            raise ValueError(
                "Ticket must be assigned to a staff member before work begins"
            )

        ticket["status"] = new_status
        self._save()
        return ticket


    def assign_ticket(self, ticket_id, staff_name):
        ticket = self.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        if not isinstance(staff_name, str) or not staff_name.strip():
            raise ValueError("Staff name must be a non-empty string")

        if ticket["status"] in ("resolved", "closed"):
            raise ValueError(
                "Reopen the ticket before assigning it"
            )

        ticket["assigned_to"] = staff_name.strip()
        self._save()
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