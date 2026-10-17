import unittest

from campusflow.reports import generate_report
from campusflow.service import TicketService
from campusflow.storage import TicketStorage


def make_ticket(
    ticket_id,
    category="Network",
    priority="critical",
    status="open",
    affected_users=15,
):
    return {
        "id": ticket_id,
        "title": "Ticket " + ticket_id,
        "category": category,
        "urgency": "high",
        "affected_users": affected_users,
        "priority": priority,
        "status": status,
        "assigned_to": None,
        "notes": [],
    }


class TestReports(unittest.TestCase):
    def test_empty_report_counts_and_percentage_are_zero(self):
        report = generate_report([])

        self.assertEqual(report["total"], 0)
        self.assertEqual(report["unresolved_count"], 0)
        self.assertEqual(report["resolved_count"], 0)
        self.assertEqual(report["resolution_percentage"], 0)

    def test_counts_follow_status_after_resolve_and_reopen(self):
        service = TicketService(TicketStorage())
        service.create("T001", "Wi-Fi down", "Network", "high", 15)
        service.assign("T001", "Ada")
        service.start("T001")
        service.resolve("T001")

        resolved = generate_report(service.get_all())
        self.assertEqual(resolved["resolved_count"], 1)
        self.assertEqual(resolved["unresolved_count"], 0)
        self.assertEqual(resolved["resolution_percentage"], 100.0)

        service.reopen("T001")

        reopened = generate_report(service.get_all())
        self.assertEqual(reopened["resolved_count"], 0)
        self.assertEqual(reopened["unresolved_count"], 1)
        self.assertEqual(reopened["resolution_percentage"], 0)

    def test_categories_are_counted_correctly(self):
        tickets = [
            make_ticket("T001", "Network"),
            make_ticket("T002", "Hardware"),
            make_ticket("T003", "Hardware"),
            make_ticket("T004", "Other"),
        ]

        report = generate_report(tickets)

        self.assertEqual(
            report["by_category"],
            {"Network": 1, "Hardware": 2, "Software": 0, "Other": 1},
        )

    def test_status_counts_do_not_overlap(self):
        tickets = [
            make_ticket("T001", status="open"),
            make_ticket("T002", status="in_progress"),
            make_ticket("T003", status="resolved"),
            make_ticket("T004", status="closed"),
        ]

        report = generate_report(tickets)

        self.assertEqual(report["total"], 4)
        self.assertEqual(sum(report["by_status"].values()), 4)
        self.assertEqual(report["unresolved_count"], 2)
        self.assertEqual(report["resolved_count"], 1)

    def test_resolution_percentage_for_partial_resolution(self):
        tickets = [
            make_ticket("T001", status="resolved"),
            make_ticket("T002", status="open"),
        ]

        report = generate_report(tickets)

        self.assertEqual(report["resolution_percentage"], 50.0)

    def test_rejects_non_list_input(self):
        with self.assertRaisesRegex(ValueError, "Tickets must be a list"):
            generate_report("not a list")

    def test_rejects_invalid_status(self):
        with self.assertRaisesRegex(ValueError, "Invalid ticket status"):
            generate_report([make_ticket("T001", status="pending")])

    def test_rejects_invalid_priority(self):
        with self.assertRaisesRegex(ValueError, "Invalid ticket priority"):
            generate_report([make_ticket("T001", priority="urgent")])

    def test_rejects_invalid_category(self):
        with self.assertRaisesRegex(ValueError, "Invalid ticket category"):
            generate_report([make_ticket("T001", category="Furniture")])


if __name__ == "__main__":
    unittest.main()
