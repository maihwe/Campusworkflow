import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from campusflow.storage import TicketStorage


class TestTicketNotes(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "tickets.json"

        ticket = {
            "id": "T001",
            "title": "Test ticket",
            "category": "Hardware",
            "urgency": "high",
            "affected_users": 2,
            "priority": "high",
            "status": "open",
            "assigned_to": None,
        }

        self.path.write_text(
            json.dumps([ticket]),
            encoding="utf-8",
        )
        self.storage = TicketStorage(self.path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_note_is_saved_and_survives_reload(self):
        expected = [
            {
                "note_id": "N001",
                "author": "Faith",
                "message": "Checked the cable",
            }
        ]

        result = self.storage.add_note(
            "T001",
            "Faith",
            "Checked the cable",
        )

        self.assertEqual(result, expected[0])

        reloaded = TicketStorage(self.path)
        self.assertEqual(reloaded.get_notes("T001"), expected)

    def test_note_ids_are_sequential(self):
        self.storage.add_note("T001", "Faith", "Checked the cable")
        self.storage.add_note("T001", "Ada", "Tested the connection")

        notes = self.storage.get_notes("T001")

        self.assertEqual(
            [note["note_id"] for note in notes],
            ["N001", "N002"],
        )

    def test_note_id_continues_after_reload(self):
        self.storage.add_note("T001", "Faith", "Checked the cable")

        reloaded = TicketStorage(self.path)
        reloaded.add_note("T001", "Ada", "Tested the connection")

        self.assertEqual(
            [note["note_id"] for note in reloaded.get_notes("T001")],
            ["N001", "N002"],
        )

    def test_empty_note_message_is_rejected(self):
        with self.assertRaises(ValueError):
            self.storage.add_note("T001", "Faith", "   ")

    def test_short_note_message_is_rejected(self):
        with self.assertRaises(ValueError):
            self.storage.add_note("T001", "Faith", "No")

    def test_long_note_message_is_rejected(self):
        with self.assertRaises(ValueError):
            self.storage.add_note("T001", "Faith", "x" * 301)

    def test_empty_author_is_rejected(self):
        with self.assertRaises(ValueError):
            self.storage.add_note("T001", "   ", "Checked the cable")

    def test_non_string_author_is_rejected(self):
        with self.assertRaises(ValueError):
            self.storage.add_note("T001", None, "Checked the cable")

    def test_non_string_message_is_rejected(self):
        with self.assertRaises(ValueError):
            self.storage.add_note("T001", "Faith", 12345)

    def test_note_for_missing_ticket_is_rejected(self):
        with self.assertRaises(ValueError):
            self.storage.add_note("T999", "Faith", "Checked the cable")

    def test_invalid_note_does_not_consume_an_id(self):
        with self.assertRaises(ValueError):
            self.storage.add_note("T001", "Faith", "No")

        self.storage.add_note("T001", "Faith", "Checked the cable")

        self.assertEqual(
            self.storage.get_notes("T001")[0]["note_id"],
            "N001",
        )

    def test_notes_are_rejected_for_resolved_ticket(self):
        ticket = self.storage.get_ticket("T001")
        ticket["status"] = "resolved"

        with self.assertRaises(ValueError):
            self.storage.add_note("T001", "Faith", "Checked the cable")

    def test_notes_are_rejected_for_closed_ticket(self):
        ticket = self.storage.get_ticket("T001")
        ticket["status"] = "closed"

        with self.assertRaises(ValueError):
            self.storage.add_note("T001", "Faith", "Checked the cable")

    def test_ticket_without_notes_starts_with_empty_list(self):
        self.assertEqual(self.storage.get_notes("T001"), [])

    def test_failed_save_rolls_back_note(self):
        original_json = self.path.read_text(encoding="utf-8")

        with patch(
            "campusflow.storage.os.replace",
            side_effect=OSError("Simulated replacement failure"),
        ):
            with self.assertRaisesRegex(
                OSError, "Simulated replacement failure"
            ):
                self.storage.add_note(
                    "T001", "Faith", "Checked the cable"
                )

        self.assertEqual(self.storage.get_notes("T001"), [])
        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            original_json,
        )


if __name__ == "__main__":
    unittest.main()
