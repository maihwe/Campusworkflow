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

        # Validate the entire file before changing current memory.
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
            "notes",
        }

        for saved_ticket in saved_tickets:
            if not isinstance(saved_ticket, dict):
                raise ValueError("Invalid ticket data in JSON storage")

            # Copy the record so validation does not mutate the
            # original dictionary loaded from the JSON list.
            ticket = dict(saved_ticket)

            # Older tickets may not have notes yet.
            ticket.setdefault("notes", [])

            if not required_fields.issubset(ticket):
                raise ValueError("Invalid ticket data in JSON storage")

            # Read the ID before using it in validation.
            ticket_id = ticket["id"]

            # Validate ticket ID.
            if (
                not isinstance(ticket_id, str)
                or not re.fullmatch(r"T\d{3,}", ticket_id)
            ):
                raise ValueError("Ticket ID must use the format T001")

            # Reject duplicate ticket IDs.
            if ticket_id in validated_tickets:
                raise ValueError(
                    f"Duplicate ticket ID in JSON storage: {ticket_id}"
                )

            # Validate title.
            if (
                not isinstance(ticket["title"], str)
                or not ticket["title"].strip()
            ):
                raise ValueError("Invalid ticket data in JSON storage")

            # Validate category.
            if ticket["category"] not in VALID_CATEGORIES:
                raise ValueError("Invalid ticket data in JSON storage")

            # Validate urgency.
            if ticket["urgency"] not in ("low", "medium", "high"):
                raise ValueError("Invalid ticket data in JSON storage")

            # Validate affected users.
            # type(...) is int rejects True and False.
            if (
                type(ticket["affected_users"]) is not int
                or ticket["affected_users"] <= 0
            ):
                raise ValueError("Invalid ticket data in JSON storage")

            # Validate that priority matches the application's rule.
            expected_priority = calculate_priority(
                ticket["urgency"],
                ticket["affected_users"],
            )

            if ticket["priority"] != expected_priority:
                raise ValueError("Invalid ticket data in JSON storage")

            # Validate status.
            if ticket["status"] not in (
                "open",
                "in_progress",
                "resolved",
                "closed",
            ):
                raise ValueError("Invalid ticket data in JSON storage")

            # Validate assignment.
            if ticket["assigned_to"] is not None:
                if (
                    not isinstance(ticket["assigned_to"], str)
                    or not ticket["assigned_to"].strip()
                ):
                    raise ValueError(
                        "Invalid ticket data in JSON storage"
                    )

            # Validate notes.
            notes = ticket["notes"]

            if not isinstance(notes, list):
                raise ValueError("Invalid ticket data in JSON storage")

            seen_note_ids = set()

            for note in notes:
                if not isinstance(note, dict):
                    raise ValueError("Invalid note data in JSON storage")

                if set(note) != {"note_id", "author", "message"}:
                    raise ValueError("Invalid note data in JSON storage")

                note_id = note["note_id"]

                if (
                    not isinstance(note_id, str)
                    or not re.fullmatch(r"N\d{3,}", note_id)
                ):
                    raise ValueError("Invalid note data in JSON storage")

                if note_id in seen_note_ids:
                    raise ValueError(
                        f"Duplicate note ID in ticket "
                        f"{ticket_id}: {note_id}"
                    )

                seen_note_ids.add(note_id)

                if (
                    not isinstance(note["author"], str)
                    or not note["author"].strip()
                ):
                    raise ValueError("Invalid note data in JSON storage")

                if not isinstance(note["message"], str):
                    raise ValueError("Invalid note data in JSON storage")

                message = note["message"].strip()

                if len(message) < 5 or len(message) > 300:
                    raise ValueError("Invalid note data in JSON storage")

            validated_tickets[ticket_id] = ticket

        # Replace current memory only after every ticket is valid.
        self.tickets = validated_tickets

    def _save(self):
        if self.file_path is None:
            return

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

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
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())

            os.replace(temp_path, self.file_path)

        except Exception:
            if temp_path.exists():
                temp_path.unlink()

            raise

    def add_ticket(self, ticket):
        ticket_id = ticket["id"]

        # New tickets must have a notes list.
        ticket.setdefault("notes", [])
        if not isinstance(ticket["notes"], list):
            raise ValueError("Ticket notes must be a list")

        if ticket_id in self.tickets:
            raise ValueError(
                f"Ticket {ticket_id} already exists"
            )

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

        if new_status not in (
            "open",
            "in_progress",
            "resolved",
            "closed",
        ):
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
                "Ticket must be assigned before "
                "moving to in_progress"
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
            raise ValueError(
                "Reopen the ticket before assigning it"
            )

        if (
            not isinstance(staff_name, str)
            or not staff_name.strip()
        ):
            raise ValueError(
                "Staff name must be a non-empty string"
            )

        old_assigned_to = ticket["assigned_to"]
        ticket["assigned_to"] = staff_name.strip()

        try:
            self._save()
        except Exception:
            ticket["assigned_to"] = old_assigned_to
            raise

        return ticket

    def filter_tickets(
        self,
        status=None,
        priority=None,
        category=None,
        assigned_to=None,
        title=None,
    ):
        tickets = self.get_all_tickets()

        if title is not None:
            search_text = title.casefold()
            tickets = [
                ticket
                for ticket in tickets
                if search_text in ticket["title"].casefold()
            ]

        if status is not None:
            tickets = [
                ticket
                for ticket in tickets
                if ticket["status"] == status
            ]

        if priority is not None:
            tickets = [
                ticket
                for ticket in tickets
                if ticket["priority"] == priority
            ]

        if category is not None:
            tickets = [
                ticket
                for ticket in tickets
                if ticket["category"] == category
            ]

        if assigned_to is not None:
            tickets = [
                ticket
                for ticket in tickets
                if ticket["assigned_to"] == assigned_to
            ]

        return tickets

    def get_notes(self, ticket_id):
        """Return the follow-up notes for an existing ticket."""
        ticket = self.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        return ticket.get("notes", [])

    def add_note(self, ticket_id, author, message):
        ticket = self.get_ticket(ticket_id)

        if ticket is None:
            raise ValueError("Ticket not found")

        if ticket["status"] not in ("open", "in_progress"):
            raise ValueError(
                "Notes can only be added to "
                "open or in_progress tickets"
            )

        if (
            not isinstance(author, str)
            or not author.strip()
        ):
            raise ValueError(
                "Author must be a non-empty string"
            )

        if not isinstance(message, str):
            raise ValueError("Message must be a string")

        message = message.strip()

        if len(message) < 5 or len(message) > 300:
            raise ValueError(
                "Message must be between "
                "5 and 300 characters"
            )

        had_notes_field = "notes" in ticket
        notes = ticket.get("notes", [])

        # Find the highest existing note number.
        highest_number = 0

        for note in notes:
            number = int(note["note_id"][1:])
            if number > highest_number:
                highest_number = number

        note_id = f"N{highest_number + 1:03d}"

        note = {
            "note_id": note_id,
            "author": author.strip(),
            "message": message,
        }

        notes.append(note)
        ticket["notes"] = notes

        try:
            self._save()
        except Exception:
            notes.remove(note)

            if not had_notes_field:
                ticket.pop("notes", None)

            raise

        return note
