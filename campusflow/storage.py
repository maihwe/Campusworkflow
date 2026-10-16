import json
import os
import re
from pathlib import Path

from campusflow.tickets import VALID_CATEGORIES, calculate_priority


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

        required_fields = {
            "id",
            "title",
            "category",
            "urgency",
            "affected_users",
            "priority",
            "status",
            "assigned_to",
        }
        valid_statuses = ("open", "in_progress", "resolved", "closed")
        loaded_tickets = {}

        for ticket in saved_tickets:
            if (
                not isinstance(ticket, dict)
                or not required_fields.issubset(ticket)
            ):
                raise ValueError("Invalid ticket data in JSON storage")

            if ticket["status"] not in valid_statuses:
                raise ValueError("Invalid ticket data in JSON storage")

            ticket_id = ticket["id"]

            if (
                not isinstance(ticket_id, str)
                or not re.fullmatch(r"T\d{3,}", ticket_id)
            ):
                raise ValueError("Ticket ID must use the format T001")

            if ticket_id in loaded_tickets:
                raise ValueError(
                    f"Duplicate ticket ID in JSON storage: {ticket_id}"
                )

            if (
                not isinstance(ticket["title"], str)
                or not ticket["title"].strip()
                or ticket["category"] not in VALID_CATEGORIES
                or ticket["urgency"] not in ("low", "medium", "high")
                or type(ticket["affected_users"]) is not int
                or ticket["affected_users"] <= 0
                or (
                    ticket["assigned_to"] is not None
                    and (
                        not isinstance(ticket["assigned_to"], str)
                        or not ticket["assigned_to"].strip()
                    )
                )
            ):
                raise ValueError("Invalid ticket data in JSON storage")

            expected_priority = calculate_priority(
                ticket["urgency"],
                ticket["affected_users"],
            )

            if ticket["priority"] != expected_priority:
                raise ValueError("Invalid ticket data in JSON storage")

            ticket.setdefault("notes", [])

            if not isinstance(ticket["notes"], list):
                raise ValueError("Ticket notes must be a list")

            seen_note_ids = set()

            for note in ticket["notes"]:
                if (
                    not isinstance(note, dict)
                    or set(note) != {"note_id", "author", "message"}
                    or not isinstance(note["note_id"], str)
                    or not re.fullmatch(r"N\d{3,}", note["note_id"])
                    or not isinstance(note["author"], str)
                    or not note["author"].strip()
                    or not isinstance(note["message"], str)
                    or not 5 <= len(note["message"].strip()) <= 300
                    or note["note_id"] in seen_note_ids
                ):
                    raise ValueError("Invalid ticket note in JSON storage")

                seen_note_ids.add(note["note_id"])

            loaded_tickets[ticket_id] = ticket

        # Replace the current collection only after every ticket is validated.
        self.tickets = loaded_tickets

    def _save(self):
        if self.file_path is None:
            return

        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        temporary_path = self.file_path.with_name(
            f".{self.file_path.name}.tmp"
        )

        try:
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(self.get_all_tickets(), file, indent=2)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())

            os.replace(temporary_path, self.file_path)

        finally:
            if temporary_path.exists():
                temporary_path.unlink()

    def add_ticket(self, ticket):
        ticket_id = ticket["id"]

        if ticket_id in self.tickets:
            raise ValueError("Ticket ID already exists")

        ticket.setdefault("notes", [])

        if not isinstance(ticket["notes"], list):
            raise ValueError("Ticket notes must be a list")

        self.tickets[ticket_id] = ticket

        try:
            self._save()
        except Exception:
            del self.tickets[ticket_id]
            raise

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

        try:
            self._save()
        except Exception:
            ticket["status"] = current_status
            raise

        return ticket

    def assign_ticket(self, ticket_id, staff_name):
        ticket = self.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        if not isinstance(staff_name, str) or not staff_name.strip():
            raise ValueError("Staff name must be a non-empty string")

        if ticket["status"] in ("resolved", "closed"):
            raise ValueError("Reopen the ticket before assigning it")

        previous_assignee = ticket["assigned_to"]
        ticket["assigned_to"] = staff_name.strip()

        try:
            self._save()
        except Exception:
            ticket["assigned_to"] = previous_assignee
            raise

        return ticket

    def add_note(self, ticket_id, author, message):
        ticket = self.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        if ticket["status"] not in ("open", "in_progress"):
            raise ValueError(
                "Notes can only be added to open or in-progress tickets"
            )

        if not isinstance(author, str) or not author.strip():
            raise ValueError("Author must be a non-empty string")

        if not isinstance(message, str):
            raise ValueError("Note message must be a string")

        author = author.strip()
        message = message.strip()

        if not 5 <= len(message) <= 300:
            raise ValueError(
                "Note message must contain between 5 and 300 characters"
            )

        notes = ticket.setdefault("notes", [])
        existing_numbers = []

        for note in notes:
            if not isinstance(note, dict):
                raise ValueError("Invalid existing ticket note")

            note_id = note.get("note_id", "")

            if not isinstance(note_id, str):
                raise ValueError("Invalid existing note ID")

            match = re.fullmatch(r"N(\d{3,})", note_id)

            if match is None:
                raise ValueError("Invalid existing note ID")

            existing_numbers.append(int(match.group(1)))

        next_number = max(existing_numbers, default=0) + 1

        new_note = {
            "note_id": f"N{next_number:03d}",
            "author": author,
            "message": message,
        }

        notes.append(new_note)

        try:
            self._save()
        except Exception:
            notes.pop()
            raise

        return list(notes)

    def get_notes(self, ticket_id):
        ticket = self.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        return list(ticket.get("notes", []))

    def filter_tickets(
        self,
        status=None,
        priority=None,
        category=None,
        assigned_to=None,
        title=None,
    ):
        results = self.get_all_tickets()

        if title is not None:
            search_text = title.casefold()
            results = [
                ticket for ticket in results
                if search_text in ticket["title"].casefold()
            ]

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