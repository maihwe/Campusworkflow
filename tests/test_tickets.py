
import unittest

from campusflow.tickets import calculate_priority, create_ticket


class TestCalculatePriority(unittest.TestCase):
    def test_critical_priority(self):
        self.assertEqual(calculate_priority("high", 15), "critical")

    def test_high_priority(self):
        self.assertEqual(calculate_priority("high", 3), "high")

    def test_medium_priority(self):
        self.assertEqual(calculate_priority("medium", 5), "medium")

    def test_medium_priority_from_affected_users(self):
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_low_priority(self):
        self.assertEqual(calculate_priority("low", 2), "low")

    def test_invalid_urgency(self):
        with self.assertRaises(ValueError):
            calculate_priority("urgent", 5)

    def test_rejects_decimal_affected_users(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", 2.5)

    def test_rejects_boolean_affected_users(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", True)


class TestCreateTicket(unittest.TestCase):
    def test_creates_ticket_with_expected_fields(self):
        ticket = create_ticket(
            1, "Wi-Fi is down", "Network", "high", 15
        )

        self.assertEqual(ticket["id"], 1)
        self.assertEqual(ticket["title"], "Wi-Fi is down")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 15)
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])

    def test_rejects_invalid_ticket_id(self):
        with self.assertRaises(ValueError):
            create_ticket(-1, "Wi-Fi is down", "Network", "high", 15)

    def test_rejects_zero_ticket_id(self):
        with self.assertRaises(ValueError):
            create_ticket(0, "Wi-Fi is down", "Network", "high", 15)

    def test_rejects_decimal_ticket_id(self):
        with self.assertRaises(ValueError):
            create_ticket(1.5, "Wi-Fi is down", "Network", "high", 15)

    def test_rejects_boolean_ticket_id(self):
        with self.assertRaises(ValueError):
            create_ticket(True, "Wi-Fi is down", "Network", "high", 15)

    def test_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            create_ticket(1, "", "Network", "high", 15)

    def test_rejects_empty_category(self):
        with self.assertRaises(ValueError):
            create_ticket(1, "Wi-Fi is down", "", "high", 15)

    def test_rejects_negative_affected_users(self):
        with self.assertRaises(ValueError):
            create_ticket(1, "Printer issue", "Hardware", "low", -3)

    def test_rejects_invalid_urgency(self):
        with self.assertRaises(ValueError):
            create_ticket(1, "Wi-Fi is down", "Network", "urgent", 5)


if __name__ == "__main__":
    unittest.main()