"""
jira-fetch/scripts/fetch.py

Fetches JIRA issues (including recent comments) for a single project.

Usage:
    python fetch.py "<Project Name>" [extra_jql]
    python fetch.py
    python fetch.py "<JIRA_URL>" "<Project Name>" [extra_jql]

Output:
    Prints a summary table to stdout and saves jira_issues_<project>_<date>.json
    in the current working directory.

Environment variables required:
    JIRA_TOKEN  — Bearer token for JIRA API auth
    JIRA_URL    — Base URL of the JIRA instance (default: https://tracker.nci.nih.gov)
    JIRA_JQL    — Additional JQL filter appended to every query
    JIRA_PROJECTS — Optional comma-separated project list used when no CLI project is provided
"""

import os
import sys
import json
import requests
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_URL   = os.getenv("JIRA_URL", "https://tracker.nci.nih.gov")
JIRA_JQL   = os.getenv("JIRA_JQL", "")
JIRA_PROJECTS = os.getenv("JIRA_PROJECTS", "")

DEFAULT_JIRA_PROJECT_NAME_MAPPING = {
    "Index of NCI Studies":                   "INS",
    "CCDI CPI":                                "CPI",
    "Clinical and Translational Data Commons": "CTDC",
    "Population Science Data Commons":         "POPSCI",
    "CCDI cBioPortal":                         "cBioPortal",
    "NCI Data Sharing Hub":                    "NCI Data Sharing",
    "CCDI Federation datacentric":         "Datacentric-CCDI-DCC-Federation ",
    "CCDI Federation":                         "FEDERATION",
    # "CCDI Hub":                                "CCDI Portal (aka CCDI Hub)",
    # "CCDI C3DC":                               "C3DC",
    
}

REPO_ROOT = Path(__file__).resolve().parents[4]
PROJECT_MAPPINGS_FILE = REPO_ROOT / "project_mappings.json"


def _load_project_name_mapping() -> tuple[dict[str, str], dict[str, str]]:
    """Load project mappings from project_mappings.json.

    Returns:
        (display_to_fetch_identifier, identifier_to_display)
    """
    if not PROJECT_MAPPINGS_FILE.exists():
        fallback_reverse = {
            fetch_identifier.strip(): display_name
            for display_name, fetch_identifier in DEFAULT_JIRA_PROJECT_NAME_MAPPING.items()
            if fetch_identifier.strip()
        }
        fallback_reverse.update({name: name for name in DEFAULT_JIRA_PROJECT_NAME_MAPPING})
        return DEFAULT_JIRA_PROJECT_NAME_MAPPING.copy(), fallback_reverse

    with PROJECT_MAPPINGS_FILE.open("r", encoding="utf-8") as fh:
        entries = json.load(fh)

    display_to_fetch_identifier: dict[str, str] = {}
    identifier_to_display: dict[str, str] = {}

    for entry in entries:
        display_name = str(entry.get("display_name") or "").strip()
        if not display_name:
            continue

        fetch_identifier = str(entry.get("fetch_identifier") or display_name).strip()
        if not fetch_identifier:
            fetch_identifier = display_name

        display_to_fetch_identifier[display_name] = fetch_identifier

        identifier_to_display[display_name] = display_name
        identifier_to_display[fetch_identifier] = display_name
        for identifier in entry.get("identifiers", []):
            cleaned = str(identifier).strip()
            if cleaned:
                identifier_to_display[cleaned] = display_name

    if not display_to_fetch_identifier:
        fallback_reverse = {
            fetch_identifier.strip(): display_name
            for display_name, fetch_identifier in DEFAULT_JIRA_PROJECT_NAME_MAPPING.items()
            if fetch_identifier.strip()
        }
        fallback_reverse.update({name: name for name in DEFAULT_JIRA_PROJECT_NAME_MAPPING})
        return DEFAULT_JIRA_PROJECT_NAME_MAPPING.copy(), fallback_reverse

    return display_to_fetch_identifier, identifier_to_display


