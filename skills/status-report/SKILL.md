---
name: status-report
description: >
  Generates a monthly status report Word document (.docx) by fetching JIRA issues for one or more projects and using AI to write project summaries and planned-tasks sections — following the standard status-report-template. Use this skill whenever the user asks to "create a status report",
  "generate monthly status", "write my status update", "make a status doc", or wants to produce a formatted Word report from JIRA data. Even if the user just says "status report" without
  mentioning JIRA or Word, use this skill — it handles the entire end-to-end workflow.
---

# Status Report Skill

Generates a polished monthly status report `.docx` for one or more JIRA projects.
The workflow is: **load cached issues from jira_issues → summarize per project → pass summary into generator → produce .docx**.

Cache behavior:
- First read issue JSON from `jira_issues/`
- If `jira_issues/` does not exist or contains no JSON files, trigger the `jira-fetch` skill automatically to generate cache files
- Then continue report generation using cached data

## Template

The output follows `assets/status-report-template.md`. Key structure per project:
- Issue table: Issue Type | Issue Key | Summary | Status
- Project Summary (~150 words, prose)
- Planned Tasks for Next Month (bulleted list)

## Scripts

| File | Purpose |
|---|---|
| `scripts/summarize.py` | Builds project summary and planned tasks from issue metadata |
| `scripts/generate.py` | Main entry point — orchestrates cache read (or trigger jira-fetch) → summarize → docx |

Run directly with:
```bash
python scripts/generate.py
```
Or set env vars to skip interactive prompts:
```bash
REPORT_AUTHOR="Yizhen Chen" REPORT_DATE="June 2026" JIRA_PROJECTS="CCDI Hub,CCDI Federation" \
  python scripts/generate.py
```

## Dependencies

- **jira-fetch skill** — `scripts/generate.py` imports `fetch_jira_issues` from `../jira-fetch/scripts/fetch.py`
- **python-docx** — `pip install python-docx`
- **env vars**: `JIRA_TOKEN`, `JIRA_URL`, `JIRA_JQL`, `JIRA_PROJECTS`

## Step-by-step workflow

### Step 1 — Gather inputs

Ask the user (via `AskUserQuestion` or inline) for:
1. **Author name** — appears in the report title (e.g., "Yizhen Chen")
2. **Report date** — month and year (e.g., "May 2026")
3. **Projects** — which JIRA projects to include (offer the full mapping list as options, allow multi-select). By default, use the `JIRA_PROJECTS` env var if set.

Set these as env vars or let `scripts/generate.py` prompt interactively.

the `JIRA_PROJECTS` env var are the arcornyms, you need to map them to the display names for the user prompt. 
Here are the mappings:
    "Index of NCI Studies":                  "INS",
    "CCDI CPI":                                "CPI",
    "Clinical and Translational Data Commons": "CTDC",
    "Population Science Data Commons":         "POPSCI",
    "CCDI cBioPortal":                         "cBioPortal",
    "NCI Data Sharing Hub":                    "NCI Data Sharing",
    "CCDI Federation datacentric":         "Datacentric-CCDI-DCC-Federation ",
    "CCDI Federation":                         "FEDERATION",

you should use the full name in the report. 

### Step 2 — Fetch issues (jira-fetch)

For each selected project, `generate.py` reads issue content from the local cache in `jira_issues/`.
If the cache is missing or empty, it automatically triggers `../jira-fetch/scripts/fetch.py` to pull issues from JIRA.

Each project produces a `project_result` dict containing:
- `display_name` — human-readable project name
- `total` — total issue count
- `issues` — list of issue dicts (issue_type, issue_key, summary, status, duedate, comments)

### Step 3 — Summarize (summarize.py)

`generate.py` passes each `project_result` (the full issue content from Step 2) into
`scripts/summarize.py → summarize_project(project_result)`.

`summarize_project` reads the issue content and returns:
- `summary` — prose paragraph (~150 words) describing completed, in-progress, and blocked work
- `planned_tasks` — list of 3–6 action items for next month derived from issue statuses

Both the issue content (`issues` list) and the summarization output (`summary`, `planned_tasks`)
are then assembled into a `project_data` payload:

```python
{
    "display_name": ...,
    "issues":       [...],   # raw issue rows → used for the issue table
    "summary":      "...",   # prose from summarize.py → Project Summary section
    "planned_tasks": [...],  # bullets from summarize.py → Planned Tasks section
}
```

### Step 4 — Generate .docx (generate.py)

`generate.py` receives each `project_data` payload and calls `_build_docx(author, report_date, projects_data)`.

For each project it renders:
1. Issue table (from `issues`)
2. Project Summary section (from `summary`)
3. Planned Tasks for Next Month section (from `planned_tasks`)

```bash
python scripts/generate.py
```

### Step 5 — Present the file

After saving, present the file to the user and give a one-sentence summary (e.g., "Status report for May 2026 covering 5 projects — 42 issues total.").
Generated filenames include a timestamp suffix in the format `YYYYMMDD_HHMMSS` to avoid overwriting earlier runs.

## Error handling

- Missing env vars → tell the user exactly which variable to set before proceeding
- Project fetch failure → log the error, skip that project, note it in the report footer
- Summarization failure → use a fallback: list the top 5 issue summaries as bullet points

## Example interaction

User: "Create my status report for May 2026"
→ Ask for author name and which projects
→ Fetch issues for each selected project
→ Summarize each project
→ Generate Status_Report_Chen_202605_20260706_203705.docx
→ Present file to user
