
import unittest

from campusflow.service import TicketService


class TestTicketService(unittest.TestCase):
    def setUp(self):
        self.service = TicketService()

    def test_create_ticket(self):
        ticket = self.service.create(
            1, "Wi-Fi is down", "Network", "high", 15
        )

        self.assertEqual(ticket["id"], 1)
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")

    def test_get_ticket(self):
        self.service.create(
            1, "Wi-Fi is down", "Network", "high", 15
        )

        ticket = self.service.get(1)

        self.assertEqual(ticket["title"], "Wi-Fi is down")

    def test_get_missing_ticket(self):
        with self.assertRaisesRegex(ValueError, "Ticket not found"):
            self.service.get(999)

    def test_assign_ticket(self):
        self.service.create(
            1, "Wi-Fi is down", "Network", "high", 15
        )

        ticket = self.service.assign(1, "Ada")

        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_update_ticket_status(self):
        self.service.create(
            1, "Wi-Fi is down", "Network", "high", 15
        )

        self.service.assign(1, "Ada")
        ticket = self.service.update_status(1, "in_progress")

        self.assertEqual(ticket["status"], "in_progress")

    def test_filter_tickets(self):
        self.service.create(
            1, "Wi-Fi is down", "Network", "high", 15
        )
        self.service.create(
            2, "Printer is broken", "Hardware", "low", 1
        )

        self.service.assign(1, "Ada")
        self.service.update_status(1, "in_progress")

        tickets = self.service.filter(status="open")

        self.assertEqual(
            [ticket["id"] for ticket in tickets],
            [2],
        )

if __name__ == "__main__":
    unittest.main()
