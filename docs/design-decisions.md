# CampusFlow Design Decisions

## 1. Programming language
We use Python3 because it supports modular programming, JSON handling, and automated testing.

## 2. Project structure
We separate ticket creation, workflow, storage, search, reporting, and the
understanding check into different modules. This makes the project easier to
understand, test, and maintain.

Search, filtering, and priority sorting live in `campusflow/search.py` as pure
functions. They never modify the tickets they are given, so they can be tested
without the CLI. `TicketStorage.filter_tickets` delegates to the same shared
function so there is only one filtering implementation.

## 3. Ticket data
Every ticket will use the same agreed fields:
- id
- title
- category
- urgency
- affected_users
- priority
- status
- assigned_to
- notes

## 4. Priority rules
The priority rules must be evaluated in this order:
1. Critical: high urgency AND at least 10 affected users.
2. High: high urgency OR at least 10 affected users.
3. Medium: medium urgency OR at least 3 affected users.
4. Low: none of the above.

## 5. Ticket workflow
New tickets begin as open. A ticket must be assigned before moving to in_progress. Tickets normally transition from open to in_progress to resolved. A resolved ticket can be reopened to open or closed. Closed tickets are final and cannot be reopened or modified through workflow operations. The unresolved queue excludes both resolved and closed tickets. Reports count all four statuses.
A closed ticket is final; a new occurrence must receive a new ticket ID.

## 6. Queue ordering
Unresolved tickets are sorted by critical, high, medium, then low priority. Ticket IDs use the format `T` followed by at least three digits, such as `T001` and `T002`. Tickets with equal priority are sorted by the numeric portion of the ID, so `T002` comes before `T010`.

## 7. Storage
We use JSON for local persistence. The application validates loaded JSON before replacing the current in-memory ticket collection. Malformed or invalid ticket data and duplicate ticket IDs are rejected.

Each ticket contains a `notes` list. Each note contains:
- note_id
- author
- message

Note IDs are generated separately for each ticket using the format `N001`, `N002`, and so on. Note authors must not be blank, and note messages must contain between 5 and 300 characters after trimming whitespace. Notes can only be added to tickets with `open` or `in_progress` status.

Validation happens before mutation so rejected operations do not partially change ticket data or consume a note ID. Storage mutations are also rolled back in memory if saving fails.


## 8. Testing
We use Python's `unittest` framework. CampusFlow Next requires at least 14 meaningful tests across the team, with at least 5 meaningful tests contributed by each engineer. Tests cover valid behaviour, invalid operations, persistence, validation, workflow protections, and edge cases.


## 9. Team integration
Before combining code, both team members must agree on function names, parameters, return values, ticket fields, and error behavior.

Agreed note interface between Engineer A (data layer) and Engineer B (CLI):

- `add_note(ticket_id, author, message)` adds a note and returns the ticket's
  complete notes list, with the new note last. The CLI shows `notes[-1]`.
- `get_notes(ticket_id)` returns a copy of the ticket's notes list.
- Both raise `ValueError` with a clear message for invalid input, and a
  rejected note never consumes a note ID.

Filtering is owned by Engineer B in `campusflow/search.py`. Supplied filters
are combined with logical AND; a `None` filter is not applied. Sorting by
priority uses the numeric part of the ticket ID to break ties, so `T002`
precedes `T010`.

## 10. Status of decisions
These decisions describe the intended design. We will update this document if the implementation or agreed requirements change.
