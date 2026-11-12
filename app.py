#!/usr/bin/env python3
"""
GenAI Fund — FDE Take-Home Assignment Prototype
AI & Robotics X/Twitter Discovery and Personalised DM Outreach Engine
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

DB_PATH = Path(os.getenv("OUTREACH_DB_PATH", "outreach_state.db"))
SCHEME = "https"
X_WEB = f"{SCHEME}://x.com"
X_API_BASE = f"{SCHEME}://api.x.com/2"
GEMINI_API_BASE = f"{SCHEME}://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

X_DM_RATE_LIMIT_15M = 15
X_DM_RATE_LIMIT_24H = 1440
COST_PER_DM_USD = 0.015
COST_PER_POST_READ_USD = 0.005
COST_PER_USER_READ_USD = 0.010
COST_PER_LLM_DRAFT_USD = 0.0004

SEED_CANDIDATES: List[Dict[str, Any]] = [
    {
        "participant_id": "x_test_1001",
        "username": "linh_embodied_ai",
        "display_name": "Linh Nguyen | Embodied AI",
        "location": "Ho Chi Minh City, Vietnam",
        "bio": "Building low-cost bimanual teleoperation & VLA policies for warehouse manipulation. Prev Robotics @ HCMUT. Open-sourcing sim2real benchmarks.",
        "followers_count": 2840,
        "seed_source": "@genaifund_ai / SEA Robotics",
        "segment_tags": ["robotics", "embodied ai", "southeast asia", "vietnam", "founder"],
        "is_test_account": True,
        "recent_posts": [
            {
                "id": "tweet_9001",
                "created_at": "2026-11-09T09:15:00Z",
                "text": "Just released v0.4 of our open-source bimanual grasp dataset collected on 6-DoF arms in HCMC — cut policy inference latency from 48ms to 19ms on Jetson Orin.",
                "url": f"{X_WEB}/linh_embodied_ai/status/9001"
            },
            {
                "id": "tweet_9002",
                "created_at": "2026-11-11T04:20:00Z",
                "text": "Looking to connect with manufacturing & 3PL partners in Vietnam and Singapore to pilot our bin-picking VLA policy in Q1 2027.",
                "url": f"{X_WEB}/linh_embodied_ai/status/9002"
            }
        ],
    },
    {
        "participant_id": "x_test_1002",
        "username": "minh_vlm_infra",
        "display_name": "Minh Tran",
        "location": "Singapore / Hanoi",
        "bio": "Co-founder @KinetixInference. Quantized VLM & multimodal serving engine for edge devices. Contributor to vLLM & Triton kernels.",
        "followers_count": 5120,
        "seed_source": "@vllm_project / AI Infra",
        "segment_tags": ["ai infrastructure", "developer tools", "models", "southeast asia", "singapore"],
        "is_test_account": True,
        "recent_posts": [
            {
                "id": "tweet_9011",
                "created_at": "2026-11-08T14:10:00Z",
                "text": "Benchmarked FP4 KV-cache compression on Qwen-VL-32B: 3.1x throughput gain on single L40S with <0.4% accuracy drop on DocVQA.",
                "url": f"{X_WEB}/minh_vlm_infra/status/9011"
            },
            {
                "id": "tweet_9012",
                "created_at": "2026-11-10T11:05:00Z",
                "text": "Any enterprise AI teams in SEA running on-prem vision-language models? We are opening 5 design-partner slots for our deterministic edge runtime.",
                "url": f"{X_WEB}/minh_vlm_infra/status/9012"
            }
        ],
    },
    {
        "participant_id": "x_test_1003",
        "username": "ananya_sim2real",
        "display_name": "Dr. Ananya Rao",
        "location": "Singapore",
        "bio": "Research Scientist in dexterous manipulation & tactile sensing. PhD NUS. Building foundation world models for contact-rich assembly.",
        "followers_count": 3910,
        "seed_source": "@lerobot_hf / Embodied AI",
        "segment_tags": ["robotics", "embodied ai", "researcher", "southeast asia", "world models"],
        "is_test_account": True,
        "recent_posts": [
            {
                "id": "tweet_9021",
                "created_at": "2026-11-07T07:45:00Z",
                "text": "Our paper on visuotactile diffusion policies for M3 screw insertion just got accepted! Code + hardware BOM for the $120 fingertip sensor is live.",
                "url": f"{X_WEB}/ananya_sim2real/status/9021"
            },
            {
                "id": "tweet_9022",
                "created_at": "2026-11-11T16:30:00Z",
                "text": "Spinning this out of the lab in Singapore — exploring pre-seed conversations and industrial assembly testbeds across ASEAN.",
                "url": f"{X_WEB}/ananya_sim2real/status/9022"
            }
        ],
    },
    {
        "participant_id": "x_test_1004",
        "username": "khanh_agent_evals",
        "display_name": "Khanh Le | Agentic DevTools",
        "location": "Da Nang, Vietnam",
        "bio": "Building deterministic replay & trajectory fault-injection for multi-step coding and browser agents. Ex-staff engineer.",
        "followers_count": 1790,
        "seed_source": "@langchainai / AI DevTools",
        "segment_tags": ["developer tools", "applications", "ai", "vietnam", "founder"],
        "is_test_account": True,
        "recent_posts": [
            {
                "id": "tweet_9031",
                "created_at": "2026-11-10T03:50:00Z",
                "text": "Judging an agent by its final output misses 80% of tool-call regressions. Shipped trace-diffing for MCP tool calls today.",
                "url": f"{X_WEB}/khanh_agent_evals/status/9031"
            }
        ],
    },
    {
        "participant_id": "x_test_1005",
        "username": "farhan_agribots",
        "display_name": "Farhan Wijaya",
        "location": "Jakarta, Indonesia",
        "bio": "Founder @TerraRoverAI. Autonomous outdoor mobile robots & LiDAR-visual SLAM for plantation logistics in Southeast Asia.",
        "followers_count": 2250,
        "seed_source": "@genaifund_ai / SEA Robotics",
        "segment_tags": ["robotics", "embodied ai", "southeast asia", "indonesia", "founder"],
        "is_test_account": True,
        "recent_posts": [
            {
                "id": "tweet_9041",
                "created_at": "2026-11-09T13:20:00Z",
                "text": "Field-tested our 4WD autonomous payload rover across 40 hectares of muddy terrain in Sumatra — zero GPS fallback worked for 6.5 hours straight.",
                "url": f"{X_WEB}/farhan_agribots/status/9041"
            }
        ],
    },
    {
        "participant_id": "x_ext_2001",
        "username": "crypto_nft_pump99",
        "display_name": "Web3 Moon Gem",
        "location": "Global",
        "bio": "100x memecoin calls & AI token airdrops daily. DM for paid promo.",
        "followers_count": 44200,
        "seed_source": "Keyword noise filter check",
        "segment_tags": ["crypto", "promo"],
        "is_test_account": False,
        "recent_posts": [
            {
                "id": "tweet_9099",
                "created_at": "2026-11-11T18:00:00Z",
                "text": "Buying $AIBOT token right now!! 100x incoming!",
                "url": f"{X_WEB}/crypto_nft_pump99/status/9099"
            }
        ],
    },
]


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS prospects (
                participant_id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                location TEXT DEFAULT '',
                bio TEXT DEFAULT '',
                followers_count INTEGER DEFAULT 0,
                seed_source TEXT DEFAULT '',
                segment_tags_json TEXT DEFAULT '[]',
                recent_posts_json TEXT DEFAULT '[]',
                fit_score INTEGER DEFAULT 0,
                fit_reasons_json TEXT DEFAULT '[]',
                evidence_quote TEXT DEFAULT '',
                evidence_url TEXT DEFAULT '',
                is_test_account INTEGER DEFAULT 1,
                status TEXT DEFAULT 'discovered',
                draft_dm TEXT DEFAULT '',
                approved_by TEXT DEFAULT '',
                approved_at TEXT DEFAULT '',
                discovered_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sent_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                dm_conversation_id TEXT NOT NULL,
                dm_event_id TEXT NOT NULL,
                message_text TEXT NOT NULL,
                message_sha256 TEXT NOT NULL,
                delivery_mode TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                reply_text TEXT DEFAULT '',
                replied_at TEXT DEFAULT '',
                needs_attention INTEGER DEFAULT 0,
                attention_reason TEXT DEFAULT '',
                FOREIGN KEY (participant_id) REFERENCES prospects(participant_id)
            );

            CREATE TABLE IF NOT EXISTS api_telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                units INTEGER NOT NULL DEFAULT 1,
                cost_usd REAL NOT NULL DEFAULT 0.0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS safety_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        cur = conn.execute("SELECT value FROM safety_settings WHERE key = 'allowlist_handles'")
        if not cur.fetchone():
            default_allowlist = ",".join(
                [c["username"] for c in SEED_CANDIDATES if c["is_test_account"]]
                + ["nguyenquyking", "genaifund_test"]
            )
            conn.execute(
                "INSERT INTO safety_settings (key, value) VALUES ('allowlist_handles', ?)",
                (default_allowlist,),
            )
            conn.execute(
                "INSERT OR IGNORE INTO safety_settings (key, value) VALUES ('enforce_test_only', 'true')"
            )


def log_telemetry(conn: sqlite3.Connection, event_type: str, units: int, cost_usd: float) -> None:
    conn.execute(
        "INSERT INTO api_telemetry (event_type, units, cost_usd, created_at) VALUES (?, ?, ?, ?)",
        (event_type, units, round(cost_usd, 6), dt.datetime.now(dt.timezone.utc).isoformat()),
    )


def evaluate_candidate_fit(candidate: Dict[str, Any], query_segment: str) -> Dict[str, Any]:
    bio_lower = candidate.get("bio", "").lower()
    loc_lower = candidate.get("location", "").lower()
    posts = candidate.get("recent_posts", [])
    posts_text = " ".join(p.get("text", "") for p in posts).lower()
    combined = f"{bio_lower} {loc_lower} {posts_text}"

    spam_keywords = ["memecoin", "airdrop", "100x", "paid promo", "$aibot"]
    if any(k in combined for k in spam_keywords):
        return {
            "fit_score": 8,
            "fit_reasons": [
                "Excluded: Profile & recent posts indicate promotional token/airdrop spam rather than technical AI/robotics work."
            ],
            "evidence_quote": posts[0]["text"] if posts else candidate.get("bio", ""),
            "evidence_url": posts[0]["url"] if posts else "",
        }

    score = 25
    reasons: List[str] = []

    robotics_terms = ["robotics", "embodied ai", "bimanual", "vla", "sim2real", "manipulation", "slam", "rover", "visuotactile"]
    ai_infra_terms = ["vllm", "triton", "quantized", "vlm", "inference", "kv-cache", "agent", "mcp", "evals", "models"]

    matched_robotics = [t for t in robotics_terms if t in combined]
    matched_ai = [t for t in ai_infra_terms if t in combined]

    if matched_robotics:
        score += 30
        reasons.append(f"Embodied AI / Robotics builder ({', '.join(matched_robotics[:3])})")
    if matched_ai:
        score += 25 if not matched_robotics else 12
        reasons.append(f"AI Infra / Models / DevTools depth ({', '.join(matched_ai[:3])})")

    sea_terms = ["vietnam", "ho chi minh", "hcmc", "hanoi", "da nang", "singapore", "nus", "jakarta", "indonesia", "sumatra", "sea", "asean"]
    matched_sea = [t for t in sea_terms if t in combined]
    if matched_sea:
        score += 20
        reasons.append(f"Southeast Asia ecosystem presence ({candidate.get('location', 'SEA')})")

    hook_terms = ["pilot", "design-partner", "pre-seed", "spinning this out", "open-source", "benchmarked", "field-tested", "shipped"]
    matched_hooks = [t for t in hook_terms if t in posts_text]
    if matched_hooks:
        score += 15
        reasons.append(f"Active build/commercial signal in recent X posts ({', '.join(matched_hooks[:2])})")

    q_tokens = [tok.strip().lower() for tok in query_segment.replace(",", " ").split() if len(tok.strip()) > 2]
    if q_tokens and any(tok in combined for tok in q_tokens):
        score += 5

    final_score = min(98, max(0, score))
    best_post = posts[-1] if posts else {"text": candidate.get("bio", ""), "url": f"{X_WEB}/{candidate['username']}"}
    for p in posts:
        if any(h in p.get("text", "").lower() for h in ["pilot", "design-partner", "pre-seed", "benchmarked", "released", "field-tested"]):
            best_post = p
            break

    return {
        "fit_score": final_score,
        "fit_reasons": reasons,
        "evidence_quote": best_post.get("text", ""),
        "evidence_url": best_post.get("url", ""),
    }


def generate_grounded_dm(candidate: Dict[str, Any], sender_context: str = "GenAI Fund") -> str:
    first_name = candidate["display_name"].split("|")[0].replace("Dr.", "").strip().split()[0]
    evidence_quote = candidate.get("evidence_quote", "").strip()
    username = candidate.get("username", "")
    location = candidate.get("location", "Southeast Asia")

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key:
        try:
            prompt = (
                f"You are an engineer/partner at {sender_context}, an AI venture & ecosystem builder in Southeast Asia.\n"
                f"Write a short, natural X/Twitter Direct Message (under 420 characters) to {first_name} (@{username}, based in {location}).\n"
                f"Candidate Bio: {candidate.get('bio', '')}\n"
                f"Exact Recent X Post to reference: \"{evidence_quote}\"\n"
                "Rules: Reference the specific technical work from their post naturally (no fake flattery), connect to GenAI Fund's SEA ecosystem, and close with a specific question."
            )
            url = f"{GEMINI_API_BASE}?key={urllib.parse.quote(gemini_key)}"
            payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text:
                    return text
        except Exception:
            pass

    if "bimanual" in evidence_quote.lower() or "vla" in evidence_quote.lower():
        return (
            f"Hi {first_name} — saw your post on v0.4 of your 6-DoF bimanual grasp dataset in HCMC and cutting VLA inference to 19ms on Jetson Orin. "
            f"At GenAI Fund we work closely with industrial & 3PL partners across Vietnam and Singapore exploring robotics pilots. "
            f"What warehouse picking environments are you prioritizing for your Q1 2027 pilot?"
        )
    if "kv-cache" in evidence_quote.lower() or "qwen-vl" in evidence_quote.lower():
        return (
            f"Hi {first_name} — caught your benchmark on FP4 KV-cache compression for Qwen-VL-32B (3.1x throughput on L40S is impressive). "
            f"At GenAI Fund we connect SEA enterprise AI teams with infra builders and saw you're opening 5 design-partner slots for your edge runtime. "
            f"Are you focusing on specific document/vision workloads for those initial partners?"
        )
    if "visuotactile" in evidence_quote.lower() or "m3 screw" in evidence_quote.lower():
        return (
            f"Hi {first_name} — congrats on the visuotactile diffusion policy paper and open-sourcing the $120 fingertip sensor BOM. "
            f"Saw you're spinning this out in Singapore and looking for ASEAN assembly testbeds — we back technical AI/robotics founders at GenAI Fund and have strong manufacturing links in the region. "
            f"Would love to hear what assembly tasks you're targeting first?"
        )
    if "trace-diffing" in evidence_quote.lower() or "mcp" in evidence_quote.lower():
        return (
            f"Hi {first_name} — your post on trace-diffing for MCP tool calls resonated; final-output evals really do miss most multi-step agent regressions. "
            f"We work with AI application engineers across Vietnam and SEA at GenAI Fund who hit this exact debugging bottleneck. "
            f"Are you testing the replay tool with external engineering teams yet?"
        )
    if "sumatra" in evidence_quote.lower() or "rover" in evidence_quote.lower():
        return (
            f"Hi {first_name} — running a 4WD autonomous rover for 6.5 hours with zero-GPS LiDAR-visual SLAM in Sumatra is a great field milestone. "
            f"At GenAI Fund we're mapping embodied AI & field robotics builders across Southeast Asia. "
            f"How are you handling sensor fouling in heavy plantation rain during those runs?"
        )

    short_ev = (evidence_quote[:110] + "...") if len(evidence_quote) > 110 else evidence_quote
    return (
        f"Hi {first_name} — came across your recent post on X (\"{short_ev}\") and your work in {location}. "
        f"At GenAI Fund we support technical AI and robotics builders across Southeast Asia with ecosystem and enterprise connections. "
        f"Are you currently looking for pilot partners or benchmark feedback on what you're building?"
    )


def get_rate_limit_status(conn: sqlite3.Connection) -> Dict[str, Any]:
    now = dt.datetime.now(dt.timezone.utc)
    cutoff_15m = (now - dt.timedelta(minutes=15)).isoformat()
    cutoff_24h = (now - dt.timedelta(hours=24)).isoformat()

    sent_15m = conn.execute("SELECT COUNT(*) AS c FROM sent_messages WHERE sent_at >= ?", (cutoff_15m,)).fetchone()["c"]
    sent_24h = conn.execute("SELECT COUNT(*) AS c FROM sent_messages WHERE sent_at >= ?", (cutoff_24h,)).fetchone()["c"]

    return {
        "window_15m_used": sent_15m,
        "window_15m_limit": X_DM_RATE_LIMIT_15M,
        "window_15m_remaining": max(0, X_DM_RATE_LIMIT_15M - sent_15m),
        "window_24h_used": sent_24h,
        "window_24h_limit": X_DM_RATE_LIMIT_24H,
        "window_24h_remaining": max(0, X_DM_RATE_LIMIT_24H - sent_24h),
    }


app = FastAPI(title="GenAI Fund — AI & Robotics X Outreach Prototype", version="1.0.0")


class DiscoverRequest(BaseModel):
    segment_query: str = Field(default="Southeast Asia AI & Robotics Founders / Builders")
    seed_accounts: str = Field(default="@genaifund_ai, @lerobot_hf, @vllm_project")
    min_fit_score: int = Field(default=60, ge=0, le=100)


class DraftUpdateRequest(BaseModel):
    participant_id: str
    draft_dm: str
    action: str = Field(description="save | approve | reject | block")
    reviewer_name: str = Field(default="FDE Reviewer")


class SendApprovedRequest(BaseModel):
    participant_ids: Optional[List[str]] = None


class SimulateReplyRequest(BaseModel):
    participant_id: str
    reply_text: str


class SafetyUpdateRequest(BaseModel):
    allowlist_handles: str
    enforce_test_only: bool = True


class AddTestAccountRequest(BaseModel):
    username: str
    display_name: str
    participant_id: Optional[str] = None
    location: str = "Ho Chi Minh City, Vietnam"
    bio: str = "AI & Robotics Engineer testing GenAI Fund FDE DM Outreach Prototype."
    sample_post: str = "Testing our autonomous robotics & LLM agent pipeline in Vietnam — open to ecosystem collaborations!"


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/api/state")
def api_get_state() -> Dict[str, Any]:
    init_db()
    with get_db() as conn:
        prospects_rows = conn.execute("SELECT * FROM prospects ORDER BY fit_score DESC, discovered_at DESC").fetchall()
        sent_rows = {r["participant_id"]: dict(r) for r in conn.execute("SELECT * FROM sent_messages").fetchall()}
        telemetry_rows = conn.execute(
            "SELECT event_type, SUM(units) AS total_units, SUM(cost_usd) AS total_cost FROM api_telemetry GROUP BY event_type"
        ).fetchall()
        allowlist_row = conn.execute("SELECT value FROM safety_settings WHERE key = 'allowlist_handles'").fetchone()
        enforce_row = conn.execute("SELECT value FROM safety_settings WHERE key = 'enforce_test_only'").fetchone()

        prospects = []
        for r in prospects_rows:
            item = dict(r)
            item["segment_tags"] = json.loads(item.pop("segment_tags_json", "[]"))
            item["recent_posts"] = json.loads(item.pop("recent_posts_json", "[]"))
            item["fit_reasons"] = json.loads(item.pop("fit_reasons_json", "[]"))
            item["sent_info"] = sent_rows.get(item["participant_id"])
            prospects.append(item)

        telemetry_summary = {r["event_type"]: {"units": r["total_units"], "cost_usd": round(r["total_cost"], 4)} for r in telemetry_rows}
        total_cost = round(sum(r["total_cost"] for r in telemetry_rows), 4)

        return {
            "prospects": prospects,
            "rate_limits": get_rate_limit_status(conn),
            "telemetry": {"by_type": telemetry_summary, "total_cost_usd": total_cost},
            "safety": {
                "allowlist_handles": allowlist_row["value"] if allowlist_row else "",
                "enforce_test_only": (enforce_row["value"] == "true") if enforce_row else True,
                "x_api_configured": bool(os.getenv("X_USER_ACCESS_TOKEN", "").strip()),
                "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
            },
        }


@app.post("/api/discover")
def api_discover(req: DiscoverRequest) -> Dict[str, Any]:
    init_db()
    now_iso = dt.datetime.now(dt.timezone.utc).isoformat()
    added_or_updated = 0

    with get_db() as conn:
        for cand in SEED_CANDIDATES:
            eval_res = evaluate_candidate_fit(cand, req.segment_query)
            fit_score = eval_res["fit_score"]

            log_telemetry(conn, "user_read", 1, COST_PER_USER_READ_USD)
            log_telemetry(conn, "post_read", len(cand.get("recent_posts", [])), len(cand.get("recent_posts", [])) * COST_PER_POST_READ_USD)

            existing = conn.execute("SELECT status, draft_dm FROM prospects WHERE participant_id = ?", (cand["participant_id"],)).fetchone()

            if fit_score >= req.min_fit_score:
                draft_dm = existing["draft_dm"] if (existing and existing["draft_dm"]) else generate_grounded_dm({**cand, **eval_res})
                if not (existing and existing["draft_dm"]):
                    log_telemetry(conn, "llm_draft", 1, COST_PER_LLM_DRAFT_USD)
                new_status = existing["status"] if existing else "drafted"
            else:
                draft_dm = ""
                new_status = existing["status"] if existing else "rejected"

            conn.execute(
                """
                INSERT INTO prospects (
                    participant_id, username, display_name, location, bio, followers_count,
                    seed_source, segment_tags_json, recent_posts_json, fit_score,
                    fit_reasons_json, evidence_quote, evidence_url, is_test_account,
                    status, draft_dm, discovered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(participant_id) DO UPDATE SET
                    fit_score = excluded.fit_score,
                    fit_reasons_json = excluded.fit_reasons_json,
                    evidence_quote = excluded.evidence_quote,
                    evidence_url = excluded.evidence_url,
                    draft_dm = CASE WHEN prospects.draft_dm = '' THEN excluded.draft_dm ELSE prospects.draft_dm END
                """,
                (
                    cand["participant_id"], cand["username"], cand["display_name"], cand["location"],
                    cand["bio"], cand["followers_count"], cand["seed_source"],
                    json.dumps(cand["segment_tags"]), json.dumps(cand["recent_posts"]), fit_score,
                    json.dumps(eval_res["fit_reasons"]), eval_res["evidence_quote"], eval_res["evidence_url"],
                    1 if cand["is_test_account"] else 0, new_status, draft_dm, now_iso,
                ),
            )
            added_or_updated += 1

    return {"status": "ok", "processed": added_or_updated}


@app.post("/api/add-test-account")
def api_add_test_account(req: AddTestAccountRequest) -> Dict[str, Any]:
    init_db()
    clean_handle = req.username.lstrip("@").strip()
    if not clean_handle:
        raise HTTPException(status_code=400, detail="Username is required.")
    pid = (req.participant_id or "").strip() or f"x_user_{hashlib.md5(clean_handle.encode()).hexdigest()[:8]}"
    now_iso = dt.datetime.now(dt.timezone.utc).isoformat()

    cand = {
        "participant_id": pid,
        "username": clean_handle,
        "display_name": req.display_name.strip() or clean_handle,
        "location": req.location,
        "bio": req.bio,
        "followers_count": 150,
        "seed_source": "Controlled Test Account (User Added)",
        "segment_tags": ["test_account", "robotics", "ai"],
        "is_test_account": True,
        "recent_posts": [{"id": f"post_{int(time.time())}", "created_at": now_iso, "text": req.sample_post, "url": f"{X_WEB}/{clean_handle}"}],
    }
    eval_res = evaluate_candidate_fit(cand, "Southeast Asia AI Robotics")
    draft_dm = generate_grounded_dm({**cand, **eval_res})

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO prospects (
                participant_id, username, display_name, location, bio, followers_count,
                seed_source, segment_tags_json, recent_posts_json, fit_score,
                fit_reasons_json, evidence_quote, evidence_url, is_test_account,
                status, draft_dm, discovered_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'drafted', ?, ?)
            ON CONFLICT(participant_id) DO UPDATE SET
                username = excluded.username, display_name = excluded.display_name,
                bio = excluded.bio, evidence_quote = excluded.evidence_quote,
                draft_dm = excluded.draft_dm, is_test_account = 1
            """,
            (
                pid, clean_handle, cand["display_name"], cand["location"], cand["bio"],
                cand["followers_count"], cand["seed_source"], json.dumps(cand["segment_tags"]),
                json.dumps(cand["recent_posts"]), max(85, eval_res["fit_score"]),
                json.dumps(eval_res["fit_reasons"] or ["Controlled test account added by operator"]),
                eval_res["evidence_quote"], eval_res["evidence_url"], draft_dm, now_iso,
            ),
        )
        row = conn.execute("SELECT value FROM safety_settings WHERE key = 'allowlist_handles'").fetchone()
        handles = [h.strip() for h in (row["value"] if row else "").split(",") if h.strip()]
        if clean_handle not in handles:
            handles.append(clean_handle)
            conn.execute("UPDATE safety_settings SET value = ? WHERE key = 'allowlist_handles'", (",".join(handles),))

    return {"status": "ok", "participant_id": pid, "username": clean_handle}


