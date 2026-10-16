import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from campusflow.storage import TicketStorage
from campusflow.tickets import create_ticket


class TestTicketStorage(unittest.TestCase):
    def setUp(self):
        self.storage = TicketStorage()
        self.ticket = create_ticket(
            "T001", "Wi-Fi is down", "Network", "high", 15
        )

    def test_add_ticket(self):
        result = self.storage.add_ticket(self.ticket)

        self.assertEqual(result, self.ticket)
        self.assertEqual(len(self.storage.get_all_tickets()), 1)

    def test_get_ticket(self):
        self.storage.add_ticket(self.ticket)

        result = self.storage.get_ticket("T001")

        self.assertEqual(result, self.ticket)

    def test_get_missing_ticket(self):
        result = self.storage.get_ticket("T099")

        self.assertIsNone(result)

    def test_get_all_tickets(self):
        self.storage.add_ticket(self.ticket)
        second_ticket = create_ticket(
            "T002", "Printer is broken", "Hardware", "medium", 4
        )
        self.storage.add_ticket(second_ticket)

        result = self.storage.get_all_tickets()

        self.assertEqual(len(result), 2)

    def test_reject_duplicate_ticket_id(self):
        self.storage.add_ticket(self.ticket)

        with self.assertRaises(ValueError):
            self.storage.add_ticket(self.ticket)

    def test_update_status_to_in_progress(self):
        self.storage.add_ticket(self.ticket)
        self.storage.assign_ticket("T001", "Ada")

        result = self.storage.update_status("T001", "in_progress")

        self.assertEqual(result["status"], "in_progress")

    def test_cannot_close_ticket_directly_from_open(self):
        self.storage.add_ticket(self.ticket)

        with self.assertRaises(ValueError):
            self.storage.update_status("T001", "closed")

    def test_close_ticket_after_in_progress(self):
        self.storage.add_ticket(self.ticket)
        self.storage.assign_ticket("T001", "Ada")
        self.storage.update_status("T001", "in_progress")
        self.storage.update_status("T001", "resolved")

        result = self.storage.update_status("T001", "closed")

        self.assertEqual(result["status"], "closed")

    def test_resolved_ticket_can_be_reopened(self):
        self.storage.add_ticket(self.ticket)
        self.storage.assign_ticket("T001", "Ada")
        self.storage.update_status("T001", "in_progress")
        self.storage.update_status("T001", "resolved")

        result = self.storage.update_status("T001", "open")

        self.assertEqual(result["status"], "open")

    def test_cannot_start_work_without_assignment(self):
        self.storage.add_ticket(self.ticket)

        with self.assertRaises(ValueError):
            self.storage.update_status("T001", "in_progress")

    def test_closed_ticket_cannot_be_changed(self):
        self.storage.add_ticket(self.ticket)
        self.storage.assign_ticket("T001", "Ada")
        self.storage.update_status("T001", "in_progress")
        self.storage.update_status("T001", "resolved")
        self.storage.update_status("T001", "closed")

        with self.assertRaises(ValueError):
            self.storage.update_status("T001", "open")

    def test_invalid_status_is_rejected(self):
        self.storage.add_ticket(self.ticket)

        with self.assertRaises(ValueError):
            self.storage.update_status("T001", "pending")

    def test_cannot_reassign_resolved_ticket(self):
        self.storage.add_ticket(self.ticket)
        self.storage.assign_ticket("T001", "Ada")
        self.storage.update_status("T001", "in_progress")
        self.storage.update_status("T001", "resolved")

        with self.assertRaisesRegex(
            ValueError, "Reopen the ticket before assigning it"
        ):
            self.storage.assign_ticket("T001", "Faith")

    def test_cannot_reassign_closed_ticket(self):
        self.storage.add_ticket(self.ticket)
        self.storage.assign_ticket("T001", "Ada")
        self.storage.update_status("T001", "in_progress")
        self.storage.update_status("T001", "resolved")
        self.storage.update_status("T001", "closed")

        with self.assertRaisesRegex(
            ValueError, "Reopen the ticket before assigning it"
        ):
            self.storage.assign_ticket("T001", "Faith")

    def test_reject_empty_staff_name(self):
        self.storage.add_ticket(self.ticket)

        with self.assertRaises(ValueError):
            self.storage.assign_ticket("T001", "   ")

    # New tests for title search

    def test_filter_tickets_by_title(self):
        ticket = self.storage.add_ticket({
            "id": "T001",
            "title": "Campus Wi-Fi down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        })

        result = self.storage.filter_tickets(title="Wi-Fi")

        self.assertEqual(result, [ticket])

    def test_filter_tickets_by_title_is_case_insensitive(self):
        ticket = self.storage.add_ticket({
            "id": "T001",
            "title": "Campus Wi-Fi down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        })

        result = self.storage.filter_tickets(title="WI-FI")

        self.assertEqual(result, [ticket])

    def test_filter_tickets_by_status(self):
        ticket = self.storage.add_ticket({
            "id": "T001",
            "title": "Wi-Fi down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        })

        result = self.storage.filter_tickets(status="open")

        self.assertEqual(result, [ticket])

    def test_filter_tickets_by_priority(self):
        ticket = self.storage.add_ticket({
            "id": "T001",
            "title": "Wi-Fi down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        })

        result = self.storage.filter_tickets(priority="critical")

        self.assertEqual(result, [ticket])

    def test_filter_tickets_by_multiple_fields(self):
        ticket = self.storage.add_ticket({
            "id": "T001",
            "title": "Wi-Fi down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": "Ada",
        })

        result = self.storage.filter_tickets(
            status="open",
            category="Network",
            assigned_to="Ada",
        )

        self.assertEqual(result, [ticket])

    def test_filter_tickets_returns_empty_list_when_no_match(self):
        result = self.storage.filter_tickets(status="closed")

        self.assertEqual(result, [])

    def test_filter_tickets_returns_all_matching_tickets(self):
        first_ticket = {
            "id": "T001",
            "title": "Wi-Fi down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        }

        second_ticket = {
            "id": "T002",
            "title": "Printer broken",
            "category": "Hardware",
            "urgency": "low",
            "affected_users": 1,
            "priority": "low",
            "status": "closed",
            "assigned_to": None,
        }

        third_ticket = {
            "id": "T003",
            "title": "Login failure",
            "category": "Software",
            "urgency": "medium",
            "affected_users": 3,
            "priority": "medium",
            "status": "open",
            "assigned_to": None,
        }

        self.storage.add_ticket(first_ticket)
        self.storage.add_ticket(second_ticket)
        self.storage.add_ticket(third_ticket)

        result = self.storage.filter_tickets(status="open")

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T001", "T003"],
        )

    def test_ticket_persists_after_reloading_storage(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            storage = TicketStorage(path)
            ticket = create_ticket(
                "T001", "Wi-Fi is down", "Network", "high", 15
            )

            storage.add_ticket(ticket)
            reloaded_storage = TicketStorage(path)

            self.assertEqual(reloaded_storage.get_ticket("T001"), ticket)

    def test_malformed_json_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            path.write_text("{broken", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Invalid JSON"):
                TicketStorage(path)

    def test_ticket_missing_status_in_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            ticket = create_ticket(
                "T001", "Wi-Fi is down", "Network", "high", 15
            )
            del ticket["status"]

            path.write_text(json.dumps([ticket]), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Invalid ticket data"):
                TicketStorage(path)

    def test_invalid_status_in_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            ticket = create_ticket(
                "T001", "Wi-Fi is down", "Network", "high", 15
            )
            ticket["status"] = "flying"

            path.write_text(json.dumps([ticket]), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Invalid ticket data"):
                TicketStorage(path)

    def test_duplicate_ids_in_json_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            ticket = create_ticket(
                "T001", "Wi-Fi is down", "Network", "high", 15
            )
            path.write_text(
                json.dumps([ticket, ticket]),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Duplicate ticket ID"):
                TicketStorage(path)

    def test_failed_reload_preserves_existing_tickets(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            self.storage.add_ticket(self.ticket)
            original_ticket = self.storage.get_ticket("T001").copy()

            path.write_text(
                json.dumps([self.ticket, self.ticket]),
                encoding="utf-8",
            )
            self.storage.file_path = path

            with self.assertRaisesRegex(
                ValueError, "Duplicate ticket ID"
            ):
                self.storage._load()

            self.assertEqual(
                self.storage.get_ticket("T001"),
                original_ticket,
            )
            self.assertEqual(
                len(self.storage.get_all_tickets()),
                1,
            )

    def test_malformed_reload_preserves_existing_tickets(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"

            self.storage.add_ticket(self.ticket)
            original_ticket = self.storage.get_ticket("T001").copy()

            path.write_text(
                "{invalid json",
                encoding="utf-8",
            )
            self.storage.file_path = path

            with self.assertRaisesRegex(ValueError, "Invalid JSON"):
                self.storage._load()

            self.assertEqual(
                self.storage.get_ticket("T001"),
                original_ticket,
            )
            self.assertEqual(
                len(self.storage.get_all_tickets()),
                1,
            )

    def test_assignment_persists_after_reloading_storage(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            storage = TicketStorage(path)

            ticket = create_ticket(
                "T001", "Wi-Fi is down", "Network", "high", 15
            )
            storage.add_ticket(ticket)
            storage.assign_ticket("T001", "Faith")

            reloaded_storage = TicketStorage(path)

            self.assertEqual(
                reloaded_storage.get_ticket("T001")["assigned_to"],
                "Faith",
            )

    def test_failed_save_preserves_original_json(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            storage = TicketStorage(path)
            ticket = create_ticket(
                "T001", "Wi-Fi is down", "Network", "high", 15
            )

            storage.add_ticket(ticket)
            original_json = path.read_text(encoding="utf-8")

            second_ticket = create_ticket(
                "T002", "Printer is broken", "Hardware", "medium", 4
            )

            with patch(
                "campusflow.storage.os.replace",
                side_effect=OSError("Simulated replacement failure"),
            ):
                with self.assertRaisesRegex(
                    OSError, "Simulated replacement failure"
                ):
                    storage.add_ticket(second_ticket)

            self.assertEqual(
                path.read_text(encoding="utf-8"),
                original_json,
            )
            self.assertFalse(
                path.with_name(".tickets.json.tmp").exists()
            )

    def test_failed_save_preserves_ticket_status_in_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            storage = TicketStorage(path)
            ticket = create_ticket(
                "T001", "Wi-Fi is down", "Network", "high", 15
            )
            storage.add_ticket(ticket)
            storage.assign_ticket("T001", "Faith")

            with patch(
                "campusflow.storage.os.replace",
                side_effect=OSError("Simulated replacement failure"),
            ):
                with self.assertRaises(OSError):
                    storage.update_status("T001", "in_progress")

            self.assertEqual(storage.get_ticket("T001")["status"], "open")
            self.assertEqual(
                TicketStorage(path).get_ticket("T001")["status"], "open"
            )

    def test_failed_save_preserves_ticket_assignment_in_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            storage = TicketStorage(path)
            ticket = create_ticket(
                "T001", "Wi-Fi is down", "Network", "high", 15
            )
            storage.add_ticket(ticket)

            with patch(
                "campusflow.storage.os.replace",
                side_effect=OSError("Simulated replacement failure"),
            ):
                with self.assertRaises(OSError):
                    storage.assign_ticket("T001", "Faith")

            self.assertIsNone(storage.get_ticket("T001")["assigned_to"])
            self.assertIsNone(
                TicketStorage(path).get_ticket("T001")["assigned_to"]
            )

    def test_failed_save_does_not_add_ticket_to_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tickets.json"
            storage = TicketStorage(path)
            ticket = create_ticket(
                "T001", "Wi-Fi is down", "Network", "high", 15
            )

            with patch(
                "campusflow.storage.os.replace",
                side_effect=OSError("Simulated replacement failure"),
            ):
                with self.assertRaises(OSError):
                    storage.add_ticket(ticket)

            self.assertIsNone(storage.get_ticket("T001"))
            self.assertEqual(storage.get_all_tickets(), [])


if __name__ == "__main__":
    unittest.main()