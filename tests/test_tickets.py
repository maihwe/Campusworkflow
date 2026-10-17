
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

    def test_high_urgency_with_nine_users_is_high(self):
        self.assertEqual(calculate_priority("high", 9), "high")

    def test_high_urgency_with_ten_users_is_critical(self):
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_low_urgency_with_nine_users_is_medium(self):
        self.assertEqual(calculate_priority("low", 9), "medium")

    def test_low_urgency_with_ten_users_is_high(self):
        self.assertEqual(calculate_priority("low", 10), "high")

    def test_low_priority(self):
        self.assertEqual(calculate_priority("low", 2), "low")

    def test_invalid_urgency(self):
        with self.assertRaises(ValueError):
            calculate_priority("urgent", 5)

    def test_rejects_zero_affected_users(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", 0)

    def test_rejects_negative_affected_users(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", -1)

    def test_rejects_decimal_affected_users(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", 2.5)

    def test_rejects_string_affected_users(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", "2")

    def test_rejects_boolean_affected_users(self):
        with self.assertRaises(ValueError):
            calculate_priority("low", True)


class TestCreateTicket(unittest.TestCase):
    def test_creates_ticket_with_expected_fields(self):
        ticket = create_ticket(
            "T001", "Wi-Fi is down", "Network", "high", 15
        )

        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["title"], "Wi-Fi is down")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 15)
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(ticket["notes"], [])

    def test_rejects_invalid_ticket_id(self):
        with self.assertRaises(ValueError):
            create_ticket("BAD", "Wi-Fi is down", "Network", "high", 15)

    def test_rejects_short_ticket_id(self):
        with self.assertRaises(ValueError):
            create_ticket("T1", "Wi-Fi is down", "Network", "high", 15)

    def test_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", "", "Network", "high", 15)

    def test_rejects_whitespace_only_title(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", "   ", "Network", "high", 15)

    def test_rejects_non_string_title(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", None, "Network", "high", 15)

    def test_strips_title_whitespace(self):
        ticket = create_ticket(
            "T001", "  Wi-Fi is down  ", "Network", "high", 15
        )
        self.assertEqual(ticket["title"], "Wi-Fi is down")

    def test_rejects_empty_category(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", "Wi-Fi is down", "", "high", 15)

    def test_rejects_invalid_category(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", "Wi-Fi is down", "Food", "high", 15)

    def test_normalizes_category_capitalization(self):
        ticket = create_ticket(
            "T001", "Wi-Fi is down", "nEtWoRk", "high", 15
        )
        self.assertEqual(ticket["category"], "Network")

    def test_normalizes_urgency_capitalization(self):
        ticket = create_ticket(
            "T001", "Wi-Fi is down", "Network", " HIGH ", 15
        )
        self.assertEqual(ticket["urgency"], "high")

    def test_rejects_zero_affected_users(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", "Wi-Fi is down", "Network", "low", 0)

    def test_rejects_negative_affected_users(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", "Printer issue", "Hardware", "low", -3)

    def test_rejects_decimal_affected_users(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", "Printer issue", "Hardware", "low", 2.5)

    def test_rejects_string_affected_users(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", "Printer issue", "Hardware", "low", "2")

    def test_rejects_boolean_affected_users(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", "Printer issue", "Hardware", "low", True)

    def test_rejects_invalid_urgency(self):
        with self.assertRaises(ValueError):
            create_ticket("T001", "Wi-Fi is down", "Network", "urgent", 5)


if __name__ == "__main__":
    unittest.main()
