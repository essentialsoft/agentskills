---
name: sprint-performance-report
description: Generate a validated Sprint Performance Report for the CRDCDH Jira project — individual developer performance, Dev vs. QA team performance, velocity trends by sprint, scope changes, carryover, and completion rates, delivered as a Word document with tables and charts. Use this whenever the user asks for a sprint report, sprint performance, developer performance, team velocity, sprint metrics, completion rates, scope-change analysis, or a sprint retrospective data pack for CRDCDH — even if they just say "how did sprint 25 go" or "pull the numbers for the last release". The `mcp-atlassian` MCP is the authoritative Jira data source for this report; do not use the Jira script or direct API calls as the source of truth.
---

# Sprint Performance Report (CRDCDH)

Produce a sprint performance report from Jira covering developer performance, Dev
and QA team performance, velocity trends, scope changes, and completion rates —
with every number validated before it is presented.

## Files in this skill

- `references/config.md` — project key, custom field IDs, developer roster,
  status fallback list, colors, output conventions. **Read first, every run.**
  If a needed value is missing there, ask the user at runtime.
- `references/jira-retrieval.md` — scope confirmation, JQL, pagination,
  sprint normalization, historical-status rules, error handling. Read before
  querying Jira.
- `references/metrics.md` — the calculation rules and validation identities.
  Read before computing anything.
- `references/report-spec.md` — document order, table layouts, chart specs.
  Read before writing the deliverable.

## Workflow

1. **Confirm scope.** One or more sprints and/or releases; sprint is the
   primary dimension. If the user hasn't specified, ask: *"Which release(s) or
   sprint(s) should I include in the Sprint Performance Report?"* Do not query
   Jira until scope is clear.  You need to get all the valid sprints and releases 
   from JIRA, and confirm with the user which ones to include in the report. 
   If user give invalid sprints or releases, ask them to clarify. If user doesn't specify, 
   you can suggest the last 3 sprints or the last release. Retry three times if 
   the user doesn't provide valid input, abort the operation.

2. **Load config** (`references/config.md`).

3. **Retrieve** (`references/jira-retrieval.md`). Use the `mcp-atlassian` MCP
   as the authoritative Jira data source for **Task** issues (Dev metrics) and
   **User Story** issues (QA metrics) in scope — both completed and
   incomplete. Do not use the Jira script or any direct Jira API call as the
   report's source of truth. Fields per issue: key, summary, issue type,
   created date, status, status category, resolution, resolution date, story
   points, developer, sprint, fix version; plus sprint metadata and changelog
   history (needed for sprint-end status, when issues entered the sprint, and
   carryover). Retrieve **all pagination pages**, confirm the count against
   Jira's total, and dedupe by issue key.

  

4. **Classify and compute** (`references/metrics.md`). For each issue × sprint:
   completed/incomplete at sprint end; start vs. scope-change entry; carryover.
   Then aggregate per developer (Tasks), per team (Dev = Tasks, QA = User
   Stories), and per sprint for the three velocity sections.

5. **Validate before writing.** Check every identity in `metrics.md` §4. A
   report with numbers that don't reconcile is worse than a late report — fix
   the classification, don't footnote the mismatch.

6. **Build the deliverable** (`references/report-spec.md`). Default is a Word
   document: read the **docx** skill and follow it; render charts as images and
   embed them beside their tables. If the user asked for slides, use the
   **pptx** skill instead, one report section per slide or slide group. Deliver
   the file to the user when done.

7. **Disclose.** End with risks/observations, data-quality notes (missing
   story points, unassigned tasks, fallbacks used, snapshot labeling), and the
   validation summary.

## Non-negotiables

- Never build a report from a single pagination page.
- Never estimate missing story points.
- Historical sprints are judged by status **at sprint end** (changelog), not
  current status; active sprints are labeled snapshots.
- Start/Scope-Change and Completed/Incomplete are two views of the same points —
  validate both partitions, never stack all four together.
- Dev metrics from Tasks only; QA metrics from User Stories only.
- Present partial or unvalidated data only with an explicit "incomplete" label.
- Be professional, concise, and direct; separate Dev, QA, and combined results
  clearly; state assumptions and limitations; don't judge individuals on
  completion percentage alone.
