# CampusFlow AI Learning Log
Project Information
- Project: CampusFlow Next
- Team member: Faith Ejembi
- Project type: Python command-line ticket/helpdesk workflow
- Purpose: Improve the reliability, usability, testing, and maintainability of the existing CampusFlow project.
- Repository: https://github.com/maihwe/Campusworkflow
- Current feature branch: feat/campusflow-next-fixes
- Current verification date: 16 October 2026
This document records my learning, experiments, decisions, and verification while developing CampusFlow Next. It distinguishes between advice received from AI, experiments I actually ran, and work that still requires review.
## 1. Learning Goals
My goals for this project are to:
1. Understand the existing application before changing its behaviour.
2. Improve the application without breaking existing ticket-management features.
3. Write automated tests for normal behaviour, invalid inputs, and edge cases.
4. Understand how JSON persistence works and how to protect saved ticket data.
5. Learn how to implement searching, filtering, notes, reports, and an understanding check.
6. Verify AI recommendations independently rather than accepting them without testing.
7. Use Git branches and pull requests correctly.
8. Explain my implementation and testing decisions without relying entirely on AI.
## 2. Learning Entry — Understanding Existing Code and Tests
Problem
CampusFlow Next builds on an existing ticket-management application. Before extending it, I needed to understand the existing functions, storage format, tests, and workflow rules.
Initial understanding
I understood that the application stores tickets and provides operations for creating, assigning, updating, and viewing them. However, I needed to examine how the different modules work together and how changes could affect existing behaviour.
What I learned
A feature should not be changed in isolation without considering its dependencies. A change to storage can affect the CLI, reports, and tests. Similarly, a change to ticket filtering can affect the unresolved work queue. Automated tests help establish whether existing behaviour remains correct after a change.
Verification
I used the existing test suite as a regression check:
python3 -m unittest discover -s tests -v
Historical test results should remain associated with the runs in which they were obtained. The latest result is recorded in Section 8.
Decision
I continued working from the existing repository and created a feature branch instead of making the new changes directly on main.
What I can explain independently
- Regression testing: checking that previously working behaviour still works after changes.
- Feature branches: isolating development work from the main branch.
- Unit tests: checking the behaviour of individual functions or components.
- Integration: making sure the different parts of the application work together correctly.
## 3. Learning Entry — Case-Insensitive Text Matching
Problem
Searching for text should work consistently regardless of the capitalization used by the person searching. I investigated the difference between Python's lower() and casefold() methods.
Experiment
I ran this Python experiment:
samples = ["Straße", "STRASSE", "Cafe"]

for value in samples:
    print(repr(value), "|", repr(value.lower()), "|", repr(value.casefold()))

print("equal with lower  :", "Straße".lower() == "STRASSE".lower())
print("equal with casefold:", "Straße".casefold() == "STRASSE".casefold())
Actual observed output
'Straße' | 'straße' | 'strasse'
'STRASSE' | 'strasse' | 'strasse'
'Cafe' | 'cafe' | 'cafe'
equal with lower  : False
equal with casefold: True
What I learned
lower() converts uppercase letters to lowercase, while casefold() is designed for more comprehensive caseless text comparisons. In this example, casefold() converts the German character ß into ss, allowing "Straße" and "STRASSE" to compare equally after case folding.
Decision and limitation
For case-insensitive search, casefold() is useful when more comprehensive Unicode-aware matching is desired. Case folding does not automatically make all text equivalent; accent normalization is a separate concern. Search behaviour should match the project's requirements rather than assuming every spelling variation should match.
What I can explain independently
- Why text normalization helps with searching.
- Why casefold() can be more appropriate than lower() for caseless comparisons.
- Why a small experiment is useful before adopting an AI recommendation.
## 4. Learning Entry — Designing a Test That Exposes a Bug
Problem
A test can pass even when it does not adequately test the behaviour it is intended to verify. I investigated how the choice of test data affects whether a test exposes a bug.
Experiment and actual observed output
I compared a fixture that hides the bug with one that exposes it. The recorded output was:
fixture that hides the bug: True
fixture that exposes it  : False
What I learned
A test is useful when its inputs distinguish correct behaviour from incorrect behaviour. If a test uses values that produce the same result in both the correct and faulty implementations, it may pass without revealing the problem. A better test uses an input at which the expected and faulty behaviours differ.
When writing tests, I should ask:
1. What behaviour am I trying to prove?
2. What result should the correct implementation produce?
3. What would the faulty implementation produce?
4. Does this test input distinguish those two outcomes?
Evidence limitation: This recorded experiment demonstrates a testing principle, but it does not include enough detail to identify a specific production bug or prove that a particular code change fixed it. I should make such a claim only when I record the actual faulty behaviour, expected result, observed result, and correction.
## 5. Learning Entry — Safe JSON Storage and Backward Compatibility
Problem
CampusFlow tickets are stored in JSON. The newer application supports ticket notes, but older saved tickets may not contain a notes field. I needed to understand how the storage loader handles older records without unnecessarily rejecting otherwise valid ticket data.
Code examined
    # Older tickets may not have notes yet.
