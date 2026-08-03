[Title — styled H1 in Word]
{{ author_name }}'s Status Report — {{ report_date }}

[Word auto Table of Contents — insert normally, refresh on open]

─────────────────────────────────────────────
{% for project in projects %}

[H1 heading styled in Word]
# {{ project.name }}:

Tasks completed or to be continued in the upcoming month.

[Table — 4 cols, style the header row bold in Word]
| Issue Type | Issue Key | Summary         | Status |
|------------|-----------|-----------------|--------|
{% for row in project.issues %}
| {{ row.issue_type }} | {{ row.issue_key }} | {{ row.summary }} | {{ row.status }} |
{% endfor %}

[H3 heading]
### Project Summary
{{ project.summary }}

[H3 heading]
### Planned Tasks for Next Month
{% for task in project.planned_tasks %}
  • {{ task }}
{% endfor %}

{% endfor %}