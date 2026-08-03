---
name: jira-fetch
description: >
  Fetches JIRA issues for one or more projects and returns structured data ready for report generation.
  Use this skill whenever you need to pull issues from JIRA — whether as a standalone lookup or
  as the data-fetching step inside status-report or milestone-report workflows. Triggers on any
  request to "get JIRA issues", "fetch tickets", "pull JIRA data for [project]", or when another
  skill needs raw JIRA issue data.
---

# JIRA Fetch Skill

This skill fetches issues from the NCI JIRA instance and returns
clean, structured data. It is designed to be called by other skills (status-report,
milestone-report) or standalone when the user wants to inspect raw issue data.

## Required environment variables

These must be set in the user's `.env` file (or shell environment):

| Variable | Description | Example |
|---|---|---|
| `JIRA_TOKEN` | Bearer token for JIRA API auth | `eyJ...` |
| `JIRA_URL` | Base URL of the JIRA instance | `https://tracker.nci.nih.gov` |
| `JIRA_JQL` | Additional JQL filter appended to every query | `AND updated >= -30d ORDER BY updated DESC` |
| `JIRA_PROJECTS` | Comma-separated list of JIRA project keys to fetch | `INS,CPI,CTDC,POPSCI,CBIO,DATASHARE,FEDERATION` |

If '.env' variables are missing, the skill will raise a clear error indicating which variable(s) need to be set. and create a `.env` file template if it doesn't exist.

## clean output folder
The skill saves output JSON files to a `jira_issues/` folder. To avoid confusion from old files, it automatically deletes any existing JSON files in that folder before saving new results. 

## Python environment

This skill requires Python 3.8+ and the `requests` library. if python virtual environemnt venv is not set up,

create a virtual environment and install dependencies with:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r ./requirements.txt
```



## How to run

use ther shell command to run the skill for a specific project, before run the shell command make sure you have virtual environment activated and dependencies installed:

```bash
python3 ./.agents/skills/jira-fetch/scripts/fetch.py 

```

## Output structure

```json
{
  "project_name": "CCDI Hub",
  "display_name": "CCDI Portal (aka CCDI Hub)",
  "total": 14,
  "issues": [
    {
      "issue_type": "Story",
      "issue_key": "CCDH-123",
      "summary": "Implement search filter on portal homepage",
      "status": "Done",
      "priority": "High",
      "created": "2026-04-01",
      "updated": "2026-05-10",
      "duedate": "2026-05-15",
      "comments": [
        {
          "author": "Jane Smith",
          "date": "2026-05-09",
          "body": "PR merged, deployed to staging. QA sign-off received."
        }
      ]
    }
  ]
}
```

## How downstream skills should use comments

Comments are the richest signal for understanding actual ticket progress — use them in AI prompts alongside the standard fields.

- **status-report**: include the most recent comment body when formatting issues for the summary prompt, so Claude can reflect actual progress rather than just the JIRA status label.
- **milestone-report**: use comments to identify real delivery dates (e.g., "deployed on 2026-05-10"), blockers, or completion notes that aren't captured in `duedate` or `status` alone.

When formatting issues for an AI prompt in a downstream skill, append comments like this:

```
Key: CCDH-123 | Type: Story | Status: Done | Due: 2026-05-15
Summary: Implement search filter on portal homepage
Latest comment (Jane Smith, 2026-05-09): PR merged, deployed to staging. QA sign-off received.
```
```

## Error handling

- If `JIRA_TOKEN` is missing or invalid → raise a clear `ValueError` telling the user which env var to set.
- If the API returns a non-200 status → print the status code and response body, then raise.
- If a project returns 0 issues → return the structure with an empty `issues` list and `total: 0`; do **not** error.

## Standalone usage

When called by the user directly (not from another skill), print the results as a formatted
table to the console and also save a `jira_issues_{project_name}_{date}.json` file to the
current working directory.
