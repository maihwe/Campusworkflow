
import unittest

from campusflow.reports import generate_report
from campusflow.workflow import (
    assign_ticket,
    start_ticket,
    resolve_ticket,
    reopen_ticket,
    close_ticket,
    get_unresolved_tickets,
)


class TestAssignTicket(unittest.TestCase):
    def setUp(self):
        self.ticket = {
            "id": "T001",
            "title": "Campus Wi-Fi is down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 15,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        }

    def test_assign_ticket(self):
        result = assign_ticket(self.ticket, "Faith")
        self.assertEqual(result["assigned_to"], "Faith")
        self.assertIs(result, self.ticket)

    def test_reject_empty_assignee(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.ticket, " ")

    def test_reject_assignment_to_resolved_ticket(self):
        self.ticket["status"] = "resolved"
        with self.assertRaises(ValueError):
            assign_ticket(self.ticket, "Faith")

    def test_reject_non_dictionary_ticket(self):
        with self.assertRaises(ValueError):
            assign_ticket([], "Faith")

    def test_reject_ticket_missing_status(self):
        ticket = {"assigned_to": None}
        with self.assertRaises(ValueError):
            assign_ticket(ticket, "Faith")

    def test_start_assigned_ticket(self):
        self.ticket["assigned_to"] = "Faith"
        result = start_ticket(self.ticket)
        self.assertEqual(result["status"], "in_progress")
        self.assertIs(result, self.ticket)

    def test_reject_start_unassigned_ticket(self):
        with self.assertRaises(ValueError):
            start_ticket(self.ticket)

    def test_resolve_in_progress_ticket(self):
        self.ticket["status"] = "in_progress"
        result = resolve_ticket(self.ticket)
        self.assertEqual(result["status"], "resolved")
        self.assertIs(result, self.ticket)

    def test_reject_resolving_open_ticket(self):
        with self.assertRaises(ValueError):
            resolve_ticket(self.ticket)

    def test_reopen_resolved_ticket(self):
        self.ticket["status"] = "resolved"
        result = reopen_ticket(self.ticket)
        self.assertEqual(result["status"], "open")
        self.assertIs(result, self.ticket)

    def test_reject_reopening_open_ticket(self):
        with self.assertRaises(ValueError):
            reopen_ticket(self.ticket)

    def test_get_unresolved_tickets_with_empty_list(self):
        self.assertEqual(get_unresolved_tickets([]), [])

    def test_get_unresolved_tickets_sorted(self):
        ticket2 = {
            **self.ticket,
            "id": "T002",
            "priority": "low",
            "status": "open",
        }
        ticket3 = {
            **self.ticket,
            "id": "T003",
            "priority": "high",
            "status": "in_progress",
        }
        ticket4 = {
            **self.ticket,
            "id": "T004",
            "priority": "critical",
            "status": "resolved",
        }

        tickets = [ticket2, ticket3, ticket4, self.ticket]
        result = get_unresolved_tickets(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T001", "T003", "T002"],
        )
        self.assertEqual(len(tickets), 4)

    def test_generate_empty_report(self):
        report = generate_report([])

        self.assertEqual(report["total"], 0)
        self.assertEqual(
            report["by_status"],
            {"open": 0, "in_progress": 0, "resolved": 0, "closed": 0},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 0, "high": 0, "medium": 0, "low": 0},
        )

    def test_generate_report_with_tickets(self):
        resolved_ticket = {
            **self.ticket,
            "id": "T002",
            "status": "resolved",
            "priority": "high",
        }

        report = generate_report([self.ticket, resolved_ticket])

        self.assertEqual(report["total"], 2)
        self.assertEqual(
            report["by_status"],
            {"open": 1, "in_progress": 0, "resolved": 1, "closed": 0},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 1, "high": 1, "medium": 0, "low": 0},
        )

    def test_report_counts_categories(self):
        hardware_ticket = {
            **self.ticket,
            "category": "Hardware",
        }
        software_ticket = {
            **self.ticket,
            "id": "T002",
            "category": "Software",
        }

        report = generate_report([hardware_ticket, software_ticket])

        self.assertEqual(
            report["by_category"],
            {
                "Network": 0,
                "Hardware": 1,
                "Software": 1,
                "Other": 0,
            },
        )

    def test_report_counts_unresolved_tickets(self):
        open_ticket = {**self.ticket, "status": "open"}
        in_progress_ticket = {
            **self.ticket,
            "id": "T002",
            "status": "in_progress",
        }
        resolved_ticket = {
            **self.ticket,
            "id": "T003",
            "status": "resolved",
        }

        report = generate_report(
            [open_ticket, in_progress_ticket, resolved_ticket]
        )

        self.assertEqual(report["unresolved_count"], 2)
        self.assertEqual(report["resolved_count"], 1)

    def test_report_resolution_percentage(self):
        resolved_ticket = {
            **self.ticket,
            "id": "T002",
            "status": "resolved",
        }

        report = generate_report([self.ticket, resolved_ticket])

        self.assertEqual(report["resolution_percentage"], 50.0)

    def test_empty_report_resolution_percentage_is_zero(self):
        report = generate_report([])

        self.assertEqual(report["resolution_percentage"], 0)
        self.assertEqual(report["unresolved_count"], 0)
        self.assertEqual(report["resolved_count"], 0)

    def test_close_resolved_ticket(self):
        self.ticket["status"] = "resolved"
        result = close_ticket(self.ticket)
        self.assertEqual(result["status"], "closed")
        self.assertIs(result, self.ticket)

    def test_reject_closing_open_ticket(self):
        with self.assertRaises(ValueError):
            close_ticket(self.ticket)

    def test_closed_ticket_cannot_be_reopened(self):
        self.ticket["status"] = "closed"
        with self.assertRaises(ValueError):
            reopen_ticket(self.ticket)

    def test_closed_ticket_cannot_be_reassigned(self):
        self.ticket["status"] = "closed"
        with self.assertRaises(ValueError):
            assign_ticket(self.ticket, "Faith")

    def test_closed_ticket_excluded_from_unresolved_queue(self):
        closed_ticket = {
            **self.ticket,
            "id": "T002",
            "status": "closed",
        }

        result = get_unresolved_tickets([self.ticket, closed_ticket])

        self.assertEqual([ticket["id"] for ticket in result], ["T001"])

    def test_report_counts_closed_tickets(self):
        closed_ticket = {
            **self.ticket,
            "id": "T002",
            "status": "closed",
        }

        report = generate_report([self.ticket, closed_ticket])

        self.assertEqual(report["total"], 2)
        self.assertEqual(
            report["by_status"],
            {"open": 1, "in_progress": 0, "resolved": 0, "closed": 1},
        )

    def test_report_counts_affected_users_across_all_tickets(self):
        ticket1 = {**self.ticket, "affected_users": 15}
        ticket2 = {
            **self.ticket,
            "id": "T002",
            "affected_users": 10,
            "status": "closed",
        }

        report = generate_report([ticket1, ticket2])

        self.assertEqual(report["total_affected_users"], 25)

    def test_report_counts_affected_users_on_closed_tickets(self):
        open_ticket = {
            **self.ticket,
            "affected_users": 8,
            "status": "open",
        }
        closed_ticket = {
            **self.ticket,
            "id": "T002",
            "affected_users": 15,
            "status": "closed",
        }
        another_closed_ticket = {
            **self.ticket,
            "id": "T003",
            "affected_users": 10,
            "status": "closed",
        }

        report = generate_report(
            [open_ticket, closed_ticket, another_closed_ticket]
        )

        self.assertEqual(report["closed_affected_users"], 25)

    def test_reject_start_ticket_with_whitespace_assignee(self):
        self.ticket["assigned_to"] = " "
        with self.assertRaises(ValueError):
            start_ticket(self.ticket)

    def test_reject_start_ticket_with_non_string_assignee(self):
        self.ticket["assigned_to"] = 123
        with self.assertRaises(ValueError):
            start_ticket(self.ticket)

    def test_reject_assignment_to_closed_ticket(self):
        self.ticket["status"] = "closed"
        with self.assertRaisesRegex(ValueError, "Reopen the ticket"):
            assign_ticket(self.ticket, "Faith")

    def test_generate_report_rejects_non_list_input(self):
        with self.assertRaisesRegex(ValueError, "Tickets must be a list"):
            generate_report({"status": "open", "priority": "low"})


if __name__ == "__main__":
    unittest.main()
