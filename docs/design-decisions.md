# CampusFlow Design Decisions

# Design Decision: Ticket Status Lifecycle

**Project:** CampusFlow

**Decision:** Adopt a four-status ticket lifecycle

**Status:** Accepted for implementation

## 1. Decision

CampusFlow will use four ticket statuses:

- `open`
- `in_progress`
- `resolved`
- `closed`

These status values must be used consistently across ticket creation, storage, workflow management, reporting, and automated tests.

## 2. Status Definitions

| Status | Meaning |
|---|---|
| `open` | A ticket has been created and is awaiting work. |
| `in_progress` | An assigned staff member is actively working on the issue. |
| `resolved` | The issue is believed to be fixed, but formal closure is pending. |
| `closed` | The ticket has been formally completed. |

## 3. Transition Rules

1. A newly created ticket starts with the status `open`.
2. A ticket must be assigned to a staff member before moving to `in_progress`.
3. A ticket may move from `in_progress` to `resolved` when the issue is believed to be fixed.
4. A resolved ticket may return to `open` if further work is required.
5. A resolved ticket may move to `closed` when formal closure is appropriate.
6. A closed ticket is final. If the problem occurs again, a new ticket must be created with a new ID.
7. Invalid status values and disallowed transitions must be rejected consistently.

## 4. Implementation Requirements

- All modules must use the same four status values.
- Storage must preserve valid ticket statuses when saving and loading tickets.
- Workflow logic must enforce assignment and transition rules.
- Reports must distinguish open, in-progress, resolved, and closed tickets.
- Automated tests must cover valid transitions, invalid transitions, assignment requirements, and reopening resolved tickets.

## 5. Reason for the Decision

Separating `resolved` from `closed` allows CampusFlow to distinguish an issue believed to be fixed from one that has been formally completed. This improves workflow clarity and reporting.

## 6. Integration Requirement

Before integration, the team must ensure that `tickets.py`, `storage.py`, `workflow.py`, `reports.py`, `main.py`, and their tests agree with this decision.

The implementation and tests must follow this document.



## 1. Programming language
We use Python3 because it supports modular programming, JSON handling, and automated testing.

## 2. Project structure
We separate ticket creation, workflow, storage, and reporting into different modules. This makes the project easier to understand, test, and maintain.

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

## 4. Priority rules
The priority rules must be evaluated in this order:
1. Critical: high urgency AND at least 10 affected users.
2. High: high urgency OR at least 10 affected users.
3. Medium: medium urgency OR at least 3 affected users.
4. Low: none of the above.

## 5. Ticket workflow

New tickets begin with `open`. A ticket must be assigned before moving to `in_progress`.

The supported statuses are `open`, `in_progress`, `resolved`, and `closed`.

A resolved ticket may be reopened to `open` when further work is required.

A closed ticket is final; a new occurrence must receive a new ticket ID.

## 6. Queue ordering
Unresolved tickets are sorted by critical, high, medium, then low priority. Tickets with equal priority are sorted by numerical ticket ID.

## 7. Storage
We use JSON for local persistence. The application must handle malformed JSON clearly and preserve unique ticket IDs when loading existing tickets.

## 8. Testing
We use Python's unittest framework and aim for at least eight meaningful tests.

## 9. Team integration
Before combining code, both team members must agree on function names, parameters, return values, ticket fields, and error behavior.

## 10. Status of decisions
These decisions describe the intended design. We will update this document if the implementation or agreed requirements change.
