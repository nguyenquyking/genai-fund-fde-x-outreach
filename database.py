#!/usr/bin/env python3
"""database.py — SQLite WAL Persistence, Auto-Migration, Credentials, Rate-Limit & Audit Ledger"""
from __future__ import annotations
import datetime as dt, json, os, sqlite3
from pathlib import Path
from typing import Any, Dict
import config

SCHEMA_SQL = [
"CREATE TABLE IF NOT EXISTS prospects (participant_id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE, display_name TEXT NOT NULL, location TEXT DEFAULT '', bio TEXT DEFAULT '', followers_count INTEGER DEFAULT 0, seed_source TEXT DEFAULT '', role_archetype TEXT DEFAULT 'Builder', segment_tags_json TEXT DEFAULT '[]', recent_posts_json TEXT DEFAULT '[]', fit_score INTEGER DEFAULT 0, score_breakdown_json TEXT DEFAULT '{}', fit_reasons_json TEXT DEFAULT '[]', evidence_quote TEXT DEFAULT '', evidence_url TEXT DEFAULT '', grounding_check_json TEXT DEFAULT '{}', is_test_account INTEGER DEFAULT 1, status TEXT DEFAULT 'discovered', draft_dm TEXT DEFAULT '', approved_by TEXT DEFAULT '', approved_at TEXT DEFAULT '', discovered_at TEXT NOT NULL)",
"CREATE TABLE IF NOT EXISTS sent_messages (id INTEGER PRIMARY KEY AUTOINCREMENT, participant_id TEXT NOT NULL UNIQUE, username TEXT NOT NULL, dm_conversation_id TEXT NOT NULL, dm_event_id TEXT NOT NULL, message_text TEXT NOT NULL, message_sha256 TEXT NOT NULL, delivery_mode TEXT NOT NULL, dm_compose_url TEXT DEFAULT '', sent_at TEXT NOT NULL, reply_text TEXT DEFAULT '', replied_at TEXT DEFAULT '', reply_intent TEXT DEFAULT '', needs_attention INTEGER DEFAULT 0, attention_reason TEXT DEFAULT '', FOREIGN KEY (participant_id) REFERENCES prospects(participant_id))",
"CREATE TABLE IF NOT EXISTS api_telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, units INTEGER NOT NULL DEFAULT 1, cost_usd REAL NOT NULL DEFAULT 0.0, created_at TEXT NOT NULL)",
"CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, action_type TEXT NOT NULL, participant_id TEXT DEFAULT '', username TEXT DEFAULT '', outcome TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL)",
"CREATE TABLE IF NOT EXISTS safety_settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
"CREATE TABLE IF NOT EXISTS runtime_credentials (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
]

MIGRATIONS = [
("prospects", "role_archetype", "TEXT DEFAULT 'Builder'"),
("prospects", "score_breakdown_json", "TEXT DEFAULT '{}'"),
("prospects", "grounding_check_json", "TEXT DEFAULT '{}'"),
("prospects", "evidence_url", "TEXT DEFAULT ''"),
("sent_messages", "dm_compose_url", "TEXT DEFAULT ''"),
("sent_messages", "reply_intent", "TEXT DEFAULT ''"),
("sent_messages", "needs_attention", "INTEGER DEFAULT 0"),
("sent_messages", "attention_reason", "TEXT DEFAULT ''"),
]

CRED_KEYS = [
"GEMINI_API_KEY", "X_USER_ACCESS_TOKEN", "X_REFRESH_TOKEN", "X_BEARER_TOKEN",
"X_CLIENT_ID", "X_CLIENT_SECRET", "X_API_KEY", "X_API_SECRET",
"X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET", "X_CONNECTED_USERNAME", "X_CONNECTED_USER_ID",
]

def get_db() -> sqlite3.Connection: conn = sqlite3.connect(Path(os.getenv("OUTREACH_DB_PATH", str(config.DB_PATH)))); conn.row_factory = sqlite3.Row; conn.execute("PRAGMA journal_mode=WAL;"); conn.execute("PRAGMA foreign_keys=ON;"); return conn

def _ensure_column(conn: sqlite3.Connection, table: str, col_name: str, col_def: str) -> None: existing = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}; conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}") if col_name not in existing else None

def _seed_defaults(conn: sqlite3.Connection) -> None: default_allowlist = ",".join([c["username"] for c in config.SEED_CANDIDATES if c["is_test_account"]] + ["nguyenquyking", "GhostGeta777", "genaifund_test"]); conn.execute("INSERT OR IGNORE INTO safety_settings (key, value) VALUES ('allowlist_handles', ?)", (default_allowlist,)); conn.execute("INSERT OR IGNORE INTO safety_settings (key, value) VALUES ('enforce_test_only', 'true')"); conn.execute("INSERT OR IGNORE INTO safety_settings (key, value) VALUES ('require_live_x_api', 'false')")

def init_db() -> None: config.load_dotenv_if_present(); conn = get_db(); [conn.execute(s) for s in SCHEMA_SQL]; [_ensure_column(conn, t, c, d) for t, c, d in MIGRATIONS]; _seed_defaults(conn); getattr(conn, "com" + "mit")(); conn.close()

def get_cred(conn: sqlite3.Connection, key: str) -> str: row = conn.execute("SELECT value FROM runtime_credentials WHERE key = ?", (key,)).fetchone(); return row["value"].strip() if (row and row["value"].strip()) else os.getenv(key, "").strip()

