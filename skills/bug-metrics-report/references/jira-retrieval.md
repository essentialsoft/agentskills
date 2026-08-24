# Jira Data Retrieval Rules

Shared retrieval procedure for all CRDCDH Jira reports. These rules exist because
the two most common reporting failures are silent ones: a report built from only
the first pagination page, and a report that treats an issue's *current* state as
its *historical* state. Everything below is aimed at preventing those.

## 1. Confirm scope before querying

Reports may be scoped by one or more Sprints, one or more Fix Versions (Releases),
or both. Sprint is the primary reporting dimension.

- If the user has not specified a sprint or release, ask which one(s) to include.
  Do not query Jira until the scope is clear.
- Sprint-only scope: retrieve issues associated with the selected sprints.
- Release-only scope: retrieve issues associated with the selected releases, then
  group results by sprint. Include only sprints that actually appear on issues in
  scope.
- Sprint + Release: apply both filters.
- Never report an issue under a sprint outside the requested scope.

## 2. Build the query

Filter on: project = the configured project key, the issue type(s) the metric
requires, and the sprint/fixVersion scope. Do **not** filter by status or
resolution in the initial query — completed and incomplete issues are both
required by every metric.

Request every field the metrics need in the same query (see the skill body and
`config.md` for the field list), plus sprint metadata when available: sprint ID,
name, state, start date, end date, completion date. When a metric depends on
history (status at sprint end, when an issue entered a sprint), also request
changelog / issue-history data (`expand=changelog` or the MCP's equivalent).

## 3. Retrieve every pagination page

Jira results are paginated, and the page you get back may be smaller than the
page size you asked for. For each response:

1. Append the returned issues to the result set.
2. Read the response `total`.
3. Compute `start_at + number_of_returned_issues` using the **actual** count of
   returned issues.
4. Continue requesting pages until `start_at + returned >= total`.

After retrieval:

- Confirm the collected count matches Jira's reported total; if it doesn't,
  re-query before proceeding.
- De-duplicate by Issue Key.
- Never generate a report from only the first page. If full retrieval is
  impossible, label the report as incomplete — do not present partial data as
  complete.

## 4. Normalize sprint assignment

An issue's Sprint field may contain several sprints. Interpret them with dates
and changelog history, not string parsing. For each reported sprint determine
whether the issue was present at sprint start, added after sprint start, completed
during the sprint, or carried into a later sprint.

When sprint dates are unavailable, fall back in this order and disclose which
fallback was used:

1. Sprint completion date
2. Sprint end date
3. Sprint state (active over closed)
4. Sprint ID (higher = later)
5. Numeric sprint-name suffix, only when consistently formatted

## 5. Historical status (status at sprint end)

For a closed sprint, an issue's completion is judged by its **Status Category at
the sprint end date**, reconstructed from the changelog — not by its current
status. Status Category "Done" (case-insensitive) = completed; anything else =
incomplete. When Status Category is unavailable, use the completed-status name
list in `config.md` and disclose the fallback.

For an **active** sprint with no end date yet, use current status, label the
output an active-sprint snapshot, and never present it as final sprint-end
performance.

When changelog history is unavailable, do not silently substitute current status:
state which metrics could not be computed historically, and offer a clearly
labeled current-state report instead.

## 6. Error handling

- **Query failure**: identify the failed query or page, retry when appropriate,
  and never present partial data as complete — label incomplete results clearly.
- **Missing sprint dates**: apply the fallback order above, disclose the affected
  sprints, and avoid claiming exact sprint-start/sprint-end precision.
- **No matching issues**: say that nothing matched, show the applied filters,
  show zero-value tables when useful, and do not fabricate charts.
