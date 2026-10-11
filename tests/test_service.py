import unittest

from campusflow.service import TicketService


class TestTicketService(unittest.TestCase):
    def setUp(self):
        self.service = TicketService()

    def create_ticket(self):
        return self.service.create(
            1, "Wi-Fi is down", "Network", "high", 15
        )

    def test_create_ticket(self):
        ticket = self.create_ticket()
        self.assertEqual(ticket["id"], 1)
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")

    def test_get_ticket(self):
        self.create_ticket()
        self.assertEqual(self.service.get(1)["title"], "Wi-Fi is down")

    def test_get_missing_ticket(self):
        with self.assertRaisesRegex(ValueError, "Ticket not found"):
            self.service.get(999)

    def test_assign_ticket(self):
        self.create_ticket()
        self.assertEqual(self.service.assign(1, "Ada")["assigned_to"], "Ada")

    def test_update_ticket_status(self):
        self.create_ticket()
        self.service.assign(1, "Ada")
        ticket = self.service.update_status(1, "in_progress")
        self.assertEqual(ticket["status"], "in_progress")

    def test_filter_tickets(self):
        self.create_ticket()
        self.service.create(2, "Printer is broken", "Hardware", "low", 1)
        self.service.assign(1, "Ada")
        self.service.update_status(1, "in_progress")
        tickets = self.service.filter(status="open")
        self.assertEqual([ticket["id"] for ticket in tickets], [2])

    def test_start_ticket(self):
        self.create_ticket()
        self.service.assign(1, "Ada")
        self.assertEqual(self.service.start(1)["status"], "in_progress")

    def test_resolve_ticket(self):
        self.create_ticket()
        self.service.assign(1, "Ada")
        self.service.start(1)
        self.assertEqual(self.service.resolve(1)["status"], "resolved")

    def test_reopen_ticket(self):
        self.create_ticket()
        self.service.assign(1, "Ada")
        self.service.start(1)
        self.service.resolve(1)
        self.assertEqual(self.service.reopen(1)["status"], "open")

    def test_close_ticket(self):
        self.create_ticket()
        self.service.assign(1, "Ada")
        self.service.start(1)
        self.service.resolve(1)
        self.assertEqual(self.service.close(1)["status"], "closed")

    def test_start_ticket_requires_assignment(self):
        self.create_ticket()
        with self.assertRaisesRegex(ValueError, "assigned"):
            self.service.start(1)

    def test_closed_ticket_cannot_be_reopened(self):
        self.create_ticket()
        self.service.assign(1, "Ada")
        self.service.start(1)
        self.service.resolve(1)
        self.service.close(1)
        with self.assertRaises(ValueError):
            self.service.reopen(1)


if __name__ == "__main__":
    unittest.main()
