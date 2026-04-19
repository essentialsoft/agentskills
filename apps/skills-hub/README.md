# Skills Hub

Static React app that loads skills from GitHub at runtime and presents a searchable catalog plus deep-linkable skill detail pages.

## Local Development

Install dependencies and start the app:

```bash
npm install
npm run dev
```

## Environment Variables

Copy values from `.env.example` if you need to target a different repository:

- `VITE_SKILLS_REPO_OWNER`
- `VITE_SKILLS_REPO_NAME`
- `VITE_SKILLS_REPO_REF`
- `VITE_SKILLS_ROOT_PATH`

## Scripts

- `npm run dev` - run Vite dev server
- `npm run test` - run Vitest tests once
- `npm run test:watch` - run Vitest in watch mode
- `npm run build` - create production build
- `npm run preview` - preview production build

## Routing and Vercel

The app uses client-side routing (`/` and `/skills/:name`).

`vercel.json` includes an SPA rewrite so deep links resolve to `index.html`.