ticket.setdefault("notes", [])

if not required_fields.issubset(ticket):
    raise ValueError("Invalid ticket data in JSON storage")
What the code does
ticket.setdefault("notes", []) checks whether the dictionary already contains the notes key.
- If the key exists, its current value is preserved.
- If the key is missing, an empty list is added.
- The required-field check then validates whether the ticket contains the fields required by the loader.
This allows older tickets without a notes field to be upgraded in memory with an empty list.
What I learned and decision
Backward compatibility means allowing older valid data to continue working when the application gains new features. The default value must not hide unrelated corruption or replace existing note data. I kept the compatibility behaviour for missing notes while retaining validation for required fields and other stored values.
Verification performed
I validated the saved ticket JSON with:
python3 -m json.tool data/tickets.json > /dev/null && echo "Ticket JSON is valid"
Actual result:
Ticket JSON is valid
I also added storage tests covering older tickets without notes, duplicate note IDs, invalid note messages, and preserving existing in-memory tickets when a reload fails. The targeted storage-test run passed all four tests. After correcting the Open Work Queue, I reran the full test suite; the latest run passed all 168 tests. The queue regression and its verification are documented in Section 6.1.
What I can explain independently
- JSON is a text format used to store structured data.
- json.load() reads JSON data into Python objects.
- dict.setdefault() supplies a default only when a dictionary key is absent.
- Validation helps prevent malformed saved data from being accepted.
- Backward compatibility helps newer code work with older saved records.
Limitation: Valid JSON syntax alone does not prove that the data follows the application's schema. Storage tests and validation logic are needed for that.
## 6. Learning Entry — Searching, Filtering, and Sorting Tickets
Problem
Users need to find tickets without manually inspecting every record. CampusFlow Next introduces reusable search functions so the search logic can be tested independently of interactive CLI input.
What I learned
A search function can take a collection of tickets and criteria, then return matching records. Several criteria can be combined using logical AND. For example, if a user searches for a title and selects a status, a ticket should match both criteria to appear in the results.
Blank optional filters should not unintentionally exclude records. Sorting is separate from filtering: a search can first identify matching records and then sort those records by priority or ID.
Design decisions
- Keep search logic separate from CLI input and output.
- Normalize text before case-insensitive comparisons.
- Treat optional blank filters as unspecified.
- Combine supplied filters using AND semantics.
- Reject invalid filter values clearly.
- Avoid changing the original ticket collection during search or sorting.
Testing performed
The search test suite includes checks for:
- Matching text with different capitalization and matching part of a title.
- Handling punctuation differences.
- Searching with one or more filters and ignoring blank optional filters.
- Rejecting invalid filter values.
- Confirming that searching does not mutate the original data.
- Sorting tickets by priority and numeric ID.
- Sorting notes by their identifiers.
- Returning an empty result when nothing matches.
What I can explain independently
Separating search logic from the CLI makes the code easier to reuse and test. Pure functions are especially useful because their results can be checked without depending on interactive input or changes to global state.
### 6.1 Learning Entry — Fixing the Open Work Queue Regression
Problem
The Open Work Queue was intended to display only tickets with the open status. However, its previous filtering condition excluded only resolved and closed tickets. This allowed in_progress tickets to appear in a queue that should contain only open tickets.
How I identified the problem
I added a regression test that creates tickets with different lifecycle statuses and priorities. The test checks that only open tickets are displayed, sorted by priority and then by numeric ticket ID. The test includes critical, high, and low-priority open tickets, as well as tickets in in_progress, resolved, and closed states.
Expected behaviour
- Display only tickets whose status is open.
- Sort tickets by priority: critical, high, medium, then low.
- For tickets with equal priority, sort by numeric ticket ID.
- Do not display in_progress, resolved, or closed tickets.
- Display an appropriate message when no open tickets are available.
Correction
I changed the filter to check explicitly for the open status:
tickets = [
    ticket for ticket in service.get_all()
    if ticket["status"] == "open"
]
I also aligned the empty-state message and heading with the queue's purpose.
Verification
I ran the targeted regression test:
python3 -m unittest tests.test_cli.TestUnresolvedQueueCli -v
Actual result:
Ran 1 test in 0.002s

OK
I then ran the complete test suite:
python3 -m unittest discover -s tests -v
Actual result:
Ran 168 tests in 0.225s