JIRA_PROJECT_NAME_MAPPING, JIRA_PROJECT_IDENTIFIER_TO_DISPLAY = _load_project_name_mapping()

MAX_COMMENTS_PER_ISSUE = 5  # Keep the N most recent comments to avoid token bloat


def validate_env():
    if not JIRA_TOKEN or JIRA_TOKEN == "your_token_here":
        raise ValueError("JIRA_TOKEN is not set. Add it to your .env file.")
    if "yourdomain" in JIRA_URL:
        raise ValueError("JIRA_URL still contains placeholder. Set your real JIRA instance URL.")


def get_projects_from_env() -> list[str]:
    """Return a cleaned list of project names from JIRA_PROJECTS env var."""
    if not JIRA_PROJECTS:
        return []

    raw = JIRA_PROJECTS.strip()
    # Allow env value wrapped as a single quoted string.
    if (raw.startswith("'") and raw.endswith("'")) or (raw.startswith('"') and raw.endswith('"')):
        raw = raw[1:-1]

    projects = []
    for name in raw.split(","):
        cleaned = name.strip()
        # Unescape shell-style quoted entries like \'Project Name\'.
        cleaned = cleaned.replace("\\'", "'").replace('\\"', '"')
        cleaned = cleaned.strip().strip("'\"")
        if cleaned:
            projects.append(cleaned)

    return projects


def fetch_jira_issues(project_name: str, extra_jql: str = "") -> dict:
    """
    Fetch issues for one JIRA project, including recent comments.

    Args:
        project_name: JIRA project name (key in JIRA_PROJECT_NAME_MAPPING)
        extra_jql:    Optional JQL clause to override the JIRA_JQL env var

    Returns:
        {
            "project_name": str,
            "display_name": str,
            "total": int,
            "issues": [
                {
                    "issue_type": str,
                    "issue_key":  str,
                    "summary":    str,
                    "status":     str,
                    "priority":   str,
                    "created":    "YYYY-MM-DD",
                    "updated":    "YYYY-MM-DD",
                    "duedate":    "YYYY-MM-DD" or "",
                    "comments": [
                        {"author": str, "date": "YYYY-MM-DD", "body": str}
                    ]
                }
            ]
        }
    """
    validate_env()

    project_name = project_name.strip()
    display_name = JIRA_PROJECT_IDENTIFIER_TO_DISPLAY.get(project_name, project_name)
    fetch_project_name = JIRA_PROJECT_NAME_MAPPING.get(display_name, project_name)
    jql_filter   = extra_jql or JIRA_JQL
    jql          = f'project = {fetch_project_name} {jql_filter}'.strip()

    headers = {
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "Accept": "application/json",
    }
    params = {
        "jql":        jql,
        "fields":     "issuetype,key,summary,status,priority,created,updated,duedate,comment",
        "maxResults": 200,
    }

    print(f"Fetching issues: project = '{fetch_project_name}' | jql = {jql_filter or '(none)'}")
    print(f"  → URL: {JIRA_URL}/rest/api/2/search")
    print(f"  → Headers: {headers}")
    print(f"  → Params: {params}")
    
    resp = requests.get(
        f"{JIRA_URL}/rest/api/2/search",
        headers=headers,
        params=params,
        timeout=30,
    )
    
    if resp.status_code != 200:
        raise RuntimeError(
            f"JIRA API error {resp.status_code} for project '{fetch_project_name}': {resp.text}"
        )

    raw_issues = resp.json().get("issues", [])
    print(f"  → {len(raw_issues)} issues returned")

    issues = []
    for i in raw_issues:
        f = i.get("fields", {})

        # Extract the N most recent comments
        raw_comments  = (f.get("comment") or {}).get("comments", [])
        recent        = raw_comments[-MAX_COMMENTS_PER_ISSUE:]
        comments      = [
            {
                "author": (c.get("author") or {}).get("displayName", "Unknown"),
                "date":   (c.get("updated") or c.get("created") or "")[:10],
                "body":   (c.get("body") or "").strip(),
            }
            for c in recent
        ]

        issues.append({
            "issue_type": f.get("issuetype", {}).get("name", "Unknown"),
            "issue_key":  i.get("key", ""),
            "summary":    f.get("summary", ""),
            "status":     f.get("status", {}).get("name", "Unknown"),
            "priority":   f.get("priority", {}).get("name", "None"),
            "created":    (f.get("created")  or "")[:10],
            "updated":    (f.get("updated")  or "")[:10],
            "duedate":    (f.get("duedate")  or ""),
            "comments":   comments,
        })

    return {
        "project_name": fetch_project_name,
        "display_name": display_name,
        "total":        len(issues),
        "issues":       issues,
    }


