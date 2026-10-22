# AI Travel Planner: React frontend

Vite + React 19 + TypeScript frontend for the FastAPI backend in the parent folder.
Styled with Tailwind CSS v4 and [shadcn/ui](https://ui.shadcn.com) components
(Radix base), themed to the site's palette in `src/index.css`.
It opens on a landing page (`#/`) that explains how a plan is made, then the
planner (`#/plan`) has the same features as the Streamlit app in `../frontend/`:
trip form, progress while agents run, itinerary and budget, approve or request
changes, and retry after a failure.

## Run

Start the API from the project root first:

```bash
uv run uvicorn main:app
```

Then, in this folder:

```bash
npm install
npm run dev
```

Open http://localhost:5173. To use a different API address, copy `.env.example`
to `.env` and change `VITE_API_URL`.

## Scripts

| Command | What it does |
|---|---|
| `npm run dev` | Development server with hot reload |
| `npm test` | Vitest + React Testing Library (the API is mocked, no backend needed) |
| `npm run typecheck` | TypeScript in strict mode |
| `npm run lint` | oxlint |
| `npm run build` | Production build into `dist/` |

## Structure

```
src/
  api.ts                 API client and error parsing
  types.ts               Types matching the FastAPI responses
  format.ts              Money and date formatting
  hooks/useTrip.ts       Loads a trip and polls every 4 s while it is running
  hooks/useStoredThreadId.ts  Remembers the current trip across page reloads
  hooks/useHashRoute.ts  Landing page (#/) or planner (#/plan)
  hooks/useCountUp.ts    One-time total count-up on the landing ticket
  index.css              Tailwind and the shadcn theme (colours, fonts, radius)
  app.css                Styles for the plan view (older, kept in a lower CSS layer)
  components/
    ui/                  shadcn/ui components (generated, add more with `npx shadcn add`)
    trip-form/           Date range picker, interests input, live trip ticket
    landing/             Landing page, example plan ticket, route steps, styles
    TripForm.tsx         The trip form
    TripView.tsx         Chooses what to show for each status
    TripProgress.tsx     Running state
    ItineraryView.tsx    Day-by-day plan, warnings, suggestions
    BudgetTable.tsx      Totals, categories, items with source links
    ReviewNotes.tsx      Rule-check issues and reviewer feedback
    ApprovalPanel.tsx    Approve or request changes
    ErrorBoundary.tsx    Catches unexpected rendering errors
```

## Deploying

`npm run build` produces static files in `dist/` that any static host can serve.
Set `VITE_API_URL` to your deployed API at build time, and add the frontend's
address to the API's CORS origins in `main.py`.
