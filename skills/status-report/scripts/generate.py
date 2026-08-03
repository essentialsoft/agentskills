"""
status-report/scripts/generate.py

End-to-end script: fetches JIRA issues for one or more projects, summarizes
each project, and produces a monthly status report .docx.

Usage:
    python generate.py

The script reads configuration from environment variables and prompts
interactively for anything that isn't set.

Environment variables (set in .env or shell):
    JIRA_TOKEN      — JIRA Bearer token
    JIRA_URL        — JIRA base URL (default: https://tracker.nci.nih.gov)
    JIRA_JQL        — Additional JQL filter
    JIRA_PROJECTS   — Comma-separated project names (optional; asked interactively if absent)
    REPORT_AUTHOR   — Author name for the report title (optional; asked interactively if absent)
    REPORT_DATE     — Report month/year string, e.g. "May 2026" (optional; asked interactively)
"""

import os
import sys
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Path setup: allow importing from jira-fetch/scripts ──────────────────────
SKILL_ROOT   = Path(__file__).resolve().parents[1]          # status-report/
JIRA_FETCH   = SKILL_ROOT.parent / "jira-fetch" / "scripts"
REPO_ROOT    = Path(__file__).resolve().parents[4]
JIRA_ISSUES_DIR = REPO_ROOT / "jira_issues"
PROJECT_MAPPINGS_FILE = REPO_ROOT / "project_mappings.json"
sys.path.insert(0, str(JIRA_FETCH))

from fetch     import fetch_jira_issues, JIRA_PROJECT_NAME_MAPPING, get_projects_from_env  # noqa: E402
from summarize import summarize_project                               # noqa: E402

# python-docx for Word document generation
from docx                   import Document
from docx.shared            import Pt, RGBColor
from docx.enum.text         import WD_ALIGN_PARAGRAPH
from docx.oxml.ns           import qn
from docx.oxml              import OxmlElement


# ── Available projects ────────────────────────────────────────────────────────
def _load_project_mappings() -> tuple[list[str], dict[str, str], dict[str, str], dict[str, list[str]]]:
    all_projects = list(JIRA_PROJECT_NAME_MAPPING.keys())
    identifier_to_display = {display_name: display_name for display_name in all_projects}
    identifier_to_display.update({
        project_id.strip(): display_name
        for display_name, project_id in JIRA_PROJECT_NAME_MAPPING.items()
        if project_id.strip()
    })
    display_to_fetch_identifier = {
        display_name: (project_id.strip() or display_name)
        for display_name, project_id in JIRA_PROJECT_NAME_MAPPING.items()
    }
    display_to_identifiers = {display_name: [display_name] for display_name in all_projects}

    if PROJECT_MAPPINGS_FILE.exists():
        with PROJECT_MAPPINGS_FILE.open("r", encoding="utf-8") as fh:
            config_entries = json.load(fh)

        all_projects = []
        identifier_to_display = {}
        display_to_fetch_identifier = {}
        display_to_identifiers = {}

        for entry in config_entries:
            display_name = (entry.get("display_name") or "").strip()
            if not display_name:
                continue

            identifiers = []
            for identifier in entry.get("identifiers", []):
                cleaned = str(identifier).strip()
                if cleaned and cleaned not in identifiers:
                    identifiers.append(cleaned)
            if display_name not in identifiers:
                identifiers.insert(0, display_name)

            fetch_identifier = str(entry.get("fetch_identifier") or identifiers[0]).strip()

            all_projects.append(display_name)
            display_to_fetch_identifier[display_name] = fetch_identifier
            display_to_identifiers[display_name] = identifiers
            for identifier in identifiers:
                identifier_to_display[identifier] = display_name

    return all_projects, identifier_to_display, display_to_fetch_identifier, display_to_identifiers


ALL_PROJECTS, IDENTIFIER_TO_DISPLAY, DISPLAY_TO_FETCH_IDENTIFIER, DISPLAY_TO_IDENTIFIERS = _load_project_mappings()


def _ask(prompt: str, default: str = "") -> str:
    val = input(f"{prompt}{f' [{default}]' if default else ''}: ").strip()
    return val or default


