---
name: bug-metrics-report
description: Generate a validated bug metrics report for the CRDCDH Jira project — New Bugs Created by Sprint, and Closed Bugs by Root Cause and Sprint — each as a table plus chart, delivered as a Word document. Use this whenever the user asks for a bug report, bug metrics, bug trends, new/created bugs per sprint, closed bugs, defect counts, root-cause analysis or breakdown for CRDCDH — even phrasings like "how many bugs came in last sprint" or "what's driving our defects". Requires the mcp-atlassian (Jira) connector.
---

# Bug Metrics Report (CRDCDH)

Produce two bug metrics from Jira, each presented as a table and a chart:

1. **New Bugs Created by Sprint** — how many bugs were *reported* during each
   sprint's date window.
2. **Closed Bugs by Root Cause and Sprint** — what closed, and why.

## Files in this skill

- `references/config.md` — project key, custom field IDs (Root Cause, Sprint),
  colors, output conventions. **Read first, every run.** If a needed value is
  missing there, ask the user at runtime.
- `references/jira-retrieval.md` — scope confirmation, pagination, sprint
  normalization, historical status, error handling. Read before querying Jira.
- `references/report-spec.md` — document order, table layouts, chart specs.
  Read before writing the deliverable.

## Workflow

1. **Confirm scope.** Sprints and/or releases; sprint is the primary dimension.
   If unspecified, ask: *"Which release(s) or sprint(s) should I include in the
   bug report?"* Do not query Jira until scope is clear.

2. **Load config**, then **retrieve** per `references/jira-retrieval.md`:
   **Bug** issues only, both open and closed, all pagination pages, deduped by
   issue key. Fields: key, summary, created date, status, status category,
   resolution, resolution date, root cause, sprint, fix version; plus sprint
   metadata (IDs, names, states, start/end/completion dates).

   Because Metric 1 counts bugs by *creation date* regardless of sprint
   assignment, a sprint-field query alone can miss bugs created during a sprint
   window but never assigned to it. Also query bugs by created-date range
   spanning the selected sprint windows (`project = <key> AND issuetype = Bug
   AND created >= <earliest start> AND created < <latest end>`), merge, and
   dedupe. Disclose this in the notes.

3. **Compute Metric 1 — New Bugs by Sprint.** A bug is a New Bug for the sprint
   whose window contains its created date: `sprint start <= created < sprint
   end`. The bug's current status and its assigned Sprint field are irrelevant.
   Each bug counts once. Bugs whose created date falls in no selected sprint's
   window are excluded — count them in the data-quality notes. If sprint dates
   are unavailable for a sprint, exclude the affected bugs from this metric,
   report how many, and never guess the window.

   *Example: Sprint 4 runs Mar 21–Apr 7, Sprint 5 runs Apr 7–Apr 28. A bug
   created Mar 22 and closed Apr 10 is a New Bug in Sprint 4 — and a Closed Bug
   in Sprint 5.*

4. **Compute Metric 2 — Closed Bugs by Root Cause and Sprint.** Include only
   bugs in scope that are **closed** (status = Closed at the reporting point;
   use the config's status fallback if needed and disclose it). Count each
   closed bug once, under the sprint whose date window contains its resolution
   date (as in the example above). When resolution dates or sprint dates are
   unavailable, fall back to the bug's assigned sprint — latest by end date,
   then completion date, then active-over-closed, then highest sprint ID — and
   disclose the fallback. Bugs with no valid sprint in scope are excluded and
   counted in the notes.

   Root cause comes from the configured Root Cause field. Null, empty, or
   whitespace-only values become **Root Cause Not Provided**. Never create a
   "Not Resolved" category — this metric contains only closed bugs.

5. **Validate before writing.**
   - Retrieval: all pages fetched, count matches Jira's total, Bugs only,
     filters applied, duplicates removed.
   - Metric 1: every counted bug's created date falls inside its sprint window;
     root cause plays no role; sprint counts sum to the Total; chart matches
     table.
   - Metric 2: only closed bugs; every bug has a root-cause category; each bug
     counted once under exactly one sprint; row totals and column totals both
     sum to the same grand total; chart bar heights match column totals.

6. **Build the deliverable** per `references/report-spec.md`. Default is a Word
   document: read the **docx** skill and follow it; charts as embedded images.
   If the user asks for slides, use the **pptx** skill instead. Deliver the
   file when done.

7. **Disclose** exclusions, fallbacks, and assumptions in the data-quality
   notes; keep the executive summary factual — never infer team or developer
   performance from bug counts alone.

## Non-negotiables

- Never build a report from a single pagination page; never present partial
  data as complete.
- Each bug counts once per metric — the two metrics may legitimately place the
  same bug in different sprints (created in one, closed in another).
- New-bug counting ignores status and sprint assignment; closed-bug counting
  ignores creation date.
- No "Not Resolved" row or segment anywhere in Metric 2.
- Distinguish clearly between new-bug counts and closed-bug root-cause counts;
  state assumptions and limitations; keep the tone professional and direct.
