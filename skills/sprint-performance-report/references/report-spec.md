# Report Layout and Chart Specifications

## Document order

1. Report Scope (sprints/releases covered, snapshot vs. historical)
2. Executive Summary
3. Developer Performance Table
4. Developer Performance Chart
5. Team Performance Chart
6. Dev Velocity — table + two charts
7. QA Velocity — table + two charts
8. Total Team Velocity — table + two charts
9. Risks and Observations
10. Data-Quality Notes and Assumptions
11. Validation Summary

## Executive summary contents

Selected sprints/releases; Dev total, completed, incomplete points; QA total,
completed, incomplete points; overall completion %; sprint with highest and
lowest completion %; sprint with the largest scope increase; total carried-over
points; developer with the highest completed points; developer with the highest
completion % (only when their total assigned points are meaningful); number of
unassigned Tasks; number of issues with missing story points.

## Developer performance table

One column per developer, then Dev Total, QA Total, and Combined Total when
useful. Rows: Completed Points, Incomplete Points, Total Points, Completion %.

| Metric | Dev 1 | Dev 2 | Dev 3 | Dev Total | QA Total |
|---|---|---|---|---|---|
| Completed Points | 30 | 25 | 32 | 87 | 80 |
| Incomplete Points | 23 | 19 | 29 | 71 | 45 |
| Total Points | 53 | 44 | 61 | 158 | 125 |
| Completion % | 56.6% | 56.8% | 52.5% | 55.1% | 64.0% |

Dev values come only from Tasks; QA values only from User Stories; developer
columns (+ Unassigned) must sum to Dev Total.

## Velocity tables (one each for Dev, QA, Total Team)

| Sprint | Start | Scope Change | Total | Completed | Incomplete | Completion % | Carried Over |
|---|---|---|---|---|---|---|---|

Sprints as rows, chronological. Each section also gets a completion-rate column
(already in the table) and the two charts below. For the Total Team table verify
Dev + QA = Total per cell.

## Charts

Render charts as images (matplotlib is fine) and embed them in the document next
to their tables. Chart values must exactly match the table they accompany. Use
the colors from `config.md`, label axes, and keep the same Y-axis scale across
comparable Dev / QA / Total charts when practical.

1. **Developer Performance** — vertical stacked bars; X = developers (no Dev
   Total or QA Total bars); Y = story points; bottom segment Completed (green),
   top Incomplete (orange).
2. **Team Performance** — two stacked bars, Dev and QA; same segments/colors.
   Dev bar from Tasks, QA bar from User Stories.
3. **Scope Composition** (per velocity section) — X = sprint; bottom Start
   Points (blue), top Scope Change Points (orange).
4. **Delivery Outcome** (per velocity section) — X = sprint; bottom Completed
   (green), top Incomplete (gray or red).

Never combine Start, Scope Change, Completed, and Incomplete into one stacked
bar — they are two views of the same points (see `metrics.md` §3).

## Validation summary section

Close the report with a short section confirming the checks that were run:
pagination complete and count matched; only Task/User Story issues included;
filters applied; duplicates removed; no story points estimated; each issue
counted once per sprint/metric; historical status used (or snapshot labeled);
all identities from `metrics.md` §4 verified; charts match tables; sprint
columns chronological. Note anything that could not be verified and why.

## Data-quality notes

Always disclose: issues with missing/invalid story points (count), unassigned
Tasks (count and points), fallbacks used (status mapping, sprint-date order,
missing changelog), active-sprint snapshot labeling, and any exclusions.
