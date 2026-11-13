# GenAI Fund FDE Assignment — One-Page Write-Up (v3.0 Live Engine)

**Author:** Nguyễn Trọng Quý

## 1. Approach & System Architecture (v3.0 Live Engine)

To provide GenAI Fund with a production-grade, highly reliable tool to discover and initiate real conversations with AI and robotics builders in Southeast Asia, I built a full-stack system (**app.py**) structured around four stages:

1. **Dual Real-Account OAuth Connection & Verification:**
   - **OAuth 1.0a HMAC-SHA1 User Context:** Accepts consumer keys and user tokens (`X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`) directly for seamless server-to-server API authorization.
   - **OAuth 2.0 PKCE Flow:** Supports browser authorization via `/oauth/x/start` and token exchange callback via `/oauth/x/callback`.
   - **Account Verification:** Authenticates the connected account profile via `GET /2/users/me` at `/api/auth/verify`.

2. **Live X User & Tweet Resolution Engine:**
   - Resolves real candidate handles using `GET /2/users/by/username/:username` to obtain official user profiles and numerical IDs.
   - Fetches candidate posts via `GET /2/users/:id/tweets` or recent post search via `GET /2/tweets/search/recent`.
   - Includes graceful fallbacks via X Public Syndication and oEmbed (`resolve_tweet_oembed_text`).
   - Supports **Strict Live X API Mode (`require_live_x_api`)**: cleanly blocks fallback synthetic data when live access is demanded.

3. **Grounded Personalization & Real Outbound DM Dispatch:**
   - Leverages **Gemini 2.5 Flash** (or deterministic grounded templates) to draft hyper-targeted DMs grounded in candidates' real post evidence.
   - Enforces human-in-the-loop review, anti-spam grounding validation (`verify_dm_grounding`), rate limits, and SQLite `UNIQUE(participant_id)` duplication locks.
   - Dispatches real DMs directly to numerical recipient IDs via `POST /2/dm_conversations/with/:participant_id/messages`.

4. **Real Inbound Reply Synchronization & Intent Triage:**
   - Polls real conversation events via `GET /2/dm_conversations/with/:participant_id/dm_events`.
   - Filters events where `sender_id == participant_id` to automatically capture authentic candidate replies, update lead status, and log complete audit history in SQLite.

---

## 2. Key Technical Choices & Operational Safety

- **Runtime Credentials Storage (`runtime_credentials` table):** Allows live credential injection without restarting the web service.
- **Strict Anti-Spam & Rate-Limit Enforcement:** Hard limits of 15 DMs/15m and 1,440 DMs/24h with SHA-256 message deduplication.
- **Automated Self-Test Suite:** 7-step test runner (`run_self_test`) covering DB schema, auth verification, candidate lookup, LLM grounding, safety constraints, outbound messaging, and response sync.