def _display_name_for_project(project_name: str) -> str:
    return IDENTIFIER_TO_DISPLAY.get(project_name.strip(), project_name.strip())


def _fetch_identifier_for_project(project_name: str) -> str:
    display_name = _display_name_for_project(project_name)
    return DISPLAY_TO_FETCH_IDENTIFIER.get(display_name, project_name.strip())


def _normalize_projects(projects: list[str]) -> list[str]:
    normalized = []
    seen = set()
    for project_name in projects:
        display_name = _display_name_for_project(project_name)
        if display_name and display_name not in seen:
            seen.add(display_name)
            normalized.append(display_name)
    return normalized


def _gather_inputs() -> tuple[str, str, list[str], str]:
    """Collect author name, report date, project list, and optional JQL."""
    author = os.getenv("REPORT_AUTHOR") or _ask("Author name")
    rdate  = os.getenv("REPORT_DATE")  or _ask("Report month/year (e.g. May 2026)")
    jql    = os.getenv("JIRA_JQL", "")

    projects_env = os.getenv("JIRA_PROJECTS", "")
    if projects_env:
        # Reuse jira-fetch parsing so quoted .env values are handled correctly.
        projects = _normalize_projects(get_projects_from_env())
    else:
        print("\nAvailable projects:")
        for i, p in enumerate(ALL_PROJECTS, 1):
            print(f"  {i:2}. {p}")
        raw = _ask("\nEnter project numbers (comma-separated) or names")
        projects = []
        for token in raw.split(","):
            token = token.strip()
            if token.isdigit() and 1 <= int(token) <= len(ALL_PROJECTS):
                projects.append(ALL_PROJECTS[int(token) - 1])
            elif token in IDENTIFIER_TO_DISPLAY:
                projects.append(_display_name_for_project(token))
            else:
                print(f"  ⚠ '{token}' not recognised — skipping")

    return author, rdate, projects, jql


def _add_toc(doc: Document):
    """Insert a Word auto-updating Table of Contents field."""
    paragraph = doc.add_paragraph()
    run       = paragraph.add_run()
    fldChar   = OxmlElement("w:fldChar")
    fldChar.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
    fldChar2  = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    fldChar3  = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def _add_issue_table(doc: Document, issues: list):
    """Add the 4-column issue table for a project."""
    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, text in enumerate(["Issue Type", "Issue Key", "Summary", "Status"]):
        hdr[i].text = text
        hdr[i].paragraphs[0].runs[0].bold = True

    for issue in issues:
        row = table.add_row().cells
        row[0].text = issue.get("issue_type", "")
        row[1].text = issue.get("issue_key",  "")
        row[2].text = issue.get("summary",     "")
        row[3].text = issue.get("status",      "")


def _safe_project_name(project_name: str) -> str:
    return project_name.replace(" ", "_").replace("/", "-")


def _cache_candidates(project_name: str) -> list[str]:
    display_name = _display_name_for_project(project_name)
    candidates = DISPLAY_TO_IDENTIFIERS.get(display_name, [display_name])

    seen = set()
    ordered = []
    for c in candidates:
        cleaned = c.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            ordered.append(cleaned)
    return ordered


def _load_cached_project_result(project_name: str) -> dict | None:
    """Load the newest cached JSON for one project from jira_issues/ if available."""
    if not JIRA_ISSUES_DIR.exists():
        return None

    matches = []
    for candidate in _cache_candidates(project_name):
        safe = _safe_project_name(candidate)
        matches.extend(JIRA_ISSUES_DIR.glob(f"jira_issues_{safe}_*.json"))

    if not matches:
        return None

    latest = max(matches, key=lambda p: p.stat().st_mtime)
    with latest.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict) or "issues" not in data or "display_name" not in data:
        return None
    data["display_name"] = _display_name_for_project(project_name)
    return data


