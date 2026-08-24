# Bug Report Layout and Chart Specifications

## Document order

1. Report Scope
2. Executive Summary
3. New Bugs by Sprint — table
4. New Bugs by Sprint — chart
5. Closed Bugs by Root Cause and Sprint — table
6. Closed Bugs by Root Cause and Sprint — chart
7. Data-Quality Notes and Assumptions

## Executive summary contents

Total new bugs; sprint with the highest new-bug count; total closed bugs; sprint
with the highest closed-bug count; most common root cause among closed bugs;
number of closed bugs with no root cause; number of bugs excluded for missing or
invalid sprint data; any additional exclusions caused by missing sprint dates.
Do not infer team or developer performance from bug counts alone.

## Metric 1 table — New Bugs by Sprint

One row (New Bug Count), one column per selected sprint in chronological order
(by sprint start date), one final Total column. The Total must equal the sum of
the sprint values.

| Metric | Sprint 3 | Sprint 4 | Sprint 5 | Total |
|---|---|---|---|---|
| New Bug Count | 12 | 18 | 9 | 39 |

## Metric 1 chart

Vertical bar chart. Title: **New Bugs by Sprint**. X = sprint, Y = new bug
count, one bar per sprint, one series. Do not chart the Total column. Values
must exactly match the table.

## Metric 2 table — Closed Bugs by Root Cause and Sprint

Group closed bugs by Root Cause × Sprint. One row per root cause, one column per
sprint, a final Total column and a final Total row, zeroes for empty
combinations. Sort sprint columns chronologically by sprint end date; sort root
cause rows alphabetically with **Root Cause Not Provided** last, immediately
before the Total row. Never include a "Not Resolved" category.

| Root Cause | Sprint 3 | Sprint 4 | Sprint 5 | Total |
|---|---|---|---|---|
| Code Defect | 8 | 14 | 10 | 32 |
| Configuration Issue | 3 | 5 | 2 | 10 |
| Requirements Gap | 4 | 6 | 3 | 13 |
| Root Cause Not Provided | 1 | 0 | 2 | 3 |
| **Total** | 16 | 25 | 17 | 58 |

## Metric 2 chart

Vertical stacked bar chart. Title: **Closed Bugs by Root Cause and Sprint**.
X = sprint, Y = closed bug count, one bar per sprint, one segment per root
cause, legend listing the root-cause categories. Each bar's total height must
equal the sprint's Total in the table.

## Chart rendering

Render charts as images (matplotlib is fine) using the colors in `config.md`,
embed each beside its table, label axes, and never chart fabricated values —
when a scope has no bugs, show the zero-value table and say so instead.
