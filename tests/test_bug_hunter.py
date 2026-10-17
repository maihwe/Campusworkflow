"""Bug-hunter edge cases authored by Engineer B for Engineer A's storage module.

Case 1 - note IDs after resolve and reopen
Initial state: T001 is open and already has notes N001 and N002.
Input: resolve T001 -> attempt a note (rejected) -> reopen T001 -> add a note.
Expected result: the rejected attempt consumes no ID, the new note is N003, and
the earlier notes are still on the ticket.
Actual result: N003, with all three notes present.
Code change made: none. The test makes the "a rejected action changes nothing"
invariant visible; it passes against the current implementation.

Case 2 - note message length boundary
Initial state: T001 is open.
Input: a message of exactly 300 characters, then one of exactly 301 characters.
Expected result: 300 characters accepted, 301 rejected with no note stored.
Actual result: 300 accepted, 301 rejected, note count unchanged.
Code change made: none.
"""

import unittest

from campusflow.storage import TicketStorage
from campusflow.tickets import create_ticket


class TestNoteEdgeCases(unittest.TestCase):
    def setUp(self):
        self.storage = TicketStorage()
        self.storage.add_ticket(
            create_ticket(
                "T001",
                "Wi-Fi is down",
                "Network",
                "high",
                15,
            )
        )

    def resolve_ticket(self):
        self.storage.assign_ticket("T001", "Ada")
        self.storage.update_status("T001", "in_progress")
        self.storage.update_status("T001", "resolved")

    def test_rejected_note_after_resolve_does_not_consume_an_id(self):
        self.storage.add_note("T001", "Edwin", "First network check")
        self.storage.add_note("T001", "Ada", "Second network check")
        self.resolve_ticket()

        with self.assertRaises(ValueError):
            self.storage.add_note("T001", "Edwin", "Rejected while resolved")

        self.storage.update_status("T001", "open")

        note = self.storage.add_note("T001", "Edwin", "Third network check")

        self.assertEqual(note["note_id"], "N003")
        self.assertEqual(len(self.storage.get_ticket("T001")["notes"]), 3)

    def test_notes_survive_resolve_and_reopen(self):
        self.storage.add_note("T001", "Edwin", "First network check")
        self.resolve_ticket()

        notes_while_resolved = self.storage.get_ticket("T001")["notes"]

        self.storage.update_status("T001", "open")

        self.assertEqual(
            self.storage.get_ticket("T001")["notes"],
            notes_while_resolved,
        )
        self.assertEqual(notes_while_resolved[0]["note_id"], "N001")

    def test_note_message_length_boundary(self):
        longest_allowed = "x" * 300

        note = self.storage.add_note("T001", "Edwin", longest_allowed)

        self.assertEqual(note["message"], longest_allowed)

        with self.assertRaises(ValueError):
            self.storage.add_note("T001", "Edwin", "y" * 301)

        self.assertEqual(len(self.storage.get_ticket("T001")["notes"]), 1)


if __name__ == "__main__":
    unittest.main()
