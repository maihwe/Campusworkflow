
# CampusFlow Next — Baseline Check

## 1. Purpose

This document records the original CampusFlow baseline, historical test evidence, and verification tasks for CampusFlow Next.

The original baseline document was committed in Git commit `1a0166e` on 15 October 2026. It is preserved at the repository root as `baseline-check.md`.

## 2. Historical Baseline Test Record

The original baseline document recorded this command:

```bash
python3 -m unittest discover -s test -v
```

Recorded result:

```text
Ran 99 test in 0.090s

OK
```

The historical command uses `test`, while the repository contains a `tests/` directory. This result is preserved as recorded and is not presented as independently verified evidence.

## 3. Independently Verified Baseline

The baseline parent commit was:

`f6c4d1fd85d7d63c0b5565b0eb11db77d0fbbcb6`

The original code at this commit was tested in a separate Git worktree using:

```bash
python3 -m unittest discover -s tests -v
```

Verified historical result:

```text
Ran 112 tests in 0.029s

OK
```

This result applies to the baseline parent commit, not the final CampusFlow Next integration.

## 4. Baseline Inputs and Observations

### Valid ticket creation

The original baseline record reported that valid tickets could be created and their priority calculated.

### Invalid affected-user values

The original baseline record reported that invalid affected-user values were rejected. This observation was not independently reproduced during the test run in Section 3.

### Ticket workflow

The original baseline record reported support for ticket assignment and workflow status changes. This is a historical observation, not a newly performed manual test.

## 5. CampusFlow Next Feature Verification Plan

Complete each item only after testing the behaviour on the integrated version.

- [ ] Search tickets by title using case-insensitive substring matching.
- [ ] Combine title, category, status, priority, and assignee filters.
- [ ] Verify combined filters return tickets matching all supplied filters.
- [ ] View search results sorted by priority and numeric ticket ID.
- [ ] Confirm the open work queue lists only open tickets.
- [ ] Generate reports with status, priority, and category counts.
- [ ] Verify unresolved/resolved counts and resolution percentage, including an empty ticket list.
- [ ] Add and view ticket notes through the CLI.
- [ ] Verify note persistence after JSON storage reloads.
- [ ] Verify notes cannot be added to resolved or closed tickets.
- [ ] Verify invalid quiz answers are rejected and the user is prompted again.
- [ ] Verify the six-question Engineering Understanding Check.
- [ ] Verify quiz scoring is out of six.
- [ ] Verify explanations for at least two answers are saved for discussion.

## 6. Automated Test Verification

Run the complete test suite from the project root:

```bash
python3 -m unittest discover -s tests -v
```

Record the actual result from the final integrated version:

- Test command: `python3 -m unittest discover -s tests -v`
- Number of tests run: To be recorded after execution.
- Result: To be recorded after execution.

Do not substitute historical test counts for the result of the final integrated version.

## 7. Historical Feature Verification Record

An earlier integration record reported these features as implemented:

- Ticket search and combined filtering.
- Priority-sorted search results.
- Reports with status, priority, and category counts.
- Unresolved/resolved counts and resolution percentage.
- CLI support for adding and viewing ticket notes.
- JSON persistence of ticket notes.
- A six-question Engineering Understanding Check.
- Quiz answer validation and explanation collection.

An earlier integration record also reported **163 tests passing**, including a fresh-clone run. This is historical evidence only; it does not establish that the current conflict-resolution branch passes.

## 8. Manual Checks Still Required

- [ ] Run the CLI and verify the actual menu options and their behaviour.
- [ ] Test invalid quiz input and confirm the program retries.
- [ ] Complete the quiz and verify the explanation file is written correctly.
- [ ] Run the complete test suite after resolving all conflicts.
- [ ] Review the final changes before submitting the pull request.
- [ ] Verify the integrated project on the intended repository.

## 9. Improvements and Reliability Requirements

The baseline review identified these areas for implementation or stronger verification:

- Add follow-up notes to tickets.
- Validate note authors and messages.
- Generate note IDs independently for each ticket.
- Prevent notes from being added to resolved tickets.
- Validate persisted JSON before replacing in-memory data.
- Reject duplicate or malformed ticket and note data during loading.
- Preserve in-memory data when saving fails.
- Preserve ticket and note ID continuity after saving and reloading.
- Add combined search, filtering, richer reports, and the understanding check.
- Preserve existing CampusFlow behaviour while introducing new features.

## 10. Evidence and Limitations

The 99-test result and baseline observations were retained from the original historical document. The 112-test result was independently verified at the baseline parent commit in a separate Git worktree.

The 163-test result was reported in an earlier integration record. Neither historical test count proves that the current merge-resolution branch passes.

The checklist in this document is a verification plan. Do not mark items complete until the corresponding behaviour has been tested on the integrated code.
