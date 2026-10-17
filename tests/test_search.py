import copy
import unittest

from campusflow.search import (
    PRIORITY_ORDER,
    filter_tickets,
    numeric_part,
    search_tickets,
    sort_by_priority,
    sort_by_priority_then_id,
    sort_notes_by_id,
)


def make_ticket(
    ticket_id,
    title,
    category="Network",
    priority="high",
    status="open",
    assigned_to=None,
):
    return {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": "high",
        "affected_users": 15,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
        "notes": [],
    }

class TestFilterTickets(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            make_ticket("T001", "Campus wifi down", "Network", "critical"),
            make_ticket("T002", "Wifi login failure", "Software", "medium"),
            make_ticket(
                "T003",
                "Printer broken",
                "Hardware",
                "low",
                status="closed",
            ),
        ]

    def test_title_match_is_case_insensitive_substring(self):
        result = filter_tickets(self.tickets, title="WiFi")

        self.assertEqual([ticket["id"] for ticket in result], ["T001", "T002"])

    def test_empty_filters_return_every_ticket(self):
        self.assertEqual(filter_tickets(self.tickets), self.tickets)

    def test_combined_filters_use_and(self):
        result = filter_tickets(
            self.tickets,
            title="wifi",
            category="Network",
            status="open",
        )

        self.assertEqual([ticket["id"] for ticket in result], ["T001"])

    def test_filter_by_priority(self):
        result = filter_tickets(self.tickets, priority="low")

        self.assertEqual([ticket["id"] for ticket in result], ["T003"])

    def test_filter_by_assigned_to(self):
        tickets = self.tickets + [
            make_ticket("T004", "Router reboot", assigned_to="Ada")
        ]

        result = filter_tickets(tickets, assigned_to="Ada")

        self.assertEqual([ticket["id"] for ticket in result], ["T004"])

    def test_conflicting_filters_return_no_matches(self):
        result = filter_tickets(
            self.tickets,
            title="wifi",
            category="Hardware",
        )

        self.assertEqual(result, [])

    def test_filter_does_not_modify_input(self):
        snapshot = [dict(ticket) for ticket in self.tickets]

        filter_tickets(self.tickets, title="wifi", status="open")

        self.assertEqual(self.tickets, snapshot)

    def test_rejects_non_list_input(self):
        with self.assertRaises(ValueError):
            filter_tickets({"id": "T001"})


class TestSortByPriority(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            make_ticket("T010", "low task", priority="low"),
            make_ticket("T002", "medium task", priority="medium"),
            make_ticket("T007", "critical task", priority="critical"),
            make_ticket("T003", "high task", priority="high"),
        ]

    def test_sorted_by_priority_order(self):
        result = sort_by_priority(self.tickets)

        self.assertEqual(
            [ticket["priority"] for ticket in result],
            ["critical", "high", "medium", "low"],
        )

    def test_ties_are_broken_by_numeric_ticket_id(self):
        tickets = [
            make_ticket("T010", "second", priority="high"),
            make_ticket("T002", "first", priority="high"),
        ]

        result = sort_by_priority(tickets)

        self.assertEqual([ticket["id"] for ticket in result], ["T002", "T010"])

    def test_sort_does_not_modify_input(self):
        snapshot = list(self.tickets)

        sort_by_priority(self.tickets)

        self.assertEqual(self.tickets, snapshot)

    def test_priority_order_constant(self):
        self.assertEqual(
            PRIORITY_ORDER,
            {"critical": 0, "high": 1, "medium": 2, "low": 3},
        )


