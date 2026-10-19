import contextlib
import io
import unittest
from unittest.mock import patch

import main as main_module
from campusflow.service import TicketService
from campusflow.storage import TicketStorage
from campusflow.understanding_check import LETTERS, question_bank

from main import (
    add_follow_up_note,
    list_unresolved,
    run_understanding_check,
    search_tickets_by_title,
    show_report,
    view_ticket_notes,
)


def run_with_inputs(answers, function, *args):
    """Run a CLI function with scripted input and return what it printed."""
    output = io.StringIO()

    with patch("builtins.input", side_effect=list(answers)):
        with contextlib.redirect_stdout(output):
            function(*args)

    return output.getvalue()


class CliTestCase(unittest.TestCase):
    def setUp(self):
        # No file path, so the tests never touch data/tickets.json.
        self.service = TicketService(TicketStorage())


class TestSearchCli(CliTestCase):
    def test_reprompts_invalid_filter_and_applies_combined_filters(self):
        self.service.create(
            "T001", "Campus Wi-Fi is down", "Network", "high", 15
        )
        self.service.create(
            "T002", "Printer is broken", "Hardware", "low", 1
        )

        output = run_with_inputs(
            ["wi-fi", "Furniture", "network", "open", ""],
            search_tickets_by_title,
            self.service,
        )

        self.assertIn("Invalid category 'Furniture'", output)
        self.assertIn("Search Results (1 found)", output)
        self.assertIn("T001", output)
        self.assertNotIn("T002", output)

    def test_reprompts_blank_search_title(self):
        output = run_with_inputs(
            ["", "printer", "", "", ""],
            search_tickets_by_title,
            self.service,
        )

        self.assertIn("Search title cannot be empty.", output)
        self.assertIn(
            "No tickets matched the supplied search and filters.", output
        )

    def test_search_can_be_cancelled(self):
        output = run_with_inputs(
            ["0"], search_tickets_by_title, self.service
        )

        self.assertIn("Search cancelled.", output)

    def test_search_reports_when_nothing_matches(self):
        self.service.create(
            "T001", "Printer is broken", "Hardware", "low", 1
        )

        output = run_with_inputs(
            ["wifi", "", "", ""], search_tickets_by_title, self.service
        )

        self.assertIn(
            "No tickets matched the supplied search and filters.", output
        )

    def test_priority_sorted_view_orders_results_by_priority(self):
        self.service.create(
            "T001", "Printer issue", "Hardware", "low", 1
        )
        self.service.create(
            "T002", "Wi-Fi issue", "Network", "high", 15
        )

        output = run_with_inputs(
            ["issue", "", "", ""],
            search_tickets_by_title,
            self.service,
            True,
        )

        self.assertIn("Search Results (priority order) (2 found)", output)
        self.assertLess(output.index("T002"), output.index("T001"))

    def test_search_does_not_change_stored_tickets(self):
        self.service.create(
            "T001", "Campus Wi-Fi is down", "Network", "high", 15
        )
        before = self.service.get("T001").copy()

        run_with_inputs(
            ["wi-fi", "network", "open", ""],
            search_tickets_by_title,
            self.service,
        )

        self.assertEqual(self.service.get("T001"), before)


class TestUnresolvedQueueCli(CliTestCase):
    def test_queue_shows_only_open_tickets_in_priority_and_id_order(self):
        self.service.create(
            "T001", "Low open ticket", "Other", "low", 1
        )
        self.service.create(
            "T002", "Critical in-progress ticket", "Network", "high", 15
        )
        self.service.create(
            "T003", "High open ticket", "Network", "medium", 2
        )
        self.service.create(
            "T004", "Resolved ticket", "Other", "low", 1
        )
        self.service.create(
            "T005", "Closed ticket", "Other", "low", 1
        )
        self.service.create(
            "T006", "Critical open ticket", "Network", "high", 15
        )
        self.service.create(
            "T010", "Another critical open ticket", "Network", "high", 15
        )

        # Give tickets their different lifecycle states.
        tickets = {ticket["id"]: ticket for ticket in self.service.get_all()}
        tickets["T002"]["status"] = "in_progress"
        tickets["T004"]["status"] = "resolved"
        tickets["T005"]["status"] = "closed"

        output = run_with_inputs([], list_unresolved, self.service)

        displayed_ids = [
            line.split(" | ")[0]
            for line in output.splitlines()
            if " | " in line
        ]

        self.assertEqual(displayed_ids, ["T006", "T010", "T003", "T001"])
        self.assertNotIn("T002", displayed_ids)
        self.assertNotIn("T004", displayed_ids)
        self.assertNotIn("T005", displayed_ids)


