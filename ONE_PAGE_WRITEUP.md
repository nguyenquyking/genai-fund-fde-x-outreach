# GenAI Fund FDE Assignment — One-Page Write-Up
**Author:** Nguyễn Trọng Quý

## 1. Approach & System Architecture
To give GenAI Fund a working tool to initiate conversations with AI and robotics builders in Southeast Asia, I built a single-command **FastAPI + SQLite + Interactive Web Console** (`app.py`) around four stages:
1. **Seed & Segment Discovery with Noise Filtering:** Scores candidates (0–100) across technical depth (Embodied AI/VLA/SLAM, LLM inference, agent evaluation), Southeast Asia footprint (Vietnam, Singapore, Indonesia), and active hooks (seeking pilots, lab spinouts, open-source benchmarks), while filtering out token/promo noise.
2. **Evidence-Grounded Personalisation:** Extracts verbatim recent posts + bio into `gemini-2.5-flash` (with deterministic evidence fallback) to draft a <420-character DM referencing real metrics and ending with a specific question.
3. **Human-in-the-Loop Approval & Hard Deduplication:** Operators edit, approve, reject, or block drafts before dispatch via X API v2 (`POST /2/dm_conversations/with/:participant_id/messages`) or Safe Test Sandbox. A database-level `UNIQUE(participant_id)` lock in `sent_messages` guarantees the system never double-messages anyone.
4. **Reply Triage & Rate-Limit Telemetry:** Tracks sent messages and inbound replies (`GET /2/dm_events`), flagging warm replies under **Needs Attention** and opt-outs under **Blocked**.

## 2. Key Trade-Offs & Practical Choices
- **Single-File FastAPI + Embedded SQLite vs. Multi-Container Stack:** Evaluators can clone and run the prototype in under 5 minutes with zero Docker/Postgres setup while retaining ACID transactions and hard `UNIQUE` deduplication constraints.
- **Hybrid Live X API v2 + Controlled Test Allowlist:** Enforces an explicit test-handle allowlist and includes pre-seeded SEA AI/Robotics profiles plus a 1-click *Add Controlled Test Account* and *Simulate Reply* workflow for safe end-to-end verification.
- **Strict Human Approval Gate vs. Autonomous Sending:** Protects account reputation and ensures 100% factual personalisation.

## 3. Operating Costs & Rate Limits (2026 Pricing)
- **X API v2 Reads (100 users + 500 posts):** $0.010/user + $0.005/post = **$3.50**
- **X API v2 DM Sends (100 approved DMs):** $0.015/DM (capped at 15/15m & 1,440/24h) = **$1.50**
- **Gemini 2.5 Flash Personalisation (100 drafts):** **$0.00** (Free Tier) or **$0.05** (Paid Tier: $0.30/1M in, $2.50/1M out)
- **Total per 100 Qualified Prospects:** **~$5.05** on Pay-Per-Use (no legacy $200/mo flat subscription required).

## 4. What Comes Next
1. OAuth 2.0 PKCE `/oauth/x/login` flow with encrypted refresh token rotation.
2. Background 5-minute polling worker for `GET /2/dm_events` with Slack/Notion webhook alerts.
3. Graph expansion across followers/following of high-fit replies and GitHub/arXiv bio links.

## 5. How AI Tools Were Used & Verified
- Used AI to verify 2026 X API v2 DM endpoint specs/rate limits, scaffold the FastAPI/SQLite state machine, and build the operator UI.
- Verified via `python3 app.py --self-test` (automated test suite asserting candidate scoring, spam filtering, approval, SQLite `UNIQUE(participant_id)` anti-duplication lock, and reply triage).
