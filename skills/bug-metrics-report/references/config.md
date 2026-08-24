# Project Configuration — CRDCDH

This file holds every project-specific value the report depends on. Read it at the
start of every run. If a value needed for the current request is missing, empty, or
looks stale (for example, Jira rejects a field ID), ask the user for the correct
value at runtime instead of guessing — then suggest they update this file.

## Jira project

| Setting | Value |
|---|---|
| Project key | `CRDCDH` |
| MCP server | `mcp-atlassian` |

## Custom field IDs

| Meaning | Field ID | Used for |
|---|---|---|
| Story Points | `customfield_10042` | All point metrics |
| Developer | `customfield_23650` | Dev attribution (Tasks) |
| Sprint | `customfield_11650` | Sprint assignment + metadata |
| Root Cause | `customfield_22650` | Closed-bug root cause metric |

Field IDs vary per Jira instance. If a query returns no values for one of these
fields, verify the ID against the instance (e.g., search the field list via the MCP)
before concluding the data is missing.

## Issue types

| Audience | Issue type |
|---|---|
| Dev metrics | `Task` |
| QA metrics | `User Story` |
| Bug metrics | `Bug` |

## Developer roster

Default developers for individual Dev-performance columns (Jira usernames):

- mattuak
- vegaa3
- yoos4
- muelleras
- yingm3
- wangf6

Use the actual account identifiers Jira returns; the user may add or remove
developers for a given report. Tasks whose Developer field matches nobody on the
roster still count toward Dev Team totals (report them under their own name or
"Unassigned" as appropriate).

## Completion status fallback

When Status Category is unavailable, treat these statuses (case-insensitive) as
completed: `Closed`, `Resolved`, `Done`, `Completed`, `Verified`. All other
statuses are incomplete. Disclose whenever this fallback mapping was used.

## Chart colors

| Series | Color |
|---|---|
| Completed Points | Green `#2E7D32` |
| Incomplete Points (performance charts) | Orange `#EF6C00` |
| Incomplete Points (delivery outcome charts) | Gray `#757575` |
| Start Points | Blue `#1565C0` |
| Scope Change Points | Orange `#EF6C00` |
| New Bugs | Blue `#1565C0` |
| Root-cause segments | One distinct color per category; "Root Cause Not Provided" in gray |

## Output conventions

- Default deliverable: Word document (`.docx`). If the user asks for slides, build
  a PowerPoint (`.pptx`) instead with one section per report chapter.
- Round completion percentages to one decimal place.
- When Total Points is zero, show Completion % as `N/A` and say so in the notes.
- Order sprint columns chronologically (by start date, then end date).
