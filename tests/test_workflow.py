
import unittest

from campusflow.reports import generate_report
from campusflow.workflow import (
    assign_ticket,
    start_ticket,
    resolve_ticket,
    reopen_ticket,
    get_unresolved_tickets,
)


class TestAssignTicket(unittest.TestCase):
    def setUp(self):
        self.ticket = {
            "id": 1,
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

    def test_reject_start_ticket_with_whitespace_assignee(self):
        self.ticket["assigned_to"] = " "

        with self.assertRaises(ValueError):
            start_ticket(self.ticket)

    def test_reject_start_ticket_with_non_string_assignee(self):
        self.ticket["assigned_to"] = 123

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

    def test_get_unresolved_tickets_sorted(self):
        ticket2 = {
            **self.ticket,
            "id": 2,
            "priority": "low",
            "status": "open",
        }
        ticket3 = {
            **self.ticket,
            "id": 3,
            "priority": "high",
            "status": "in_progress",
        }
        ticket4 = {
            **self.ticket,
            "id": 4,
            "priority": "critical",
            "status": "resolved",
        }

        tickets = [ticket2, ticket3, ticket4, self.ticket]

        result = get_unresolved_tickets(tickets)

        self.assertEqual([t["id"] for t in result], [1, 3, 2])
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
            "id": 2,
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
    def test_closed_ticket_is_counted_in_report(self):
        closed_ticket = {
            **self.ticket,
            "status": "closed",
        }

        report = generate_report([closed_ticket])

        self.assertEqual(report["by_status"]["closed"], 1)
        self.assertEqual(report["total"], 1)

    def test_closed_ticket_is_excluded_from_unresolved_queue(self):
        closed_ticket = {
            **self.ticket,
            "id": 2,
            "status": "closed",
        }

        result = get_unresolved_tickets([self.ticket, closed_ticket])

        self.assertEqual([ticket["id"] for ticket in result], [1])


    def test_reject_assignment_to_closed_ticket(self):
        ticket = {
            "id": 99,
            "title": "Network failure",
            "category": "network",
            "urgency": "high",
            "affected_users": 12,
            "priority": "critical",
            "status": "closed",
            "assigned_to": "Faith",
        }

        with self.assertRaisesRegex(ValueError, "Reopen the ticket"):
            assign_ticket(ticket, "Mathias")


    def test_generate_report_rejects_non_list_input(self):
        with self.assertRaisesRegex(ValueError, "Tickets must be a list"):
            generate_report({"status": "open", "priority": "low"})


if __name__ == "__main__":
    unittest.main()
