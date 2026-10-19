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
- Search tickets by title with case-insensitive substring matching.
- Combine title, category, status, and priority filters (all must match).
- View search results sorted by priority and ticket ID.
- Sort the open work queue by priority and ticket ID.
- Generate ticket reports and analytics, including resolution percentage.
- Run an interactive Engineering Understanding Check.
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
- Ticket search and filtering UI, including combined filters and the optional priority-sorted results view.
- Reports and analytics, including resolution percentage.
- The interactive Engineering Understanding Check.
- Engineer B tests.

The shared note interface is `add_note(ticket_id, author, message)`. It returns
the ticket's full notes list (so the CLI can display the note just added), and
`get_notes(ticket_id)` returns a copy of that list. Both raise `ValueError`
with a friendly message for invalid input.

Both engineers must coordinate shared interfaces and preserve existing CampusFlow behaviour while integrating CampusFlow Next features.

## Run Tests

Run the following command from the project root:

```bash
python3 -m unittest discover -s tests -v
```

## Run the application

From a fresh clone of the repository:

    git clone <repository-url>
    cd <repository-folder>
    python3 main.py

The application needs only Python 3 and the standard library. Ticket data is
read from and written to `data/tickets.json`.

## Search and filtering

Menu option **11** searches tickets by title and lets you add optional
category, status, and priority filters:

- Title matching is a case-insensitive substring search (`WI-FI` and `wi-fi`
  match each other; spelling correction is not attempted).
- Supplied filters are combined with logical **AND** — every filter must match.
- Pressing Enter skips a filter. Invalid options re-prompt instead of ending
  the search.
- Results show ID, title, category, priority, status, and assignee.

Menu option **14** runs the same search and displays the results sorted by
priority (critical > high > medium > low) and then by numeric ticket ID. The
original Open Work Queue (option 9) is unchanged and still lists only `open`
tickets.

## Reports

Menu option **10** reports total tickets, counts by status, priority, and
category, the unresolved count (open + in_progress), the resolved count, and
the resolution percentage (resolved / total * 100). An empty dataset reports
0% without a division error. Reopened tickets are counted by their current
status, and each ticket is counted once.

## Engineering Understanding Check

Menu option **15** runs six multiple-choice scenario questions. Only A/B/C/D
are accepted (invalid answers re-prompt), the score is out of six, and the
learner is asked to explain at least two answers. Explanations are appended to
`data/quiz_explanations.txt` for mentor discussion.

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
- Explanations are appended to `data/quiz_explanations.txt` for mentor discussion. They are saved for review and are not automatically graded.

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

Saved notes are preserved in JSON and their ID sequence continues correctly after the application reloads.

`add_note` returns the ticket's complete notes list (with the new note last),
and rejected notes never consume a note ID.

## JSON storage format

`data/tickets.json` is a JSON list of ticket objects. Each ticket contains
`id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`,
`assigned_to`, and `notes`. Each note contains `note_id`, `author`, and
`message`:

```json
[
  {
    "id": "T001",
    "title": "Campus wifi down",
    "category": "Network",
    "urgency": "high",
    "affected_users": 15,
    "priority": "critical",
    "status": "open",
    "assigned_to": "Ada",
    "notes": [
      {
        "note_id": "N001",
        "author": "Mentor A",
        "message": "Wi-Fi router reboot attempted"
      }
    ]
  }
]
```

On load, the whole file is validated before it replaces the in-memory
collection: the structure, required keys, ticket ID format and uniqueness,
category/urgency/priority consistency, legal statuses, and note shapes and
per-ticket ID uniqueness. A malformed, corrupt, or duplicate record is
rejected with a clear `ValueError`, and the current in-memory tickets are left
untouched. Tickets saved before notes existed are still accepted; a missing
`notes` list is treated as empty.
