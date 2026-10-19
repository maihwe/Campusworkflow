
import json
import os
import re
from pathlib import Path

from campusflow.search import filter_tickets
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

        validated_tickets = {}

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

        for saved_ticket in saved_tickets:
            if not isinstance(saved_ticket, dict):
                raise ValueError("Invalid ticket data in JSON storage")

            ticket = dict(saved_ticket)
            ticket.setdefault("notes", [])

            if not required_fields.issubset(ticket):
                raise ValueError("Invalid ticket data in JSON storage")

            ticket_id = ticket["id"]

            if (
                not isinstance(ticket_id, str)
                or not re.fullmatch(r"T\d{3,}", ticket_id)
            ):
                raise ValueError("Ticket ID must use the format T001")

            if ticket_id in validated_tickets:
                raise ValueError(
                    f"Duplicate ticket ID in JSON storage: {ticket_id}"
                )

            if (
                not isinstance(ticket["title"], str)
                or not ticket["title"].strip()
            ):
                raise ValueError("Invalid ticket data in JSON storage")

            if ticket["category"] not in VALID_CATEGORIES:
                raise ValueError("Invalid ticket data in JSON storage")

            if ticket["urgency"] not in ("low", "medium", "high"):
                raise ValueError("Invalid ticket data in JSON storage")

            if (
                type(ticket["affected_users"]) is not int
                or ticket["affected_users"] <= 0
            ):
                raise ValueError("Invalid ticket data in JSON storage")

            expected_priority = calculate_priority(
                ticket["urgency"],
                ticket["affected_users"],
            )

            if ticket["priority"] != expected_priority:
                raise ValueError("Invalid ticket data in JSON storage")

            if ticket["status"] not in valid_statuses:
                raise ValueError("Invalid ticket data in JSON storage")

            assigned_to = ticket["assigned_to"]
            if assigned_to is not None and (
                not isinstance(assigned_to, str)
                or not assigned_to.strip()
            ):
                raise ValueError("Invalid ticket data in JSON storage")

            notes = ticket["notes"]
            if not isinstance(notes, list):
                raise ValueError("Ticket notes must be a list")

            seen_note_ids = set()

            for note in notes:
                if (
                    not isinstance(note, dict)
                    or set(note) != {"note_id", "author", "message"}
                ):
                    raise ValueError("Invalid note data in JSON storage")

                note_id = note["note_id"]
                author = note["author"]
                message = note["message"]

                if (
                    not isinstance(note_id, str)
                    or not re.fullmatch(r"N\d{3,}", note_id)
                ):
                    raise ValueError("Invalid note data in JSON storage")

                if note_id in seen_note_ids:
                    raise ValueError(
                        f"Duplicate note ID in JSON storage: {note_id}"
                    )
                if (
                    not isinstance(author, str)
                    or not author.strip()
                    or not isinstance(message, str)
                    or not 5 <= len(message.strip()) <= 300
                ):
                    raise ValueError("Invalid note data in JSON storage")

                seen_note_ids.add(note_id)

            validated_tickets[ticket_id] = ticket

        # Replace current memory only after the whole file is valid.
        self.tickets = validated_tickets

    def _save(self):
        if self.file_path is None:
            return

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.file_path.with_suffix(
            self.file_path.suffix + ".tmp"
        )

        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(
                    list(self.tickets.values()),
                    file,
                    indent=2,
                )

            os.replace(temp_path, self.file_path)

        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

    def add_ticket(self, ticket):
        ticket_id = ticket["id"]

        if ticket_id in self.tickets:
            raise ValueError(f"Ticket {ticket_id} already exists")

        ticket.setdefault("notes", [])

        if not isinstance(ticket["notes"], list):
            raise ValueError("Ticket notes must be a list")

        self.tickets[ticket_id] = ticket

        try:
            self._save()
        except Exception:
            self.tickets.pop(ticket_id, None)
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
            raise ValueError("Invalid status")

        current_status = ticket["status"]

        if new_status not in allowed_transitions[current_status]:
            raise ValueError(
                f"Cannot change status from "
                f"{current_status} to {new_status}"
            )

        if (
            new_status == "in_progress"
            and ticket["assigned_to"] is None
        ):
            raise ValueError(
                "Ticket must be assigned before moving to in_progress"
            )

        old_status = ticket["status"]
        ticket["status"] = new_status

        try:
            self._save()
        except Exception:
            ticket["status"] = old_status
            raise

        return ticket

    def assign_ticket(self, ticket_id, staff_name):
        ticket = self.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        if ticket["status"] in ("resolved", "closed"):
            raise ValueError("Reopen the ticket before assigning it")

        if not isinstance(staff_name, str) or not staff_name.strip():
            raise ValueError("Staff name must be a non-empty string")

        old_assigned_to = ticket["assigned_to"]
        ticket["assigned_to"] = staff_name.strip()

        try:
            self._save()
        except Exception:
            ticket["assigned_to"] = old_assigned_to
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

        for existing_ticket in self.tickets.values():
            for existing_note in existing_ticket.get("notes", []):
                if (
                    not isinstance(existing_note, dict)
                    or set(existing_note) != {"note_id", "author", "message"}
                ):
                    raise ValueError("Invalid existing ticket note")

                note_id = existing_note["note_id"]
                note_author = existing_note["author"]
                note_message = existing_note["message"]

                if (
                    not isinstance(note_id, str)
                    or not re.fullmatch(r"N\d{3,}", note_id)
                    or not isinstance(note_author, str)
                    or not note_author.strip()
                    or not isinstance(note_message, str)
                    or not 5 <= len(note_message.strip()) <= 300
                ):
                    raise ValueError("Invalid existing ticket note")

                existing_numbers.append(int(note_id[1:]))

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

        return new_note

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
        return filter_tickets(
            self.get_all_tickets(),
            title=title,
            category=category,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
        )
