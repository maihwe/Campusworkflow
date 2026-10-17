# Campusflow Next BaseLine Check

## 1. baseLine Test

Before implementing the campusflow next changes, the existing application was tested to confirm that it was working correctly.

Command used:

python3 -m unittest discover -s test -v

result:

Ran 99 test in 0.090s

OK

this confirm that the existing CampusFlow application passed its test suite before the new changes were introduced.

## 2. BaseLine Inputs and Observations

### Input 1: Valid Ticket Creation
A valid ticket could be created with a title, cotegory, urgency, and number of affected users.

Observation:
The existing system successfully created tickets and calculated their priority.

### Input 2. Invalid Affected Users
Invalide value for affected users were tested.

Observation:
The existing validation rejected invalid affected_user valueinstead of creating an invalid ticket.

### Input 3. ticket Workflow
Existing ticket assinment and status transition were tested.

Observation:
The application already supported ticket assignment and staus changes such as moving a ticket through its existing workflow.

## 3. Improvements Identified for CampusFlow Next

The baseline review identified areas that needed to be added or strengthened for campusflow Next:

- Add follow-up notes to tickets.
- Validate note author and message data.
- Generate note IDs independently for each ticket.
- Prevent notes from being added to resolved tickets.
- Strengthen JSON validation before replacing in-memory ticket data.
- Reject duplicate or malformed ticket and note data during loading.
- Preserve data when saving fails.
- Preserve ticket and note ID continuity after saving and reloading.
- Keep the existing CampusFlow behaviour working while adding the new features.