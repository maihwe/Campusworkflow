import unittest

from campusflow.service import TicketService


class TestTicketService(unittest.TestCase):
    def setUp(self):
        self.service = TicketService()

    def create_ticket(self):
        return self.service.create(
            "T001",
            "Wi-Fi is down",
            "Network",
            "high",
            15,
        )

    def test_create_ticket(self):
        ticket = self.create_ticket()
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")

    def test_get_ticket(self):
        self.create_ticket()
        self.assertEqual(
            self.service.get("T001")["title"],
            "Wi-Fi is down",
        )

    def test_get_missing_ticket(self):
        with self.assertRaisesRegex(ValueError, "Ticket not found"):
            self.service.get("T999")

    def test_assign_ticket(self):
        self.create_ticket()
        self.assertEqual(
            self.service.assign("T001", "Ada")["assigned_to"],
            "Ada",
        )

    def test_add_note(self):
        self.create_ticket()

        notes = self.service.add_note(
            "T001",
            "Edwin",
            "Checked the network connection",
        )

        note = notes

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Edwin")
        self.assertEqual(
            note["message"],
            "Checked the network connection",
        )

    def test_update_ticket_status(self):
        self.create_ticket()
        self.service.assign("T001", "Ada")

        ticket = self.service.update_status(
            "T001",
            "in_progress",
        )

        self.assertEqual(ticket["status"], "in_progress")

    def test_filter_tickets(self):
        self.create_ticket()

        self.service.create(
            "T002",
            "Printer is broken",
            "Hardware",
            "low",
            1,
        )

        self.service.assign("T001", "Ada")
        self.service.update_status("T001", "in_progress")

        tickets = self.service.filter(status="open")

        self.assertEqual(
            [ticket["id"] for ticket in tickets],
            ["T002"],
        )

    def test_filter_tickets_by_title(self):
        self.create_ticket()

        self.service.create(
            "T002",
            "Printer is broken",
            "Hardware",
            "low",
            1,
        )

        tickets = self.service.filter(title="Wi-Fi")

        self.assertEqual(
            [ticket["id"] for ticket in tickets],
            ["T001"],
        )

    def test_start_ticket(self):
        self.create_ticket()
        self.service.assign("T001", "Ada")

        self.assertEqual(
            self.service.start("T001")["status"],
            "in_progress",
        )

    def test_resolve_ticket(self):
        self.create_ticket()
        self.service.assign("T001", "Ada")
        self.service.start("T001")

        self.assertEqual(
            self.service.resolve("T001")["status"],
            "resolved",
        )

    def test_reopen_ticket(self):
        self.create_ticket()
        self.service.assign("T001", "Ada")
        self.service.start("T001")
        self.service.resolve("T001")

        self.assertEqual(
            self.service.reopen("T001")["status"],
            "open",
        )

    def test_close_ticket(self):
        self.create_ticket()
        self.service.assign("T001", "Ada")
        self.service.start("T001")
        self.service.resolve("T001")

        self.assertEqual(
            self.service.close("T001")["status"],
            "closed",
        )

    def test_start_ticket_requires_assignment(self):
        self.create_ticket()

        with self.assertRaisesRegex(ValueError, "assigned"):
            self.service.start("T001")

    def test_closed_ticket_cannot_be_reopened(self):
        self.create_ticket()
        self.service.assign("T001", "Ada")
        self.service.start("T001")
        self.service.resolve("T001")
        self.service.close("T001")

        with self.assertRaises(ValueError):
            self.service.reopen("T001")


if __name__ == "__main__":
    unittest.main()