OK
What I learned
A condition that excludes known completed states is not always equivalent to a condition that permits only the intended state. Explicitly checking status == "open" makes the queue's rule clearer and prevents other lifecycle states from appearing accidentally.
The regression test includes a ticket in the state that caused the problem. The full test suite also checks that the correction does not break other tested functionality.
What I can explain independently
- Why the previous filtering condition allowed in_progress tickets.
- Why explicitly checking for open is safer for this requirement.
- How the test checks both ticket visibility and sorting order.
- Why I ran the targeted test first and the full test suite afterwards.
Scope limitation: These tests passed on my current working branch. This does not establish that the change has been committed, pushed, reviewed by my partner, or merged into main.
## 7. Learning Entry — Notes, Reports, and the Understanding Check
### 7.1 Ticket notes
Notes provide additional information about a ticket without replacing its main fields. Important cases include:
- Rejecting an invalid note action without consuming a note ID.
- Preserving notes when a ticket is resolved and later reopened.
- Accepting a note at the permitted maximum length and rejecting one that exceeds it.
- Rejecting duplicate note IDs and invalid note records during loading.
- Preserving existing in-memory data if reloading invalid JSON fails.
The storage tests verify backward compatibility, note validation, duplicate note ID rejection, and state preservation on reload failure.
### 7.2 Reports
Reports summarize ticket data, including status, priority, category, unresolved work, affected users, and resolution percentage. A report should be derived from the actual ticket collection rather than hard-coded totals. Reports also need tests for empty input and invalid data so that they do not produce misleading results.
### 7.3 Understanding check
An understanding check provides questions that help assess whether I can explain important project concepts independently. The questions and answer-scoring logic should be testable without requiring a person to interact with the CLI.
Collecting explanations for later discussion is not the same as permanently saving those explanations. Unless persistence is explicitly implemented and verified, I should not claim that the explanations have been stored.
What I learned
A feature is not complete merely because it works on the normal path. I also need to consider invalid input, boundary values, repeated actions, and whether rejected actions leave the application state unchanged.
## 8. Current Verification Status
Verification date: 16 October 2026
Full test suite — latest verified run
I ran the complete test suite on the feat/campusflow-next-fixes branch after correcting the Open Work Queue regression.
Command:
python3 -m unittest discover -s tests -v
Actual output summary:
Ran 168 tests in 0.225s

OK
All 168 tests passed in this run. The test runner reported no failures or errors.
Open Work Queue regression test
I also ran the targeted regression test:
python3 -m unittest tests.test_cli.TestUnresolvedQueueCli -v
Actual output summary:
Ran 1 test in 0.002s

OK
This test verifies that the queue displays only open tickets, sorts them by priority and numeric ticket ID, and excludes tickets in other lifecycle states.
Storage tests
An earlier targeted storage-test run passed all four tests:
Ran 4 tests in 0.005s

