# GenAI Fund — AI & Robotics X/Twitter Outreach Prototype (v3.0 Live Engine)

A full-stack production-grade prototype built for the **GenAI Fund Forward Deployed Engineer (FDE) Take-Home Assignment**. It discovers relevant AI and robotics builders, founders, and researchers on X (Twitter), verifies their background using live post evidence, drafts grounded personalized DMs with Gemini AI for human approval, enforces strict anti-duplication and rate-limit safety rules, and tracks live DM responses requiring team attention.

---

## 🚀 What's New in v3.0 Live Engine

- **Dual Real Account OAuth Connection:** Connect real X accounts using either **OAuth 1.0a HMAC-SHA1** user context (`X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`) or **OAuth 2.0 PKCE** browser authorization flow (`/oauth/x/start` -> `/oauth/x/callback`).
- **Live X User & Tweet Resolution:** Fetch live public profiles and recent posts directly via `GET /2/users/by/username/:username`, `GET /2/users/:id/tweets`, `GET /2/tweets/search/recent`, or X Public Syndication / oEmbed fallbacks.
- **Strict Live X API Mode (`require_live_x_api`):** Guarantees zero synthetic fallback when enabled. If Live X API credentials are not active or rate-limited, actions are cleanly blocked with informative status warnings.
- **Real DM Outbound Engine:** Sends real DMs to verified numerical X user IDs via `POST /2/dm_conversations/with/:participant_id/messages`.
- **Real Reply Sync Engine:** Polls incoming messages via `GET /2/dm_conversations/with/:participant_id/dm_events` and filters events where `sender_id == participant_id` to update lead pipeline status automatically.
- **7-Step Integrated Self-Test Suite:** Run comprehensive end-to-end self-checks directly via `python app.py --self-test` or from the Web UI console.

---

## 1. Quick Setup & Run

### Prerequisites
- Python 3.10+
- Embedded SQLite database (zero external database setup required; WAL mode enabled with `UNIQUE` constraints).

### Installation
```bash
git clone repo_url
cd genai-fund-fde-x-outreach
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Self-Test Suite
```bash
python3 app.py --self-test
```

### Run Web Server
```bash
python3 app.py --host 127.0.0.1 --port 8000
```
Open `localhost:8000` in your web browser.

---

## 2. Authentication & Credentials Config

Configure credentials directly in your environment (`.env`) or live via **Step 1 (API Setup & Auth)** in the Web Control Panel:

### Option A: OAuth 1.0a (Recommended for Direct Live API Access)
```env
X_API_KEY=your_consumer_key
X_API_SECRET=your_consumer_secret
X_ACCESS_TOKEN=your_user_access_token
X_ACCESS_TOKEN_SECRET=your_user_access_token_secret
```

### Option B: OAuth 2.0 PKCE
- Start login flow at `/oauth/x/start`
- Provide `X_CLIENT_ID` and `X_CLIENT_SECRET` in `.env` or UI console.

### Option C: Gemini LLM Integration
```env
GEMINI_API_KEY=your_gemini_api_key
```

---

## 3. Core Architecture & Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/config` | `POST` / `GET` | Save or check runtime API credentials in memory/database |
| `/api/auth/verify` | `GET` | Verify connected X user account (`GET /2/users/me`) |
| `/oauth/x/start` | `GET` | Initiate X OAuth 2.0 PKCE authorization flow |
| `/oauth/x/callback` | `GET` | Handle OAuth 2.0 redirect callback & token exchange |
| `/api/search` | `POST` | Discover candidates via X recent search or keyword matching |
| `/api/candidates/resolve` | `POST` | Fetch real profile & recent posts (`GET /2/users/by/username/:username`) |
| `/api/generate-dm` | `POST` | Draft grounded personalized DM using Gemini LLM |
| `/api/send-approved` | `POST` | Send DM via X API (`POST /2/dm_conversations/with/:participant_id/messages`) |
| `/api/sync-x-replies` | `POST` | Fetch incoming DMs (`GET /2/dm_conversations/with/:participant_id/dm_events`) |
| `/api/safety` | `GET` / `POST` | Enforce strict anti-spam rate-limits and safety controls |

---

## 4. Verification & Testing

Verify end-to-end functionality using the 7-step test runner:
1. SQLite DB Schema & Table Verification
2. Dynamic Runtime Credentials Storage
3. Live X API Auth Verification (`/api/auth/verify`)
4. Candidate Resolution & Public Post Extraction
5. Gemini LLM Grounded DM Generation
6. Safety & Anti-Duplication Enforcement
7. Real DM Response Synchronization Engine