class TestNoteCli(CliTestCase):
    def test_adds_a_follow_up_note_to_an_open_ticket(self):
        self.service.create(
            "T001", "Wi-Fi is down", "Network", "high", 15
        )

        output = run_with_inputs(
            ["T001", "Edwin", "Checked the network connection"],
            add_follow_up_note,
            self.service,
        )

        notes = self.service.get("T001")["notes"]

        self.assertIn("Note N001 added to T001 by Edwin.", output)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["note_id"], "N001")

    def test_reprompts_blank_author_and_short_message(self):
        self.service.create(
            "T001", "Wi-Fi is down", "Network", "high", 15
        )

        output = run_with_inputs(
            ["T001", "   ", "Edwin", "Hi", "Valid network update"],
            add_follow_up_note,
            self.service,
        )

        self.assertIn("The note author cannot be blank.", output)
        self.assertIn(
            "The note message must be between 5 and 300 characters.", output
        )
        self.assertEqual(
            self.service.get("T001")["notes"][0]["message"],
            "Valid network update",
        )

    def test_note_on_resolved_ticket_is_rejected_and_changes_nothing(self):
        self.service.create(
            "T001", "Wi-Fi is down", "Network", "high", 15
        )
        self.service.assign("T001", "Ada")
        self.service.start("T001")
        self.service.resolve("T001")

        output = run_with_inputs(
            ["T001", "Edwin", "This note should be rejected"],
            add_follow_up_note,
            self.service,
        )

        self.assertIn("Note was not added:", output)
        self.assertEqual(self.service.get("T001")["notes"], [])

    def test_views_notes_in_note_id_order(self):
        self.service.create(
            "T001", "Wi-Fi is down", "Network", "high", 15
        )
        self.service.add_note("T001", "Edwin", "First network check")
        self.service.add_note("T001", "Ada", "Second network check")

        output = run_with_inputs(["T001"], view_ticket_notes, self.service)

        self.assertIn("N001", output)
        self.assertIn("N002", output)
        self.assertLess(output.index("N001"), output.index("N002"))

    def test_view_notes_reports_when_a_ticket_has_no_notes(self):
        self.service.create(
            "T001", "Wi-Fi is down", "Network", "high", 15
        )

        output = run_with_inputs(["T001"], view_ticket_notes, self.service)

        self.assertIn("No follow-up notes recorded for T001.", output)


class TestReportCli(CliTestCase):
    def test_empty_dataset_reports_zero_without_crashing(self):
        output = run_with_inputs([], show_report, self.service)

        self.assertIn("Total tickets: 0", output)
        self.assertIn("Unresolved tickets (open + in_progress): 0", output)
        self.assertIn("Resolved tickets: 0", output)
        self.assertIn("Resolution percentage: 0.0%", output)

    def test_report_shows_counts_and_percentage(self):
        self.service.create(
            "T001", "Wi-Fi is down", "Network", "high", 15
        )
        self.service.create(
            "T002", "Printer is broken", "Hardware", "low", 1
        )
        self.service.assign("T002", "Ada")
        self.service.start("T002")
        self.service.resolve("T002")

        output = run_with_inputs([], show_report, self.service)

        self.assertIn("Network: 1", output)
        self.assertIn("Hardware: 1", output)
        self.assertIn("Resolved tickets: 1", output)
        self.assertIn("Resolution percentage: 50.0%", output)


