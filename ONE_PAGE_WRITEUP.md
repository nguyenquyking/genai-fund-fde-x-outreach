# GenAI Fund FDE Assignment — One-Page Write-Up
**Author:** Nguyễn Trọng Quý

## 1. Approach & System Architecture# GenAI Fund FDE Assignment — One-Page Write-Up (v2.0)
**Author:** Nguyễn Trọng Quý

## 1. Approach & System Architecture (v2.0)
To give GenAI Fund a usable, reliable tool to initiate real conversations with AI and robotics builders in Southeast Asia, I built a single-command **FastAPI + SQLite + Interactive Operator Console** (`app.py`) structured around four stages:
1. **Hybrid Seed Discovery & 4-Pillar Explainable Scoring (0–100):** Accepts target segment queries and seed X handles (`GET /2/users/by` when live token is configured + pre-seeded Southeast Asia AI/Robotics dataset). Every candidate is classified by role archetype (*Founder / Spinout Builder*, *AI & Robotics Researcher*, *AI Infra Engineer*, or *Noise*) and scored across four transparent pillars: **Technical Depth (0–35)**, **SEA Ecosystem Fit (0–25)**, **Conversation Readiness Hook (0–25)**, and **Signal-to-Noise Specificity (0–15)**.
2. **Evidence-Grounded Personalisation + 5-Point AI Output Verifier:** Passes the candidate's bio and highest-signal recent post into `gemini-2.5-flash` (with a deterministic evidence-template fallback when offline) to draft a concise DM referencing real metrics (*19ms Jetson Orin latency*, *FP4 KV-cache throughput*, *$120 tactile sensor BOM*). Before human review, an automated verifier (`verify_dm_grounding`) audits every draft across 5 rules: *Evidence Token Anchor*, *Zero Invented Familiarity (anti-cliché filter)*, *Question Hook (`?`)*, *Length Cap (60–450 chars)*, and *No Cold Link Spam*.
3. **Human-in-the-Loop Gate & Multi-Layer Dispatch Guardrails:** Operators edit, regenerate, approve, reject, or block drafts in the web console. Approved DMs are sent via X API v2 (`POST /2/dm_conversations/with/:participant_id/messages`) or Safe Sandbox Mode. Four hard locks run before every send: (a) SQLite `UNIQUE(participant_id)` + SHA-256 digest lock preventing duplicate DMs, (b) Controlled Test Account Allowlist check, (c) explicit `status == 'approved'` check, and (d) rolling 15-minute (`15/15m`) & 24-hour (`1,440/24h`) rate-limit enforcement.
4. **Live `GET /2/dm_events` Reply Sync, Intent Triage & Audit Trail:** Polls or simulates inbound replies, classifies intent (*Warm Interest / Pilot Question* -> `needs_attention`, *Opt-out* -> `blocked`, *General Reply* -> `replied`), logs all state transitions to `audit_logs`, and exports full campaign reports to CSV (`/api/export.csv`).

## 2. Key Trade-Offs & Practical Choices
- **Single-File FastAPI + Embedded SQLite (WAL) vs. Distributed Stack:** Evaluators can clone and run the tool in under 5 minutes with zero Docker or cloud DB friction while retaining ACID transactions and hard `UNIQUE` anti-duplication locks.
- **Hybrid Live X API v2 + Controlled Test Sandbox:** Defaults to `enforce_test_only=true` with a pre-populated SEA AI/Robotics cohort, a 1-click *Add Controlled Test Account* form, and a *Test Duplicate Send Block* diagnostic button so reviewers can verify both happy paths and blocked edge cases safely.
- **Mandatory Human Approval + Link-Free First DM:** Cold DMs with links trigger spam filters and incur a $0.20 link surcharge on X's 2026 rate card; enforcing human review and link-free opening questions maximizes reply rates and account safety.

## 3. Operating Costs & Rate Limits (2026 Pricing)
- **X API v2 Reads (100 users + 500 posts):** $0.010/user + $0.005/post = **$3.50**
- **X API v2 DM Sends (100 approved DMs):** $0.015/DM (capped at 15/15m & 1,440/24h) = **$1.50**
- **Gemini 2.5 Flash Personalisation (100 drafts):** **$0.00** (Free Tier) or **$0.05** (Paid Tier: $0.30/1M in, $2.50/1M out)
- **Total per 100 Qualified Prospects:** **~$5.05** on Pay-Per-Use.

## 4. What Comes Next
1. OAuth 2.0 PKCE `/oauth/x/login` flow with encrypted refresh-token rotation (`offline.access`).
2. Scheduled 5-minute polling worker for `GET /2/dm_events` with Slack/Notion CRM webhook alerts.
3. Citation-verified graph expansion across followers/co-authors of warm responders.

## 5. How AI Tools Were Used & Verified
- Used AI to verify 2026 X API v2 DM endpoint specs/rate limits, design the 4-pillar scoring rubric, and build the FastAPI/SQLite state machine.
- Verified via `python3 app.py --self-test` (6-stage automated verification suite testing discovery scoring, 5-point AI grounding checks, unapproved-send blocking, SQLite `UNIQUE(participant_id)` duplicate-send blocking, non-allowlisted stranger blocking, and reply intent triage).
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
