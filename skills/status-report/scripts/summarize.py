"""
status-report/scripts/summarize.py

Local deterministic summarization utilities for status-report generation.
This module produces a prose summary and planned tasks from issue metadata,
then generate.py passes that output into the docx renderer.
"""


def summarize_project(project_result: dict) -> tuple[str, list[str]]:
    """
    Generate a deterministic prose project summary and a list of planned tasks
    for next month based on issue metadata.
    """
    display_name = project_result["display_name"]
    issues = project_result["issues"]

    if not issues:
        return (
            f"No issues were found for {display_name} in this reporting period.",
            ["No planned tasks identified — no issues were returned from JIRA."],
        )

    status_counts = {}
    type_counts = {}
    for issue in issues:
        status = (issue.get("status") or "Unknown").strip()
        issue_type = (issue.get("issue_type") or "Unknown").strip()
        status_counts[status] = status_counts.get(status, 0) + 1
        type_counts[issue_type] = type_counts.get(issue_type, 0) + 1

    sorted_status = sorted(status_counts.items(), key=lambda x: (-x[1], x[0]))
    sorted_types = sorted(type_counts.items(), key=lambda x: (-x[1], x[0]))

    def _pick_by_status(keywords: tuple[str, ...], limit: int) -> list[dict]:
        matches = []
        for issue in issues:
            status = (issue.get("status") or "").lower()
            if any(k in status for k in keywords):
                matches.append(issue)
        return matches[:limit]

    completed_issues = _pick_by_status(("done", "closed", "resolved", "complete"), 3)
    active_issues = _pick_by_status(("in progress", "review", "testing", "qa"), 4)
    queued_issues = _pick_by_status(("to do", "open", "backlog", "selected"), 3)
    blocked_issues = _pick_by_status(("block", "hold", "waiting", "impediment"), 2)

    top_status_text = ", ".join(f"{name}: {count}" for name, count in sorted_status[:4])
    top_type_text = ", ".join(f"{name}: {count}" for name, count in sorted_types[:3])

    summary_parts = [
        (
            f"{display_name} tracked {len(issues)} issues this month across key delivery areas. "
            f"The current workflow distribution is {top_status_text}."
        ),
        (
            f"Work was concentrated in {top_type_text}, reflecting a mix of feature development, "
            f"defect resolution, and operational follow-through."
        ),
    ]

    if completed_issues:
        completed_text = "; ".join(i.get("summary", "").strip() for i in completed_issues if i.get("summary"))
        if completed_text:
            summary_parts.append(f"Notable completed outcomes include: {completed_text}.")

    if active_issues:
        active_text = "; ".join(i.get("summary", "").strip() for i in active_issues[:2] if i.get("summary"))
        if active_text:
            summary_parts.append(
                f"Current in-flight work remains focused on: {active_text}, indicating continued progress into next month."
            )

    if blocked_issues:
        summary_parts.append(
            "A small set of items remains constrained by dependencies and coordination needs, "
            "which should be prioritized to maintain momentum."
        )

    summary = " ".join(summary_parts)

    planned_tasks = []
    for issue in active_issues[:3]:
        task = issue.get("summary", "").strip()
        if task:
            planned_tasks.append(f"Continue and complete: {task}")

    for issue in queued_issues[:2]:
        task = issue.get("summary", "").strip()
        if task:
            planned_tasks.append(f"Start or advance planned backlog work: {task}")

    for issue in blocked_issues[:1]:
        task = issue.get("summary", "").strip()
        if task:
            planned_tasks.append(f"Resolve blockers and dependencies for: {task}")

    if not planned_tasks:
        planned_tasks = [i.get("summary", "").strip() for i in issues[:5] if i.get("summary")]

    deduped = []
    seen = set()
    for item in planned_tasks:
        if item and item not in seen:
            seen.add(item)
            deduped.append(item)

    return summary, deduped[:6]
