# CampusFlow Design Decisions

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
New tickets begin as open. A ticket must be assigned before moving to in_progress. A resolved ticket must be explicitly reopened to open before modification.

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