class TestSearchTickets(unittest.TestCase):
    def setUp(self):
        self.network_open = make_ticket(
            "T001", "Campus Wi-Fi is down", "Network", "critical", "open"
        )
        self.network_resolved = make_ticket(
            "T002", "Wi-Fi switch replaced", "Network", "high", "resolved"
        )
        self.hardware_open = make_ticket(
            "T003", "Printer is broken", "Hardware", "low", "open"
        )
        self.tickets = [
            self.network_open,
            self.network_resolved,
            self.hardware_open,
        ]

    def test_title_search_ignores_case_and_matches_substring(self):
        result = search_tickets(self.tickets, title="WI-FI")

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T001", "T002"],
        )

    def test_title_search_matches_part_of_the_title(self):
        result = search_tickets(self.tickets, title="switch")

        self.assertEqual([ticket["id"] for ticket in result], ["T002"])

    def test_search_does_not_fuzzy_match_different_punctuation(self):
        # Substring matching only: "wifi" is not part of "Wi-Fi".
        result = search_tickets(self.tickets, title="wifi")

        self.assertEqual(result, [])

    def test_search_without_filters_returns_every_ticket(self):
        self.assertEqual(search_tickets(self.tickets), self.tickets)

    def test_blank_filters_do_not_filter_by_that_field(self):
        result = search_tickets(
            self.tickets,
            title="   ",
            category="",
            status=None,
            priority="",
        )

        self.assertEqual(len(result), 3)

    def test_combined_filters_use_logical_and(self):
        result = search_tickets(
            self.tickets,
            title="wi-fi",
            category="Network",
            status="open",
        )

        self.assertEqual([ticket["id"] for ticket in result], ["T001"])

    def test_combined_filters_return_nothing_when_one_filter_fails(self):
        result = search_tickets(
            self.tickets,
            title="wi-fi",
            category="Hardware",
            status="open",
        )

        self.assertEqual(result, [])

    def test_filter_values_are_case_insensitive(self):
        result = search_tickets(
            self.tickets,
            category="network",
            status="OPEN",
            priority="CRITICAL",
        )

        self.assertEqual([ticket["id"] for ticket in result], ["T001"])

    def test_search_returns_empty_list_when_nothing_matches(self):
        result = search_tickets(self.tickets, title="projector")

        self.assertEqual(result, [])

    def test_search_does_not_modify_the_ticket_collection(self):
        before = copy.deepcopy(self.tickets)

        search_tickets(
            self.tickets,
            title="wi-fi",
            category="Network",
            status="open",
            priority="critical",
        )

        self.assertEqual(self.tickets, before)

    def test_search_rejects_non_list_collection(self):
        with self.assertRaisesRegex(ValueError, "Tickets must be a list"):
            search_tickets({"id": "T001"}, title="wi-fi")

    def test_search_rejects_non_dictionary_ticket(self):
        with self.assertRaisesRegex(
            ValueError, "Each ticket must be a dictionary"
        ):
            search_tickets([self.network_open, "T002"], title="wi-fi")

    def test_search_rejects_invalid_category_filter(self):
        with self.assertRaisesRegex(ValueError, "Category must be one of"):
            search_tickets(self.tickets, category="Furniture")

    def test_search_rejects_invalid_status_filter(self):
        with self.assertRaisesRegex(ValueError, "Status must be one of"):
            search_tickets(self.tickets, status="pending")

    def test_search_rejects_invalid_priority_filter(self):
        with self.assertRaisesRegex(ValueError, "Priority must be one of"):
            search_tickets(self.tickets, priority="urgent")

    def test_search_rejects_non_text_title_filter(self):
        with self.assertRaisesRegex(ValueError, "Title filter must be text"):
            search_tickets(self.tickets, title=7)


class TestSortedSearchResults(unittest.TestCase):
    def test_results_are_sorted_by_priority_then_numeric_ticket_id(self):
        tickets = [
            make_ticket("T005", "Low issue", "Other", "low", "open"),
            make_ticket("T003", "Critical issue", "Other", "critical", "open"),
            make_ticket("T001", "High issue", "Other", "high", "open"),
            make_ticket("T004", "Medium issue", "Other", "medium", "open"),
            make_ticket("T006", "Low issue two", "Other", "low", "open"),
        ]

        result = sort_by_priority_then_id(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T003", "T001", "T004", "T005", "T006"],
        )

    def test_ticket_ids_are_ordered_numerically_not_as_text(self):
        tickets = [
            make_ticket("T0010", "Ten", "Other", "high", "open"),
            make_ticket("T002", "Two", "Other", "high", "open"),
        ]

        result = sort_by_priority_then_id(tickets)

        self.assertEqual([ticket["id"] for ticket in result], ["T002", "T0010"])

    def test_sorting_does_not_change_the_original_list(self):
        first = make_ticket("T002", "Two", "Other", "low", "open")
        second = make_ticket("T001", "One", "Other", "critical", "open")
        tickets = [first, second]

        sort_by_priority_then_id(tickets)

        self.assertEqual(tickets, [first, second])

    def test_sorting_rejects_invalid_priority(self):
        tickets = [make_ticket("T001", "One", "Other", "urgent", "open")]

        with self.assertRaisesRegex(ValueError, "Invalid ticket priority"):
            sort_by_priority_then_id(tickets)

    def test_notes_are_sorted_by_note_id(self):
        notes = [
            {"note_id": "N010", "author": "Ada", "message": "Tenth note"},
            {"note_id": "N002", "author": "Ada", "message": "Second note"},
            {"note_id": "N001", "author": "Ada", "message": "First note"},
        ]

        result = sort_notes_by_id(notes)

        self.assertEqual(
            [note["note_id"] for note in result],
            ["N001", "N002", "N010"],
        )

    def test_numeric_part_rejects_malformed_identifier(self):
        for identifier in ("T1", "100", "", None, "T0"):
            with self.assertRaises(ValueError):
                numeric_part(identifier)




if __name__ == "__main__":
    unittest.main()
