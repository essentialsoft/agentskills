# Metric Calculation Rules

All point metrics derive from a single per-issue classification. Get that right
once, and every table and chart follows from it.

## 1. Story points

- Use the configured Story Points field (`config.md`).
- Null, empty, invalid, or non-numeric values count as **zero** reportable
  points. Never estimate missing story points. Report the number of affected
  issues in the data-quality notes.
- Within one sprint and one metric, count each issue exactly once — an issue
  listing multiple sprint values must not contribute its points twice.

## 2. Completed vs. incomplete

Classify each issue per sprint using its status at that sprint's end (see
`jira-retrieval.md` §5):

- **Completed**: Status Category was Done at sprint end.
- **Incomplete**: anything else.

Multi-sprint carryover: when an issue belongs to the report sprint *and* a later
sprint, it is incomplete for the earlier sprint (it wasn't done by that sprint's
end) and is classified in the later sprint by its status at the later sprint's
end. Example: an issue on Sprint 25 and Sprint 26, unfinished at Sprint 25's end,
is incomplete for Sprint 25; if it was completed by the end of Sprint 26 it is
completed for Sprint 26.

## 3. Start, scope change, and carryover

These describe **when work entered the sprint**. They partition the same story
points as completed/incomplete — never stack all four in one bar or sum them into
one total, because that double-counts.

- **Start Points**: issues already assigned to the sprint at the sprint start
  date (from the changelog when available).
- **Scope Change Points**: issues added after sprint start and on or before
  sprint end.
- **Carried-Over Points**: issues associated with an earlier sprint that entered
  this sprint incomplete. Carryover is a *subset* of start or scope-change
  points, depending on when the issue entered — it is an annotation, not a third
  additive bucket.

## 4. Validation identities

Verify for every sprint, and for every grouping (per developer, Dev, QA, total):

```
Start Points + Scope Change Points = Total Committed Points
Completed Points + Incomplete Points = Total Committed Points
Completion % = Completed / Total × 100   (one decimal; N/A when Total = 0)
```

And across groupings:

```
Sum of individual developers (+ Unassigned) = Dev Total
Dev Total  = sum of Task story points
QA Total   = sum of User Story story points
Dev + QA   = Combined / Total Team value, per sprint and per metric
```

If any identity fails, fix the classification before writing the report — do not
publish and footnote the discrepancy.

## 5. Dev attribution (Tasks only)

- Dev performance uses **Task** issues only.
- Attribute by the configured Developer field, using the account identifiers
  Jira actually returns. Include the developers requested for this report
  (default roster in `config.md`).
- Tasks with no Developer value: exclude from individual columns, include in the
  Dev Team total under **Unassigned** (or reported separately), and disclose the
  affected points and issue count.

Example JQL shape:

```
sprint = <Sprint ID> AND issuetype = Task AND "Developer" IN (mattuak, vegaa3, ...)
```

(Use the field syntax the instance supports; when in doubt retrieve all Tasks in
scope and attribute locally from the Developer field — that also captures
unassigned Tasks, which a JQL `IN` filter would drop.)

## 6. QA metrics (User Stories only)

- QA performance uses **User Story** issues only.
- QA values are sprint-level totals; do not attribute them to individuals unless
  the user explicitly asks for a QA-owner breakdown *and* a suitable field
  exists.

## 7. Interpreting results

Never judge an individual on completion percentage alone — consider assigned
workload, scope changes pushed onto them mid-sprint, carryover, and missing
data. Surface unusual patterns as observations, not verdicts.