class TestUnderstandingCheckCli(CliTestCase):
    def test_rejects_invalid_answer_letter_and_scores_submitted_answers(self):
        questions = question_bank()
        answers = [question["answer"] for question in questions]

        wrong_answer = next(
            letter for letter in LETTERS if letter != answers[4]
        )
        answers[4] = wrong_answer

        inputs = []

        for index, answer in enumerate(answers):
            if index == 0:
                inputs.extend(["Z", answer])
            else:
                inputs.append(answer)

        inputs.extend(
            [
                "Q1,Q3",
                "An unassigned ticket must not start work.",
                "A failed load must keep current memory.",
            ]
        )

        output = run_with_inputs(inputs, run_understanding_check)

        self.assertIn(
            "Invalid choice. Please answer with A, B, C or D.", output
        )
        self.assertIn("Q5: incorrect", output)
        self.assertIn("Score: 5/6", output)
        self.assertIn("not auto-graded", output)

    def test_requires_at_least_two_explanations(self):
        import tempfile
        from pathlib import Path

        questions = question_bank()
        inputs = [question["answer"] for question in questions]
        inputs.extend(
            [
                "",
                "Q1,Q2",
                "Filters combine with AND.",
                "Memory must not change on a failed load.",
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temporary_main = str(Path(temp_dir) / "main.py")

            with patch.object(main_module, "__file__", temporary_main):
                output = run_with_inputs(
                    inputs, run_understanding_check
                )

            explanation_file = (
                Path(temp_dir) / "data" / "quiz_explanations.txt"
            )

            self.assertTrue(explanation_file.exists())
            saved_text = explanation_file.read_text(encoding="utf-8")
            self.assertIn("Filters combine with AND.", saved_text)
            self.assertIn(
                "Memory must not change on a failed load.",
                saved_text,
            )

        self.assertIn(
            "Please choose at least 2 valid question IDs", output
        )
        self.assertIn("Score: 6/6", output)
        self.assertIn("Explanations saved to", output)
        self.assertIn(
            "Explanations are saved for review and are not auto-graded.",
            output,
        )

if __name__ == "__main__":
    unittest.main()

class TestMenu(unittest.TestCase):
    def test_invalid_choice_is_reported_before_exit(self):
        memory_storage = TicketStorage()

        with patch("builtins.input", side_effect=["99", "0", "y"]):
            with patch("builtins.print") as printed:
                with patch.object(
                    main_module,
                    "TicketStorage",
                    return_value=memory_storage,
                ):
                    main_module.main()

        messages = " ".join(
            str(call) for call in printed.call_args_list
        )
        self.assertIn("Invalid option", messages)

    def test_exit_requires_confirmation(self):
        memory_storage = TicketStorage()
        prompts = []

        def fake_input(prompt=""):
            prompts.append(prompt)
            return {"Choose an option: ": "0",
                    "Are you sure you want to end the program? y/n: ": "y"}[prompt]

        with patch("builtins.input", side_effect=fake_input):
            with patch("builtins.print") as printed:
                with patch.object(
                    main_module,
                    "TicketStorage",
                    return_value=memory_storage,
                ):
                    main_module.main()

        self.assertIn(
            "Are you sure you want to end the program? y/n: ",
            prompts,
        )
        messages = " ".join(
            str(call) for call in printed.call_args_list
        )
        self.assertIn("Thank you for using CampusFlow.", messages)

    def test_cancelling_exit_returns_to_menu(self):
        memory_storage = TicketStorage()

        with patch("builtins.input", side_effect=["0", "n", "0", "y"]):
            with patch("builtins.print") as printed:
                with patch.object(
                    main_module,
                    "TicketStorage",
                    return_value=memory_storage,
                ):
                    main_module.main()

        messages = " ".join(
            str(call) for call in printed.call_args_list
        )
        self.assertIn(
            "Exit cancelled. Returning to the application...",
            messages,
        )
        self.assertIn("Thank you for using CampusFlow.", messages)

    def test_invalid_exit_confirmation_is_rejected(self):
        memory_storage = TicketStorage()

        with patch("builtins.input", side_effect=["0", "maybe", "y"]):
            with patch("builtins.print") as printed:
                with patch.object(
                    main_module,
                    "TicketStorage",
                    return_value=memory_storage,
                ):
                    main_module.main()

        messages = " ".join(
            str(call) for call in printed.call_args_list
        )
        self.assertIn(
            "Invalid response. Please enter y or n.",
            messages,
        )
