
# CampusFlow Next — Baseline Check

## 1. Purpose

This document preserves the historical CampusFlow baseline record and provides a verification checklist for CampusFlow Next.

Historical test results and implementation notes are retained for reference. They do not prove that the current conflict-resolution branch or final integrated code passes.

## 2. Historical Baseline Test Record

The original baseline document recorded the following command:

```bash
python3 -m unittest discover -s test -v
```

Recorded result: 99 tests in 0.090s, OK.

The command used `test`, while the repository contains a `tests/` directory. This result is preserved as a historical record and has not been independently verified here.

The baseline parent commit was:

`f6c4d1fd85d7d63c0b5565b0eb11db77d0fbbcb6`

A separate worktree was tested using:

```bash
python3 -m unittest discover -s tests -v
```

The recorded historical result was 112 tests in 0.029s, OK. This result applies to that baseline parent commit, not the current merge.

A later development note recorded 114 tests. An earlier integration record also reported 163 tests passing, including a fresh-clone run. These counts are historical evidence only and must not be presented as the result of a new test run.

The original baseline document was recorded as committed in Git commit `1a0166e` on 15 October 2026 and preserved at the repository root as `baseline-check.md`.

## 3. Historical Baseline Observations

The original baseline record reported that:

- Valid tickets could be created and their priority calculated.
- Invalid affected-user values were rejected.
- Ticket assignment was supported.
- Workflow status changes were supported.

These are historical observations, not newly performed manual tests for this merge.

## 4. CampusFlow Next Feature Verification Plan

The following features must be checked against the final integrated project:

- [ ] Search tickets by title using case-insensitive substring matching.
- [ ] Combine title, category, status, priority, and assignee filters.
- [ ] Confirm combined filters return tickets matching all supplied filters.
- [ ] Verify search results are sorted by priority and numeric ticket ID.
- [ ] Confirm the open work queue lists only open tickets.
- [ ] Generate reports with status, priority, and category counts.
- [ ] Verify unresolved and resolved counts and resolution percentage.
- [ ] Verify reports handle an empty ticket list correctly.
- [ ] Add ticket notes through the CLI.
- [ ] View ticket notes through the CLI.
- [ ] Verify notes persist after JSON storage is reloaded.
- [ ] Verify notes cannot be added to resolved or closed tickets.
- [ ] Verify the six-question Engineering Understanding Check.
- [ ] Accept only A/B/C/D quiz answers and retry invalid input.
- [ ] Verify the quiz score is calculated out of six.
- [ ] Verify explanations for at least two quiz answers are saved for mentor discussion.

Do not mark an item complete until the behaviour has been checked on the integrated code.

## 5. Automated Test Verification

From the project root, run the complete test suite:

```bash
python3 -m unittest discover -s tests -v
```

Record the actual result from the final integrated version:

- Test command: `python3 -m unittest discover -s tests -v`
- Number of tests run: To be recorded after execution.
- Result: To be recorded after execution.

Do not substitute a historical test count for the actual result of the final integrated version.

## 6. Manual Checks Still Required

- [ ] Run the CLI and verify the search, add-note, view-notes, and understanding-check menu options.
- [ ] Test invalid quiz input and confirm the program retries.
- [ ] Complete the quiz and verify explanations are saved as expected.
- [ ] Run the complete test suite after resolving all conflicts.
- [ ] Review the final changes before submitting the pull request.
- [ ] Verify the integrated project in the intended repository.

## 7. Reliability Requirements

The baseline review identified the following behaviours to implement or verify:

- Add follow-up notes to tickets.
- Validate note authors and messages.
- Generate note IDs independently for each ticket.
- Prevent notes from being added to resolved or closed tickets.
- Validate persisted JSON before replacing in-memory ticket data.
- Reject duplicate or malformed ticket and note data during loading.
- Preserve in-memory data when saving fails.
- Preserve ticket and note ID continuity after saving and reloading.
- Add combined search, filtering, richer reports, and the understanding check.
- Preserve existing CampusFlow behaviour while introducing new features.

## 8. Evidence and Limitations

The repository-root `baseline-check.md` is a separate file from this assessment document at `docs/baseline-check.md`.

The historical results of 99, 112, 114, and 163 tests refer to earlier records. They do not establish that the current conflict-resolution branch passes.

This document is a verification plan and historical record. The final integrated code must be tested independently before submission.
