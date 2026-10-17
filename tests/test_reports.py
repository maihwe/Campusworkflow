import unittest

from campusflow.reports import generate_report


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


class TestReportTotals(unittest.TestCase):
    def test_empty_report_returns_zero_percent_without_crashing(self):
        report = generate_report([])

        self.assertEqual(report["total"], 0)
        self.assertEqual(report["resolution_percentage"], 0)
        self.assertEqual(report["unresolved_count"], 0)
        self.assertEqual(report["resolved_count"], 0)

    def test_counts_by_category(self):
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

    def test_unresolved_count_adds_open_and_in_progress(self):
        tickets = [
            make_ticket("T001", status="open"),
            make_ticket("T002", status="in_progress"),
            make_ticket("T003", status="resolved"),
            make_ticket("T004", status="closed"),
        ]

        report = generate_report(tickets)

        self.assertEqual(report["unresolved_count"], 2)
        self.assertEqual(report["resolved_count"], 1)

    def test_status_counts_never_double_count_a_ticket(self):
        tickets = [
            make_ticket("T001", status="open"),
            make_ticket("T002", status="in_progress"),
            make_ticket("T003", status="resolved"),
            make_ticket("T004", status="closed"),
        ]

        report = generate_report(tickets)

        self.assertEqual(report["total"], 4)
        self.assertEqual(sum(report["by_status"].values()), 4)

    def test_resolution_percentage_after_resolve_and_reopen(self):
        tickets = [
            make_ticket("T001", status="open"),
            make_ticket("T002", status="in_progress"),
        ]

        resolved = generate_report(
            [tickets[0], make_ticket("T002", status="resolved")]
        )

        self.assertEqual(resolved["resolution_percentage"], 50.0)

        reopened = generate_report(
            [make_ticket("T001", status="open"), tickets[1]]
        )

        self.assertEqual(reopened["resolved_count"], 0)
        self.assertEqual(reopened["unresolved_count"], 2)
        self.assertEqual(reopened["resolution_percentage"], 0.0)

    def test_report_uses_the_current_status_not_the_oldest_status(self):
        refreshed = [
            make_ticket("T001", status="open"),
            make_ticket("T002", status="resolved"),
        ]

        report = generate_report(refreshed)

        self.assertEqual(report["by_status"]["resolved"], 1)
        self.assertEqual(report["by_status"]["open"], 1)

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