OK
These tests covered older ticket records without notes, duplicate note IDs, invalid note messages, and preservation of in-memory data when reloading fails.
JSON validation
I previously ran:
python3 -m json.tool data/tickets.json > /dev/null && echo "Ticket JSON is valid"
Actual output:
Ticket JSON is valid
This confirms that the JSON file was syntactically valid when checked. It does not independently prove that every record satisfies the application's data rules.
Diff whitespace check
I previously ran:
git --no-pager diff --check
The command produced no output at that time. This was a check of the unstaged diff at that point. It does not establish that all staged and unstaged changes are currently free of whitespace errors. Both must be checked again during the final audit.
What these checks establish
The latest full test run passed all 168 discovered tests. The targeted queue regression test also passed, and the earlier storage-test and JSON-validation results are recorded with their actual outputs.
These results do not prove that every requirement has been independently reviewed or that the feature has been merged into main. The complete staged and unstaged diffs must still be reviewed, and the full test suite should be rerun if further code changes are made.
## 9. Git Workflow and Collaboration
I am using the existing CampusFlow repository and a feature branch for the current changes.
Current branch
feat/campusflow-next-fixes
Current working-tree situation
The latest recorded git status --short showed staged changes to the README, search module, storage module, understanding check, ticket data, learning log, CLI, and several test files. It also showed an unstaged modification to tests/test_storage.py and an untracked docs/baseline-check.md.
These files must be reviewed together. A staged version and a newer unstaged version of the same file can differ, so inspecting only the staged diff would not be sufficient. The working-tree status should be checked again because it may have changed since the last recorded inspection.
Planned workflow
1. Review all modified and newly created files.
2. Inspect the ticket-data diff to ensure existing records have not been unintentionally changed.
3. Review the baseline document and learning log for accuracy.
4. Run the full test suite again after the final edits.
5. Check whitespace in both staged and unstaged changes.
6. Stage only the intended files.
7. Inspect the complete staged diff before committing.
8. Commit the work on the feature branch.
9. Push the branch to GitHub.
10. Open a pull request targeting main.
11. Ask my new partner to review the actual code and tests.
12. Address review comments and obtain approval before merging.
13. Verify the integrated result after the approved merge.
Review integrity
I must not claim that my new partner has approved the pull request before that has actually happened. I should record the real PR URL, review comments, approval, and merge result when each event occurs.
What I can explain independently
- git status shows the current working-tree state.
- git diff displays unstaged changes.
- git diff --cached displays staged changes.
- git diff HEAD displays tracked changes relative to the current commit.
- git add stages selected changes.
- git commit records staged changes in the current branch.
- git push publishes branch commits to the remote repository.
- A pull request allows another engineer to review changes before they are merged.
## 10. Challenging and Verifying AI Suggestions
I use AI as a learning and debugging aid, not as a substitute for understanding the project.
Example: text matching
I ran a small experiment using "Straße" and "STRASSE". The output showed that lower() and casefold() can produce different comparison results.
Decision: Use the method that best fits the search requirements and verify its behaviour with tests.
Example: older ticket records
I inspected the storage logic and examined how setdefault() supplies an empty list for a missing notes field.
Decision: Preserve the compatibility behaviour while retaining validation for required fields.
Example: test design
I compared a test fixture that hides a bug with one that exposes it. The experiment demonstrated why choosing discriminating test inputs matters.
Decision: Design tests to distinguish the expected behaviour from plausible incorrect behaviour.
Example: Open Work Queue regression
I investigated why the Open Work Queue could include in_progress tickets. The previous condition excluded only resolved and closed statuses, rather than explicitly permitting only open tickets.
I added a regression test with several lifecycle states, confirmed that the targeted test passed after the correction, and reran the full test suite. The targeted test passed, and the full suite reported 168 passing tests.
Decision: Keep the explicit status == "open" filter and retain the regression test to guard against the same behaviour returning.
What I still need to improve in this record
These examples describe experiments and code analysis, but they do not yet provide a complete record of two independently documented AI learning cycles.
For each cycle, I should record:
1. Concept gap: What I did not understand before asking for help.
2. Question asked: The actual question, or a clearly labelled reconstruction if I cannot verify its exact wording.
3. AI guidance: A concise, accurate summary of the explanation or recommendation.
4. Independent experiment: A small experiment that tests the concept without simply repeating the full implementation.
5. Verification: The actual output, test result, or documentation that supports or contradicts the recommendation.
6. Final decision: What I accepted, modified, or rejected and why.
If a real AI suggestion proves incorrect, I should record the original suggestion, the evidence that contradicted it, and the resulting decision. I must not invent an incorrect suggestion merely to satisfy an assessment requirement.
## 11. Known Limitations and Outstanding Work
The following items must be verified before I describe the work as complete:
- Review the full diff for every modified and untracked file.
- Confirm that the original ticket workflow and queue requirements remain satisfied.
- Confirm that existing ticket data is preserved apart from intended compatibility changes.
- Review the baseline document against the original and independently verified baseline records.
- Strengthen the AI learning log with truthful, specific evidence of the required learning cycles.
- Review the bug-hunter tests separately to establish which tests demonstrate a reproduced defect and which test edge cases or existing behaviour. The Open Work Queue regression is now a documented, reproduced defect with a passing regression test.
- Rerun the full test suite after the final edits.
- Check both staged and unstaged diffs for whitespace errors.
- Inspect the final staged changes before committing.
- Push the feature branch and open the pull request.
- Obtain a genuine review and approval from my new partner.
- Record the actual pull request and merge details after they occur.
- Verify the final integrated result on main.
The recorded test result is evidence of a successful test run, not a substitute for the remaining code review and collaboration steps.
## 12. Final Reflection
Working on CampusFlow Next is helping me understand that reliable software requires more than writing functions that appear to work.
I need to understand the existing code, preserve important behaviour, validate data, test edge cases, and check how changes affect the rest of the application.
The experiments with text normalization, test fixtures, and JSON compatibility taught me to verify claims with observable evidence rather than accepting assumptions. The Open Work Queue regression also showed me why a condition that excludes known statuses can be weaker than one that explicitly allows only the required status. I tested the correction with a targeted regression test and then ran the full suite, which passed all 168 tests.
I am also learning that Git and pull requests are part of engineering quality. A feature should be isolated, tested, reviewed by another person, and merged only after the required checks and approval.
My next step is to finish reviewing the modified files and the staged and unstaged diffs, rerun the tests after any further edits, and ensure the learning log accurately reflects the evidence. I will then stage only the intended changes, review the final staged diff, and submit the feature branch for review by my new partner.
My goal is to be able to explain what I built, why I built it that way, how I tested it, and what evidence supports my conclusions.