def _trigger_jira_fetch_if_cache_empty(projects: list[str], jql: str):
    """Run jira-fetch skill only when jira_issues folder is missing or empty."""
    cached_files = list(JIRA_ISSUES_DIR.glob("*.json")) if JIRA_ISSUES_DIR.exists() else []
    if cached_files:
        print(f"Using cached JIRA JSON files from {JIRA_ISSUES_DIR}")
        return

    print("jira_issues folder missing or empty. Triggering jira-fetch skill...")
    env = os.environ.copy()
    env["JIRA_PROJECTS"] = ",".join(_fetch_identifier_for_project(project) for project in projects)
    if jql:
        env["JIRA_JQL"] = jql

    fetch_script = JIRA_FETCH / "fetch.py"
    subprocess.run([sys.executable, str(fetch_script)], check=True, env=env, cwd=str(REPO_ROOT))


def _build_docx(author: str, report_date: str, projects_data: list, skipped_projects: list[str] | None = None) -> str:
    """
    Build the Word document from collected project data.

    projects_data: list of dicts, each:
        {
            "display_name": str,
            "issues": list,
            "summary": str,
            "planned_tasks": list[str]
        }

    Returns the saved filename.
    """
    doc = Document()

    # Title
    title_para = doc.add_heading(f"{author}'s Status Report — {report_date}", level=1)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Table of Contents
    _add_toc(doc)
    doc.add_page_break()

    # One section per project
    for project in projects_data:
        doc.add_heading(f"{project['display_name']}:", level=1)
        doc.add_paragraph("Tasks completed or to be continued in the upcoming month.")

        _add_issue_table(doc, project["issues"])

        doc.add_heading("Project Summary", level=3)
        doc.add_paragraph(project["summary"])

        doc.add_heading("Planned Tasks for Next Month", level=3)
        for task in project["planned_tasks"]:
            para = doc.add_paragraph(style="List Bullet")
            para.add_run(task)

        doc.add_page_break()

    if skipped_projects:
        footer_note = "Skipped projects: " + "; ".join(skipped_projects)
        for section in doc.sections:
            footer = section.footer.paragraphs[0] if section.footer.paragraphs else section.footer.add_paragraph()
            footer.text = footer_note

    # Derive filename: "Status_Report_Smith_202605_20260706_203705.docx"
    last_name  = author.strip().split()[-1] if author.strip() else "Unknown"
    month_code = re.sub(r"[^0-9]", "", report_date)[:6]  # e.g. "202605"
    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename   = f"Status_Report_{last_name}_{month_code}_{timestamp}.docx"

    doc.save(filename)
    return filename


def main():
    author, report_date, projects, jql = _gather_inputs()

    if not projects:
        print("No projects selected. Exiting.")
        sys.exit(1)

    projects_data = []
    skipped_projects = []

    try:
        _trigger_jira_fetch_if_cache_empty(projects, jql)
    except Exception as e:
        print(f"  ⚠ Failed to trigger jira-fetch skill ({e}). Falling back to direct fetch.")

    for project_name in projects:
        print(f"\n{'─'*50}")
        print(f"Processing: {project_name}")

        # Step 1: load from cache first
        result = _load_cached_project_result(project_name)
        if result:
            print(f"  → Loaded cached issues: {result.get('total', len(result.get('issues', [])))}")
        else:
            # Fallback if selected project has no cache file.
            try:
                result = fetch_jira_issues(_fetch_identifier_for_project(project_name), jql)
            except Exception as e:
                print(f"  ✗ Fetch failed: {e} — skipping project")
                skipped_projects.append(f"{_display_name_for_project(project_name)} ({e})")
                continue

        result["display_name"] = _display_name_for_project(project_name)

        # Step 2: local summary generation
        print(f"  → {result['total']} issues — generating project summary…")
        summary, planned_tasks = summarize_project(result)

        projects_data.append({
            "display_name": result["display_name"],
            "issues":       result["issues"],
            "summary":      summary,
            "planned_tasks": planned_tasks,
        })

    if not projects_data:
        print("\nNo project data collected. Nothing to write.")
        sys.exit(1)

    # Step 3: generate docx
    print(f"\n{'='*50}")
    print("Generating Word document…")
    filename = _build_docx(author, report_date, projects_data, skipped_projects)
    print(f"✅  Saved → {filename}")


if __name__ == "__main__":
    main()
