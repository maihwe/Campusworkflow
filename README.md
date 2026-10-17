# CampusFlow — IT Helpdesk Ticket Manager

CampusFlow is a Python application for creating, prioritizing, assigning, and tracking IT helpdesk tickets.

## Project Goals

- Create and validate IT helpdesk tickets.
- Calculate ticket priority automatically.
- Assign tickets to support personnel.
- Protect valid ticket status transitions.
- Prevent unassigned tickets from moving to `in_progress`.
- Add follow-up notes to `open` and `in_progress` tickets.
- Validate note authors and messages.
- Generate per-ticket note IDs such as `N001` and `N002`.
- Search and filter tickets.
- Sort the open work queue by priority and ticket ID.
- Generate ticket reports and analytics.
- Save and load ticket data safely using JSON.
- Validate saved data before replacing in-memory data.
- Test the application with Python's `unittest` framework.
- Generate reports containing category totals, unresolved and resolved counts, and resolution percentage.
- Provide a CLI Engineering Understanding Check with six scenario questions.

## Team Responsibilities

### Engineer A

Engineer A is responsible for:

- Validation helpers and data integrity.
- Assignment and status mutation protections.
- Follow-up note data validation.
- JSON save/load safety and ID continuity.
- Business and data-layer note functionality.
- The `add_note` service operation.
- Engineer A tests.

### Engineer B

Engineer B is responsible for:

- CLI follow-up note interaction and display.
- Ticket search and filtering UI.
- Combined search filters and the optional priority-sorted result view.
- Reports and analytics display.
- The Engineering Understanding Check.
- Engineer B tests.

Both engineers must coordinate shared interfaces and preserve existing CampusFlow behaviour while integrating CampusFlow Next features.

## Run Tests

Run the following command from the project root:

```bash
python3 -m unittest discover -s tests -v
```

## CLI Menu

```text
========== CampusFlow ==========
1. Create ticket
2. List all tickets
3. View ticket details
4. Assign ticket
5. Start ticket work
6. Resolve ticket
7. Reopen ticket
8. Close ticket
9. View unresolved queue
10. Generate report
11. Search tickets by title
12. Search tickets sorted by priority
13. Add follow-up note
14. View ticket notes
15. Engineering Understanding Check
0. Exit
```

Option 9 is the original Open Work Queue. It must retain the behaviour required by the project specification. Option 12 provides a separate optional priority-sorted view of search results and does not replace option 9.

## Search and Filtering

Menu options 11 and 12 are read-only. A search never edits a stored ticket.

- Titles are matched using case-insensitive substring matching. For example, `wi-fi` matches `Campus Wi-Fi is down`.
- Matching is exact with respect to punctuation. The search does not correct spelling, so `wifi` does not match `Wi-Fi`.
- Category, status, and priority filters are optional. Press Enter to skip a filter.
- Supplied filters are combined using logical AND. A ticket must match the title and every supplied filter.
- Invalid filter values are rejected with a message, and the prompt is shown again.
- Results display the ticket ID, title, category, priority, status, and assignee.
- Option 12 orders matching results by priority and then by numeric ticket ID.

The search rules live in `campusflow/search.py` as pure functions that operate on a list of tickets. This allows them to be tested independently of the menu.

## Notes in the CLI

Menu option 13 adds a follow-up note through the storage and service layers. Option 14 lists a ticket's notes in note ID order.

- Notes can only be added to tickets with `open` or `in_progress` status.
- A resolved ticket must be reopened before another note can be added.
- A rejected note must not change the ticket or consume a note ID.
- The author cannot be blank.
- The message must contain between 5 and 300 characters after trimming whitespace.
- Invalid input is re-prompted in the CLI.
- Errors returned by the data layer are reported using a message such as `Note was not added: <reason>`.

## Engineering Understanding Check

Menu option 15 provides a six-question multiple-choice check on the application's behaviour.

- Answers must be A, B, C, or D.
- Invalid answers are rejected and re-prompted.
- Each correct answer earns one point out of six.
- The question bank in `campusflow/understanding_check.py` is separate from the scoring function and the CLI menu loop.
- After scoring, the learner is asked to explain at least two answers.
- Explanations are collected during the current session for mentor discussion. They are not automatically graded and are not saved for later sessions.

## JSON Data File

`data/tickets.json` stores ticket data as a JSON list of ticket objects. The storage layer is responsible for loading, validation, and safe persistence.

Each ticket stores the following fields:

```text
id
title
category
urgency
affected_users
priority
status
assigned_to
notes
```

The `notes` field is a list of note objects. Each note contains `note_id`, `author`, and `message`.

Older ticket records may not contain a `notes` key. During loading, the storage layer supplies an empty list for missing `notes` fields while preserving existing notes and validating the ticket data.

The current `data/tickets.json` file contains `"notes": []` for all 13 existing tickets. Their other ticket data was preserved.

The loader validates the complete dataset before replacing the in-memory ticket collection. Invalid JSON, duplicate ticket IDs, and invalid ticket data are rejected.

## Project Status

The project is under development. Features should be marked complete only after implementation and testing.

## Ticket IDs

Each ticket has a unique string ID consisting of `T` followed by at least three digits, such as `T001`, `T002`, and `T003`.

New tickets receive the next available numeric ID. Existing saved tickets retain their IDs during normal application use.

## Follow-up Notes

Tickets contain a `notes` list for recording follow-up information.

Each note contains:

- `note_id`
- `author`
- `message`

Note IDs are generated independently for each ticket using IDs such as `N001`, `N002`, and `N003`.

Notes can only be added while a ticket is `open` or `in_progress`. A resolved ticket must be reopened before another note can be added.

The note author must not be blank. The note message is trimmed and must contain between 5 and 300 characters.

Saved notes are preserved in JSON, and their ID sequence continues correctly after the application reloads.