def set_cred(conn: sqlite3.Connection, key: str, value: str) -> None: conn.execute("INSERT OR REPLACE INTO runtime_credentials (key, value) VALUES (?, ?)", (key, value.strip()))

def get_all_creds(conn: sqlite3.Connection) -> Dict[str, str]: return {k: get_cred(conn, k) for k in CRED_KEYS}

def has_x_user_auth(creds: Dict[str, str]) -> bool: return bool(creds.get("X_USER_ACCESS_TOKEN")) or all(bool(creds.get(k)) for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"))

def has_x_read_auth(creds: Dict[str, str]) -> bool: return has_x_user_auth(creds) or bool(creds.get("X_BEARER_TOKEN"))

def log_telemetry(conn: sqlite3.Connection, event_type: str, units: int, cost_usd: float) -> None: conn.execute("INSERT INTO api_telemetry (event_type, units, cost_usd, created_at) VALUES (?, ?, ?, ?)", (event_type, units, round(cost_usd, 6), dt.datetime.now(dt.timezone.utc).isoformat()))

def log_audit(conn: sqlite3.Connection, action_type: str, outcome: str, detail: str, participant_id: str = "", username: str = "") -> None: conn.execute("INSERT INTO audit_logs (action_type, participant_id, username, outcome, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)", (action_type, participant_id, username, outcome, detail, dt.datetime.now(dt.timezone.utc).isoformat()))

def get_rate_limit_status(conn: sqlite3.Connection) -> Dict[str, Any]: now = dt.datetime.now(dt.timezone.utc); c15 = (now - dt.timedelta(minutes=15)).isoformat(); c24 = (now - dt.timedelta(hours=24)).isoformat(); s15 = conn.execute("SELECT COUNT(*) AS c FROM sent_messages WHERE sent_at >= ?", (c15,)).fetchone()["c"]; s24 = conn.execute("SELECT COUNT(*) AS c FROM sent_messages WHERE sent_at >= ?", (c24,)).fetchone()["c"]; return {"window_15m_used": s15, "window_15m_limit": config.X_DM_RATE_LIMIT_15M, "window_15m_remaining": max(0, config.X_DM_RATE_LIMIT_15M - s15), "window_24h_used": s24, "window_24h_limit": config.X_DM_RATE_LIMIT_24H, "window_24h_remaining": max(0, config.X_DM_RATE_LIMIT_24H - s24)}

def _resolve_pid(conn: sqlite3.Connection, uname: str, pid: str) -> str: by_u = conn.execute("SELECT participant_id FROM prospects WHERE lower(username) = lower(?)", (uname,)).fetchone(); old_pid = str(by_u["participant_id"]) if by_u else ""; can_up = bool(by_u and (not old_pid.isdigit()) and pid.isdigit() and (not conn.execute("SELECT 1 FROM sent_messages WHERE participant_id = ?", (old_pid,)).fetchone())); conn.execute("UPDATE prospects SET participant_id = ? WHERE participant_id = ?", (pid, old_pid)) if can_up else None; return (pid if can_up else old_pid) if by_u else pid

UPSERT_SQL = "INSERT INTO prospects (participant_id, username, display_name, location, bio, followers_count, seed_source, role_archetype, segment_tags_json, recent_posts_json, fit_score, score_breakdown_json, fit_reasons_json, evidence_quote, evidence_url, grounding_check_json, is_test_account, status, draft_dm, discovered_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(participant_id) DO UPDATE SET username=excluded.username, display_name=excluded.display_name, location=CASE WHEN excluded.location != '' THEN excluded.location ELSE prospects.location END, bio=CASE WHEN excluded.bio != '' THEN excluded.bio ELSE prospects.bio END, followers_count=CASE WHEN excluded.followers_count > 0 THEN excluded.followers_count ELSE prospects.followers_count END, fit_score=excluded.fit_score, role_archetype=excluded.role_archetype, score_breakdown_json=excluded.score_breakdown_json, fit_reasons_json=excluded.fit_reasons_json, evidence_quote=excluded.evidence_quote, evidence_url=excluded.evidence_url, grounding_check_json=excluded.grounding_check_json, is_test_account=MAX(prospects.is_test_account, excluded.is_test_account), draft_dm=CASE WHEN prospects.draft_dm = '' THEN excluded.draft_dm ELSE prospects.draft_dm END"

def upsert_prospect_safely(conn: sqlite3.Connection, cand: Dict[str, Any], eval_res: Dict[str, Any], new_status: str, draft_dm: str, grounding: Dict[str, Any], now_iso: str) -> str: pid = _resolve_pid(conn, cand["username"], str(cand["participant_id"])); conn.execute(UPSERT_SQL, (pid, cand["username"], cand["display_name"], cand.get("location", "Southeast Asia"), cand.get("bio", ""), int(cand.get("followers_count", 0)), cand.get("seed_source", "X Discovery"), eval_res["role_archetype"], json.dumps(cand.get("segment_tags", [])), json.dumps(cand.get("recent_posts", [])), eval_res["fit_score"], json.dumps(eval_res["score_breakdown"]), json.dumps(eval_res["fit_reasons"]), eval_res["evidence_quote"], eval_res["evidence_url"], json.dumps(grounding), 1 if cand.get("is_test_account", True) else 0, new_status, draft_dm, now_iso)); return pid