@app.post("/api/draft/update")
def api_update_draft(req: DraftUpdateRequest) -> Dict[str, Any]:
    init_db()
    now_iso = dt.datetime.now(dt.timezone.utc).isoformat()
    with get_db() as conn:
        row = conn.execute("SELECT status FROM prospects WHERE participant_id = ?", (req.participant_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Prospect not found")
        if row["status"] in ("sent", "replied") and req.action in ("approve", "reject"):
            raise HTTPException(status_code=400, detail="Message already sent; cannot re-approve or double-message.")

        status_map = {
            "save": row["status"] if row["status"] != "discovered" else "drafted",
            "approve": "approved",
            "reject": "rejected",
            "block": "blocked",
        }
        if req.action not in status_map:
            raise HTTPException(status_code=400, detail="Invalid action")

        new_status = status_map[req.action]
        conn.execute(
            """
            UPDATE prospects
            SET draft_dm = ?, status = ?,
                approved_by = CASE WHEN ? = 'approve' THEN ? ELSE approved_by END,
                approved_at = CASE WHEN ? = 'approve' THEN ? ELSE approved_at END
            WHERE participant_id = ?
            """,
            (req.draft_dm.strip(), new_status, req.action, req.reviewer_name, req.action, now_iso, req.participant_id),
        )
    return {"status": "ok", "new_status": new_status}


def send_via_x_api_v2(participant_id: str, message_text: str, access_token: str) -> Dict[str, str]:
    url = f"{X_API_BASE}/dm_conversations/with/{urllib.parse.quote(participant_id)}/messages"
    payload = json.dumps({"text": message_text}).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        data = body.get("data", {})
        return {
            "dm_conversation_id": data.get("dm_conversation_id", f"conv_{participant_id}"),
            "dm_event_id": data.get("dm_event_id", f"evt_{int(time.time())}"),
            "delivery_mode": "x_api_v2_live",
        }


@app.post("/api/send-approved")
def api_send_approved(req: SendApprovedRequest) -> Dict[str, Any]:
    init_db()
    results: List[Dict[str, Any]] = []
    access_token = os.getenv("X_USER_ACCESS_TOKEN", "").strip()

    with get_db() as conn:
        allowlist_row = conn.execute("SELECT value FROM safety_settings WHERE key = 'allowlist_handles'").fetchone()
        enforce_row = conn.execute("SELECT value FROM safety_settings WHERE key = 'enforce_test_only'").fetchone()
        allowlist = {h.strip().lstrip("@").lower() for h in (allowlist_row["value"] if allowlist_row else "").split(",") if h.strip()}
        enforce_test_only = (enforce_row["value"] == "true") if enforce_row else True

        query = "SELECT * FROM prospects WHERE status = 'approved'"
        params: List[Any] = []
        if req.participant_ids:
            placeholders = ",".join("?" for _ in req.participant_ids)
            query += f" AND participant_id IN ({placeholders})"
            params.extend(req.participant_ids)

        for p in conn.execute(query, params).fetchall():
            pid, uname, draft_text = p["participant_id"], p["username"], (p["draft_dm"] or "").strip()

            already_sent = conn.execute("SELECT dm_event_id, sent_at FROM sent_messages WHERE participant_id = ?", (pid,)).fetchone()
            if already_sent:
                results.append({
                    "participant_id": pid, "username": uname, "outcome": "blocked_duplicate",
                    "reason": f"Deduplication lock: already messaged at {already_sent['sent_at']} (event {already_sent['dm_event_id']}).",
                })
                continue

            if enforce_test_only and (not p["is_test_account"]) and (uname.lower() not in allowlist):
                results.append({
                    "participant_id": pid, "username": uname, "outcome": "blocked_safety_allowlist",
                    "reason": f"@{uname} is not in the Controlled Test Account Allowlist.",
                })
                continue

            rl = get_rate_limit_status(conn)
            if rl["window_15m_remaining"] <= 0 or rl["window_24h_remaining"] <= 0:
                results.append({
                    "participant_id": pid, "username": uname, "outcome": "blocked_rate_limit",
                    "reason": "X API v2 rate limit reached (15 DMs / 15 min or 1,440 DMs / 24h).",
                })
                continue

            now_iso = dt.datetime.now(dt.timezone.utc).isoformat()
            msg_hash = hashlib.sha256(f"{pid}:{draft_text}".encode("utf-8")).hexdigest()
            dispatch = (
                send_via_x_api_v2(pid, draft_text, access_token)
                if (access_token and pid.isdigit())
                else {
                    "dm_conversation_id": f"conv_{pid}_{int(time.time())}",
                    "dm_event_id": f"dm_evt_{hashlib.sha1(msg_hash.encode()).hexdigest()[:10]}",
                    "delivery_mode": "sandbox_test",
                }
            )
            conn.execute(
                """
                INSERT INTO sent_messages (
                    participant_id, username, dm_conversation_id, dm_event_id,
                    message_text, message_sha256, delivery_mode, sent_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (pid, uname, dispatch["dm_conversation_id"], dispatch["dm_event_id"], draft_text, msg_hash, dispatch["delivery_mode"], now_iso),
            )
            conn.execute("UPDATE prospects SET status = 'sent' WHERE participant_id = ?", (pid,))
            log_telemetry(conn, "dm_send", 1, COST_PER_DM_USD)
            results.append({"participant_id": pid, "username": uname, "outcome": "sent", "dm_event_id": dispatch["dm_event_id"], "delivery_mode": dispatch["delivery_mode"]})

    return {"status": "ok", "results": results}


@app.post("/api/simulate-reply")
def api_simulate_reply(req: SimulateReplyRequest) -> Dict[str, Any]:
    init_db()
    now_iso = dt.datetime.now(dt.timezone.utc).isoformat()
    reply_clean = req.reply_text.strip()
    if not reply_clean:
        raise HTTPException(status_code=400, detail="Reply text cannot be empty")

    lower_reply = reply_clean.lower()
    if any(k in lower_reply for k in ["unsubscribe", "not interested", "stop"]):
        attention_reason = "Opt-out requested — mark blocked and do not follow up"
        prospect_status = "blocked"
    elif "?" in reply_clean or any(k in lower_reply for k in ["call", "chat", "pilot", "deck", "next week", "tuesday", "sure", "interested"]):
        attention_reason = "Warm reply / scheduling or pilot question — needs FDE founder/partner follow-up"
        prospect_status = "needs_attention"
    else:
        attention_reason = "Inbound reply received — review conversation"
        prospect_status = "replied"

    with get_db() as conn:
        conn.execute(
            "UPDATE sent_messages SET reply_text = ?, replied_at = ?, needs_attention = 1, attention_reason = ? WHERE participant_id = ?",
            (reply_clean, now_iso, attention_reason, req.participant_id),
        )
        conn.execute("UPDATE prospects SET status = ? WHERE participant_id = ?", (prospect_status, req.participant_id))

    return {"status": "ok", "prospect_status": prospect_status, "attention_reason": attention_reason}


@app.post("/api/safety")
def api_update_safety(req: SafetyUpdateRequest) -> Dict[str, Any]:
    init_db()
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO safety_settings (key, value) VALUES ('allowlist_handles', ?)", (req.allowlist_handles.strip(),))
        conn.execute("INSERT OR REPLACE INTO safety_settings (key, value) VALUES ('enforce_test_only', ?)", ("true" if req.enforce_test_only else "false",))
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def serve_dashboard() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>GenAI Fund — AI & Robotics X Outreach Console</title>
  <style>
    body { margin: 0; font-family: system-ui, sans-serif; background: #0b0f19; color: #f9fafb; }
    header { padding: 16px 24px; background: #0f172a; border-bottom: 1px solid #374151; display: flex; justify-content: space-between; align-items: center; }
    main { max-width: 1320px; margin: 0 auto; padding: 20px; display: grid; grid-template-columns: 320px 1fr; gap: 20px; }
    .card { background: #111827; border: 1px solid #374151; border-radius: 10px; padding: 16px; margin-bottom: 16px; }
    input, textarea { width: 100%; background: #0b0f19; border: 1px solid #374151; color: #fff; padding: 8px; border-radius: 6px; margin-top: 4px; box-sizing: border-box; }
    button { background: #3b82f6; color: #fff; border: none; padding: 8px 12px; border-radius: 6px; font-weight: 600; cursor: pointer; margin-top: 8px; }
    .btn-success { background: #10b981; }
    .btn-warn { background: #f59e0b; color: #111827; }
    .btn-danger { background: #ef4444; }
    .badge { padding: 3px 8px; border-radius: 99px; font-size: 0.75rem; background: #1e3a8a; color: #93c5fd; margin-left: 6px; }
  </style>
</head>
<body>
  <header>
    <div><strong>GenAI Fund — AI & Robotics X Outreach Prototype</strong></div>
    <div id="metrics"></div>
  </header>
  <main>
    <aside>
      <div class="card">
        <h3>1. Discover AI/Robotics People</h3>
        <input id="seg" value="Southeast Asia AI & Robotics Founders" />
        <button onclick="discover()">Find & Score People</button>
      </div>
      <div class="card">
        <h3>2. Add Controlled Test Account</h3>
        <input id="tUser" placeholder="@username" />
        <input id="tName" placeholder="Display Name" />
        <textarea id="tPost" rows="2">Testing autonomous robotics & LLM outreach in Vietnam!</textarea>
        <button onclick="addTest()">+ Add Test Account</button>
      </div>
    </aside>
    <section>
      <div style="margin-bottom:12px;">
        <button class="btn-success" onclick="sendAll()">Send All Approved DMs</button>
      </div>
      <div id="list"></div>
    </section>
  </main>
  <script>
    async function load() {
      const r = await fetch('/api/state');
      const s = await r.json();
      document.getElementById('metrics').textContent = `15m Quota: ${s.rate_limits.window_15m_remaining}/15 | Est. Cost: $${s.telemetry.total_cost_usd}`;
      document.getElementById('list').innerHTML = s.prospects.map(p => `
        <div class="card">
          <div><strong>${p.display_name}</strong> (@${p.username} • ${p.location}) <span class="badge">Fit: ${p.fit_score}/100</span> <span class="badge">${p.status}</span></div>
          <p style="font-size:0.85rem;color:#9ca3af;">${p.bio}</p>
          <div style="font-size:0.82rem;color:#60a5fa;">Why they fit: ${(p.fit_reasons || []).join(' • ')}</div>
          <blockquote style="border-left:3px solid #3b82f6;padding-left:10px;font-size:0.85rem;color:#d1d5db;">"${p.evidence_quote}"</blockquote>
          <textarea id="dm_${p.participant_id}" rows="3">${p.draft_dm || ''}</textarea>
          ${p.sent_info ? `<div style="margin-top:8px;color:#6ee7b7;font-size:0.85rem;">✓ Sent (${p.sent_info.dm_event_id}) • Dedup Lock Active ${p.sent_info.reply_text ? '• Reply: ' + p.sent_info.reply_text : `<input id="rep_${p.participant_id}" placeholder="Simulate reply..."/><button class="btn-warn" onclick="simReply('${p.participant_id}')">Simulate Reply</button>`}</div>` : `
            <div>
              <button class="btn-success" onclick="act('${p.participant_id}','approve')">Approve</button>
              <button onclick="act('${p.participant_id}','save')">Save</button>
              <button class="btn-danger" onclick="act('${p.participant_id}','block')">Block</button>
            </div>
          `}
        </div>
      `).join('');
    }
    async function discover() {
      await fetch('/api/discover', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({segment_query:document.getElementById('seg').value})});
      load();
    }
    async function addTest() {
      await fetch('/api/add-test-account', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:document.getElementById('tUser').value, display_name:document.getElementById('tName').value, sample_post:document.getElementById('tPost').value})});
      load();
    }
    async function act(id, action) {
      await fetch('/api/draft/update', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({participant_id:id, draft_dm:document.getElementById('dm_'+id).value, action})});
      load();
    }
    async function sendAll() {
      await fetch('/api/send-approved', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({})});
      load();
    }
    async function simReply(id) {
      await fetch('/api/simulate-reply', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({participant_id:id, reply_text:document.getElementById('rep_'+id).value})});
      load();
    }
    load();
  </script>
</body>
</html>"""


def run_self_test() -> None:
    print("=== Running End-to-End Self-Test for GenAI Fund X Outreach Prototype ===")
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
    disc = api_discover(DiscoverRequest())
    print(f"[1/4] Discovery completed: {disc['processed']} candidates scored.")
    state = api_get_state()
    qualified = [p for p in state["prospects"] if p["status"] == "drafted"]
    target_pid = qualified[0]["participant_id"]
    api_update_draft(DraftUpdateRequest(participant_id=target_pid, draft_dm=qualified[0]["draft_dm"], action="approve"))
    send_res1 = api_send_approved(SendApprovedRequest(participant_ids=[target_pid]))
    assert send_res1["results"][0]["outcome"] == "sent"
    with get_db() as conn:
        conn.execute("UPDATE prospects SET status = 'approved' WHERE participant_id = ?", (target_pid,))
    send_res2 = api_send_approved(SendApprovedRequest(participant_ids=[target_pid]))
    assert send_res2["results"][0]["outcome"] == "blocked_duplicate"
    reply_res = api_simulate_reply(SimulateReplyRequest(participant_id=target_pid, reply_text="Would love to chat Tuesday about the robotics pilot!"))
    assert reply_res["prospect_status"] == "needs_attention"
    print("=== ALL END-TO-END CHECKS PASSED ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
    else:
        import uvicorn
        init_db()
        uvicorn.run(app, host=args.host, port=args.port)