def format_issue_for_prompt(issue: dict) -> str:
    """
    Format a single issue as a compact text block for use in AI prompts.
    Includes the most recent comment if present.
    """
    lines = [
        f"Key: {issue['issue_key']} | Type: {issue['issue_type']} | "
        f"Status: {issue['status']} | Due: {issue['duedate'] or 'N/A'}",
        f"Summary: {issue['summary']}",
    ]
    if issue.get("comments"):
        latest = issue["comments"][-1]
        lines.append(
            f"Latest comment ({latest['author']}, {latest['date']}): {latest['body'][:300]}"
        )
    return "\n".join(lines)


def print_summary_table(result: dict):
    """Print a simple ASCII table of fetched issues to stdout."""
    print(f"\n{'='*70}")
    print(f"Project : {result['project_name']}  ({result['display_name']})")
    print(f"Total   : {result['total']} issues")
    print(f"{'='*70}")
    print(f"{'TYPE':<14} {'KEY':<14} {'STATUS':<16} {'SUMMARY'}")
    print(f"{'-'*70}")
    for issue in result["issues"]:
        summary = issue["summary"][:38] + "…" if len(issue["summary"]) > 39 else issue["summary"]
        print(f"{issue['issue_type']:<14} {issue['issue_key']:<14} {issue['status']:<16} {summary}")
        for c in issue["comments"]:
            snippet = c["body"][:60].replace("\n", " ")
            print(f"  └─ [{c['date']}] {c['author']}: {snippet}")
    print()


def save_json(result: dict):
    """Save the result dict to a timestamped JSON file in jira_issues folder."""
    safe_name = result["project_name"].replace(" ", "_").replace("/", "-")
    filename  = f"jira_issues_{safe_name}_{date.today().isoformat()}.json"
    output_dir = "jira_issues"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    with open(file_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)
    print(f"Saved → {file_path}")
    return file_path


# ── CLI entry point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    argv = sys.argv[1:]

    # Optional compatibility mode: allow first positional arg to be a JIRA base URL.
    if argv and argv[0].startswith(("http://", "https://")):
        JIRA_URL = argv[0].rstrip("/")
        argv = argv[1:]

    # Backward compatible mode: project name from CLI.
    if len(argv) >= 1:
        projects = [argv[0]]
        extra_jql = argv[1] if len(argv) > 1 else ""
    else:
        # New mode: fetch all projects from JIRA_PROJECTS when no CLI project is passed.
        projects = get_projects_from_env()
        extra_jql = ""

    if not projects:
        print("Usage: python fetch.py '<Project Name>' [extra_jql]")
        print("   or: python fetch.py  # uses JIRA_PROJECTS from .env")
        print("   or: python fetch.py '<JIRA_URL>' '<Project Name>' [extra_jql]")
        print("Example: python fetch.py 'CCDI Hub' 'AND updated >= -30d'")
        print("Example: python fetch.py 'https://tracker.nci.nih.gov' 'CCDI Hub' 'AND updated >= -30d'")
        print("Example .env: JIRA_PROJECTS=CCDI Hub,CCDI CPI,Index of NCI Studies")
        sys.exit(1)

    for project in projects:
        result = fetch_jira_issues(project, extra_jql)
        print_summary_table(result)
        save_json(result)
