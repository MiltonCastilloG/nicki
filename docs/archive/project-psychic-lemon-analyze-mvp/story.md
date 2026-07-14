# analyze-mvp — Minimal Gemini analysis for Psychic Lemon

Minimal analyze MVP for Psychic Lemon. Clinician pastes transcript locally; one-shot analysis via Gemini; results in browser. Maps to P1 tasks 1.2–1.8.

End-to-end flow: clinician pastes session text into `backend/data/transcript.txt` (gitignored). UI shows **Psychic Lemon** + **Analyze** button. Click → `POST /api/analyze` (no body) via Vite proxy → backend reads file → Gemini (`gemini-2.5-flash`, `@google/genai`) → structured `AnalysisResult` → UI renders four sections. Chat (1.9–1.10) out of scope.

---

## Design decisions (approved)

| ADR | Decision |
| --- | -------- |
| ADR-1 | Transcript at `backend/data/transcript.txt`; gitignored; hand-paste only — no upload/paste API |
| ADR-2 | `AnalysisResult`: `patterns: string[]`, `discrepancies: string[]`, `soap: { subjective, objective, assessment, plan }` (each string), `tips: string[]` |
| ADR-3 | LLM: `@google/genai`; `GEMINI_API_KEY` required; `GEMINI_MODEL` in `.env` defaulting to `gemini-2.5-flash` in code when unset |
| ADR-4 | `POST /api/analyze` no body; missing file → 404; empty/whitespace-only → 400; LLM failure → 502; success → 200 + `AnalysisResult` JSON |
| ADR-5 | Error body `{ "error": string }` |
| ADR-6 | `backend/src/agent.ts`: AGENT-SPEC system prompt; JSON-constrained Gemini output; ephemeral processing — no DB, no transcript logging |
| ADR-7 | UI: keep heading; Analyze button; disable button while in-flight; render patterns / discrepancies / SOAP (four sub-headings) / tips; plain error text on failure |
| ADR-8 | `ui/vite.config.ts`: `server.proxy["/api"] → http://localhost:8008` |
| ADR-9 | `backend/src/analyze.test.ts`: file-validation branches only (missing/empty transcript) — no live LLM |
| ADR-10 | `backend/.env.example` adds `GEMINI_API_KEY` + `GEMINI_MODEL`; README status/stack updated for transcript-file workflow |

---

## Feature: Local transcript source

As a psychologist using Psychic Lemon locally  
I want the current session transcript in a fixed gitignored file  
So that the backend has one source of truth without an upload flow

```gherkin
Given backend/ is scaffolded with Hono on port 8008
And backend/data/transcript.txt does not exist or is gitignored
```

### Scenario: Transcript file is the single source

```gherkin
When the clinician pastes session text into backend/data/transcript.txt by hand
Then that file is the only transcript source for analyze in this MVP
And backend/data/ or transcript.txt is listed in .gitignore
And no API accepts transcript upload or paste in this task
```

---

## Feature: Agent module with structured analysis

As a psychologist  
I want session analysis grounded in AGENT-SPEC  
So that I get clinician-only drafts I can review and edit

```gherkin
Given GEMINI_API_KEY is set in backend/.env
And backend/src/agent.ts exports AnalysisResult and analyzeTranscript()
And the system prompt encodes AGENT-SPEC (case-scoped, no diagnosis, clinician-only, ephemeral)
```

### Scenario: analyzeTranscript returns structured JSON

```gherkin
When analyzeTranscript() runs with non-empty transcript text
Then it calls Gemini via @google/genai using GEMINI_MODEL (default gemini-2.5-flash)
And it returns AnalysisResult with patterns, discrepancies, soap, and tips
And patterns and discrepancies and tips are string arrays
And soap has subjective, objective, assessment, and plan string fields
And raw transcript and chain-of-thought are not persisted beyond the request
```

---

## Feature: Analyze API route

As a Psychic Lemon developer  
I want POST /api/analyze on the Hono app  
So that the frontend triggers analysis without sending transcript in the body

```gherkin
Given backend/src/app.ts mounts POST /api/analyze
And the route reads backend/data/transcript.txt server-side
```

### Scenario: Missing transcript file

```gherkin
Given backend/data/transcript.txt does not exist
When the client sends POST /api/analyze with no body
Then the response status is 404
And the body is JSON with an error message
```

### Scenario: Empty transcript file

```gherkin
Given backend/data/transcript.txt exists but is empty or whitespace-only
When the client sends POST /api/analyze
Then the response status is 400
And the body is JSON with an error message
```

### Scenario: Successful analysis

```gherkin
Given backend/data/transcript.txt contains session text
And the Gemini call succeeds
When the client sends POST /api/analyze
Then the response status is 200
And Content-Type is application/json
And the body matches AnalysisResult shape per ADR-2
```

### Scenario: LLM failure

```gherkin
Given backend/data/transcript.txt contains session text
And the Gemini call fails
When the client sends POST /api/analyze
Then the response status is 502
And the body is JSON with an error message
```

---

## Feature: Analyze route tests without live LLM

As a developer  
I want validation-branch tests for the analyze route  
So that missing/empty transcript errors are caught without API keys

```gherkin
Given backend/src/analyze.test.ts exists
And tests do not call the live Gemini API
```

### Scenario: Missing file returns error response

```gherkin
When the test exercises POST /api/analyze with no transcript file present
Then the response status is 404
```

### Scenario: Empty file returns error response

```gherkin
When the test exercises POST /api/analyze with an empty transcript file
Then the response status is 400
```

---

## Feature: Frontend analysis view

As a psychologist  
I want an Analyze button and rendered results  
So that I can review patterns, discrepancies, SOAP, and tips in the browser

```gherkin
Given ui/src/App.tsx shows the Psychic Lemon heading
And there is no transcript input on the page
```

### Scenario: Analyze triggers API and renders sections

```gherkin
When I click Analyze
Then the UI sends POST /api/analyze to /api/analyze
And the button is disabled while the request is in flight
And on success the UI renders patterns, discrepancies, SOAP (four parts), and tips
And the Psychic Lemon heading remains visible
```

### Scenario: API error shows plain message

```gherkin
When POST /api/analyze returns an error status
Then the UI shows a plain error state with the error message
And no analysis sections are shown as successful output
```

---

## Feature: Vite dev proxy to backend

As a developer running ui and backend locally  
I want /api proxied to port 8008  
So that the frontend calls the Hono API without CORS setup

```gherkin
Given ui/vite.config.ts configures server.proxy
When the UI dev server runs on port 8007
And the backend runs on port 8008
Then browser requests to /api/* from the UI origin reach http://localhost:8008
```

---

## Feature: Env and documentation

As a new contributor  
I want env template and README updated  
So that I can run the analyze MVP without guessing

### Scenario: Env example documents Gemini vars

```gherkin
Given backend/.env.example is updated
Then it documents GEMINI_API_KEY and GEMINI_MODEL alongside PORT
And README notes the hand-pasted transcript workflow and analyze MVP status
```

---

## Out of scope

- Chat route/UI (1.9–1.10)
- SQLite, Zod schemas, transcript upload UI
- CORS (Vite proxy handles dev)
- Live LLM integration tests
