# CampusFlow Next — Baseline Check

## 1. Purpose

This document combines the CampusFlow Next feature checklist with the historical baseline record. Historical results are not evidence that the current merged code passes.

## 2. Historical baseline results

The original baseline document recorded a run using:

    python3 -m unittest discover -s test -v

Recorded result: 99 tests in 0.090s, OK. The command used `test` although the repository contains a `tests/` directory, so this is retained only as a historical record.

The baseline parent commit was `f6c4d1fd85d7d63c0b5565b0eb11db77d0fbbcb6`. A separate worktree was tested with:

    python3 -m unittest discover -s tests -v

Verified historical result: 112 tests in 0.029s, OK. This result applies to that baseline commit, not the current merge.

## 3. CampusFlow Next feature verification

The original feature checklist records these items as implemented. Recheck them against the final integrated project before submission.

- [x] Search tickets by title.
- [x] Combine title, category, status, and priority filters.
- [x] Generate reports and handle an empty ticket list.
- [x] Add ticket notes through the CLI.
- [x] View ticket notes through the CLI.
- [x] Persist notes through JSON storage reloads.
- [x] Provide a six-question Engineering Understanding Check.
- [x] Accept only A/B/C/D quiz answers and retry invalid input.
- [x] Calculate a score out of six.
- [x] Save explanations for at least two quiz answers for mentor discussion.

## 4. Automated tests to run

From the project root, run:

    python3 -m unittest discover -s tests -v

A development note recorded 114 tests during development. Confirm the actual result on the final integrated code before submission; do not treat that note as a current test result.

## 5. Manual checks still required

- [ ] Run the CLI and verify the search, add-note, view-notes, and understanding-check menu options.
- [ ] Test invalid quiz input and confirm the program retries.
- [ ] Complete the quiz and verify that explanations are saved as expected.
- [ ] Run the complete test suite again before submitting the pull request.
- [ ] Verify the integrated project on the intended repository after partner review and merge.

## 6. Historical baseline observations

The original baseline record reported that valid tickets could be created and their priority calculated, invalid affected-user values were rejected, and ticket assignment and workflow status changes were supported. These are historical observations, not newly performed manual tests for this merge.

## 7. Improvements identified

- Add follow-up notes to tickets.
- Validate note authors and messages.
- Generate note IDs independently for each ticket.
- Prevent notes from being added to resolved tickets.
- Validate persisted JSON before replacing in-memory ticket data.
- Reject duplicate or malformed ticket and note data during loading.
- Preserve data when saving fails.
- Preserve ticket and note ID continuity after saving and reloading.
- Keep existing CampusFlow behaviour working while adding features.

## 8. Evidence and limitations

The repository-root `baseline-check.md` remains a separate file. This is the assessment copy under `docs/baseline-check.md`.

The 99-test result and baseline observations are historical records. The 112-test result was independently verified at the baseline parent commit in a separate worktree. Neither historical result replaces a fresh test run on the final integrated code.
