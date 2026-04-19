# ESI Skills Hub Static Web App Design

Date: 2026-04-18
Status: Approved for planning handoff
Owner: Internal ESI engineering enablement

## 1. Goal and Context

Build a simple static web app that demonstrates the skills available in the ESI skills repository and shows how to use them.

This app is for internal ESI engineers and developers. It should be deployable to Vercel and support easy sharing of links to individual skills.

## 2. Confirmed Decisions

- Audience: Internal ESI engineers and developers
- User capabilities: Browse skills, copy install commands, filter/search skills
- Data source: Live GitHub API at runtime
- Frontend stack: Vite + React
- Navigation pattern: Catalog route plus dedicated detail route for each skill (Option C)

## 3. Functional Requirements

1. Catalog page
- Show all available skills from the repository
- Provide search by skill name/description
- Provide filtering by category/tag where available
- Show concise skill summary in a card-based layout

2. Skill detail page
- Dedicated route per skill (`/skills/:name`)
- Show parsed skill metadata from `SKILL.md`
- Include copyable install command for the selected skill
- Provide clear navigation back to catalog

3. Install command behavior
- Render command in a copy-friendly format:
  - `npx skills add essentialsoft/agentskills@<skill-name>`
- One-click copy with success and error feedback

4. Live data behavior
- Fetch from GitHub API on runtime load
- Support direct deep links to detail routes by fetching missing skill data on demand

## 4. Non-Functional Requirements

- Deployable as a static frontend on Vercel
- Responsive for desktop and mobile
- Accessible controls for search, filter, and copy actions
- Fail gracefully under network issues and API rate limits

## 5. Architecture

## 5.1 High-level structure

- Vite + React app
- React Router with two main routes:
  - `/` for catalog
  - `/skills/:name` for detail pages

## 5.2 Data layer

- GitHub API client for repository directory and file reads
- Parser/normalizer for `SKILL.md` frontmatter and selected content blocks
- In-memory state for fetched skills and loading/error status

## 5.3 UI layer

- App shell and top-level layout
- Catalog page with search and filter controls
- Skill grid and reusable skill card
- Skill detail page with metadata, content summary, and copy command block

## 6. Data Flow

1. App loads catalog route
2. Fetch skill folder names from repository path
3. Fetch each `SKILL.md` content
4. Parse into normalized skill objects
5. Store in state and render catalog
6. User applies search/filter client-side
7. User opens detail route
8. If detail skill is absent in state, fetch and parse that one skill on demand
9. Render detail and install command copy action

## 7. Error Handling and Reliability

- Repository fetch failure:
  - Show retryable message on catalog page
- GitHub rate limit response:
  - Show explicit rate-limit message and retry guidance
- Malformed `SKILL.md` for one skill:
  - Skip that skill, keep rendering others
- Empty repository result:
  - Show clear empty-state message
- No filter matches:
  - Show no-results state with clear reset action
- Clipboard API failure:
  - Show copy-failure feedback and provide visible command text for manual copy

## 8. Testing Strategy (v1)

1. Unit tests
- Frontmatter parsing and normalization behavior
- Search/filter functions

2. Integration tests
- Catalog route success/failure loading states
- Detail deep-link fetch flow

3. Manual verification
- Desktop/mobile responsive checks
- Copy command behavior in major browsers
- Vercel deployment smoke check with live GitHub data

## 9. Scope Boundaries and YAGNI

Included in v1:
- Catalog + detail routes
- Search/filter
- Copy install command
- Runtime GitHub API fetch

Excluded from v1:
- Authentication and role management
- Backend persistence or analytics pipeline
- Rich editing UI for skill content
- Complex personalization

## 10. Risks and Mitigations

1. GitHub API rate limiting
- Mitigation: clear UX messaging and retry path

2. Inconsistent skill markdown formats
- Mitigation: tolerant parser with defaults and per-skill skip behavior

3. Performance impact from many file fetches
- Mitigation: lazy fetch on detail routes and simple client caching

## 11. Delivery Plan (High-Level)

1. Scaffold Vite + React app and routing
2. Implement GitHub fetch and parser utilities
3. Build catalog UI with search and filter
4. Build detail page and copy command UX
5. Add loading/error/empty states
6. Add tests and responsive polish
7. Deploy to Vercel

## 12. Acceptance Criteria

- Users can browse all available skills in a catalog
- Users can search and filter skills from the catalog
- Users can open a dedicated detail URL for any skill
- Users can copy a valid `npx skills add ...` command per skill
- App handles API and parse failures without total-page failure
- App is deployable and functional on Vercel
