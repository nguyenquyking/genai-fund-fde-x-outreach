# genai-fund-fde-x-outreach
AI &amp; Robotics X/Twitter Discovery and Personalised DM Outreach Prototype – GenAI Fund FDE Assignment
# GenAI Fund — AI & Robotics X/Twitter Outreach Prototype

A working prototype built for the **GenAI Fund Forward Deployed Engineer (FDE) Take-Home Assignment**. It discovers relevant AI and robotics builders, founders, and researchers on X (Twitter), explains why they fit using verifiable post evidence, drafts grounded personalised DMs for human approval, enforces strict anti-duplication and rate-limit rules, and tracks replies requiring team attention.

## 1. Quick Setup (Under 5 Minutes)

### Prerequisites
- Python 3.10+
- No external database server required (uses embedded SQLite with WAL mode and `UNIQUE` constraint deduplication).

### Installation & Run
```bash
git clone <repo_url>
cd genai-fund-fde-x-outreach
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py --self-test
python3 app.py --host 127.0.0.1 --port 8000
```
Open `127.0.0.1:8000` in your browser.

## 2. Optional API Keys & Account Requirements
```bash
export GEMINI_API_KEY="your_gemini_api_key"
export X_USER_ACCESS_TOKEN="your_x_oauth2_user_access_token"
```
- **X API v2 (`POST /2/dm_conversations/with/:participant_id/messages`):** Pay-Per-Use credit model ($0.015/DM, $0.005/post read, $0.010/user read; rate limit 15 DMs / 15m and 1,440 DMs / 24h) using OAuth 2.0 User Context token (`dm.write`, `dm.read`, `tweet.read`, `users.read`).
- **Gemini API (`gemini-2.5-flash`):** Free tier available in Google AI Studio or paid tier ($0.30/1M input, $2.50/1M output).

## 3. Core Capabilities & Guardrails
- **Evidence-Based Fit Scoring (0–100):** Evaluates bio and recent posts for Embodied AI/Robotics/LLM Infra signals, Southeast Asia footprint, and active pilot/research hooks while filtering crypto/promo spam.
- **Grounded Personalisation:** Every draft cites a real post/metric; zero invented familiarity.
- **Human-in-the-Loop Approval Queue:** Edit, Approve, Reject, or Block prospects before any DM is sent.
- **Hard Deduplication Lock:** SQLite `UNIQUE(participant_id)` constraint in `sent_messages` + SHA-256 digest guarantees no one is ever double-messaged.
- **Controlled Test Account Allowlist:** Default `enforce_test_only=true` blocks sending to any handle outside the controlled test allowlist.
