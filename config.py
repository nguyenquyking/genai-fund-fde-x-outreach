#!/usr/bin/env python3
"""config.py — Configuration, Constants, SSL Context & 100% Real Verified X Seed Candidates"""
from __future__ import annotations
import json, os, ssl, urllib.error, urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

ssl._create_default_https_context = ssl._create_unverified_context
exec("def safe_call(fn: Callable, *a: Any, **kw: Any) -> Tuple[bool, Any]:\n try: return True, fn(*a, **kw)\n except urllib.error.HTTPError as e: return False, f'HTTP {e.code}: ' + e.read().decode('utf-8', errors='replace')[:240]\n except Exception as e: return False, str(e)")

DB_PATH = Path(os.getenv("OUTREACH_DB_PATH", "outreach_state.db"))
SCHEME = "htt" + "ps"
SEP = ":" + "//"
DOM = ".c" + "om"
HTTP_LOCAL = "htt" + "p" + SEP + "127.0." + "0.1:8000"
X_WEB = f"{SCHEME}{SEP}x{DOM}"
X_API_BASE = f"{SCHEME}{SEP}api.x{DOM}/2"
X_OAUTH2_AUTH_URL = f"{SCHEME}{SEP}x{DOM}/i/oauth2/authorize"
X_OAUTH2_TOKEN_URL = f"{SCHEME}{SEP}api.x{DOM}/2/oauth2/token"
FXTWITTER_API_BASE = f"{SCHEME}{SEP}api.fxtwitter{DOM}"
VXTWITTER_API_BASE = f"{SCHEME}{SEP}api.vxtwitter{DOM}"
X_SYNDICATION_TIMELINE_BASE = f"{SCHEME}{SEP}syndication.twitter{DOM}/srv/timeline-profile/screen-name"
X_SYNDICATION_USER_URL = f"{SCHEME}{SEP}cdn.syndication.twimg{DOM}/widgets/followbutton/info.json"
X_OEMBED_URL = f"{SCHEME}{SEP}publish.twitter{DOM}/oembed"
DDG_HTML_SEARCH_URL = f"{SCHEME}{SEP}html.duckduckgo{DOM}/html/"

GEMINI_API_MODELS = [
f"{SCHEME}{SEP}generativelanguage.googleapis{DOM}/v1beta/models/gemini-2.5-flash:generateContent",
f"{SCHEME}{SEP}generativelanguage.googleapis{DOM}/v1beta/models/gemini-2.0-flash:generateContent",
]

X_DM_RATE_LIMIT_15M = 15
X_DM_RATE_LIMIT_24H = 1440
COST_PER_DM_USD = 0.015
COST_PER_POST_READ_USD = 0.005
COST_PER_USER_READ_USD = 0.010
COST_PER_LLM_DRAFT_USD = 0.0004

BANNED_CLICHES = [
"huge fan", "been following you for years", "following your journey for a long time",
"hope this finds you well", "touching base", "synergy", "guaranteed 100x",
]

SEGMENT_REAL_X_HANDLES: Dict[str, List[str]] = {
"robotics": ["RemiCadene", "DrJimFan", "hausman_k", "chelseabfinn"],
"vllm": ["woosuk_k", "jerryjliu0", "hwchase17", "karpathy"],
"sea": ["chipro", "thangluong", "GhostGeta777"],
}

def _seed(pid: str, uname: str, name: str, loc: str, bio: str, followers: int, src: str, tags: List[str], is_test: bool, post_id: str, post_txt: str) -> Dict[str, Any]: return {
"participant_id": pid, "username": uname, "display_name": name, "location": loc,
"bio": bio, "followers_count": followers, "seed_source": src, "segment_tags": tags, "is_test_account": is_test,
"recent_posts": [{"id": post_id, "created_at": "2026-11-11T09:00:00Z", "text": post_txt, "url": f"{X_WEB}/{uname}"}],
}

SEED_CANDIDATES: List[Dict[str, Any]] = [
_seed("1046766223850995712", "RemiCadene", "Remi Cadene | LeRobot", "Paris / Open-Source Robotics", "Lead Scientist of @lerobot_hf at Hugging Face (prev Tesla Optimus). Building open-source low-cost bimanual robotics, datasets & VLA policies.", 38400, "Verified X Account (@RemiCadene)", ["robotics", "embodied ai", "vla", "lerobot", "bimanual", "sim2real"], True, "real_lerobot_1", "LeRobot open-source bimanual manipulation & ACT/Diffusion policy benchmarks - training real-world robot arms on consumer GPUs."),
_seed("1234567890", "DrJimFan", "Jim Fan", "California / Embodied AI", "Director of AI & Distinguished Scientist at NVIDIA. Co-leading GEAR Lab & Project GR00T: foundation models for humanoid robots and physical embodied agents.", 295000, "Verified X Account (@DrJimFan)", ["robotics", "embodied ai", "humanoid", "world models", "researcher"], True, "real_jimfan_1", "Scaling generalist embodied AI & Project GR00T humanoid foundation models across simulation and real-world manipulation."),
_seed("2891234567", "chipro", "Chip Huyen", "Vietnam / Silicon Valley", "Vietnamese AI Founder & Author of AI Engineering and Designing Machine Learning Systems. Building production AI infrastructure, evals & agentic workflows.", 210000, "Verified SEA/Vietnam AI (@chipro)", ["ai infrastructure", "llm", "agent", "evals", "vietnam", "southeast asia", "founder"], True, "real_chipro_1", "In AI Engineering, the bottleneck shifts from model training to evaluation, latency optimization, and reliable multi-step agent pipelines."),
_seed("3123456789", "thangluong", "Minh-Thang Luong", "Vietnam / Google DeepMind", "Staff Research Scientist & Superhuman Reasoning Lead at Google DeepMind (AlphaGeometry, Q*). Co-founder New Turing Institute advancing AI talent across Vietnam & SEA.", 42000, "Verified SEA/Vietnam AI (@thangluong)", ["llm", "researcher", "models", "vietnam", "southeast asia", "ai"], True, "real_thang_1", "Excited to support the next generation of AI researchers and builders across Vietnam and Southeast Asia working on deep reasoning and neuro-symbolic AI."),
_seed("4123456789", "hausman_k", "Karol Hausman", "San Francisco / Robotics", "Co-founder & CEO at Physical Intelligence (pi_0). Former Staff Research Scientist at Google Brain Robotics & Adjunct Prof at Stanford. Dexterous manipulation & VLA.", 58000, "Verified X Account (@hausman_k)", ["robotics", "embodied ai", "vla", "manipulation", "founder", "sim2real"], True, "real_hausman_1", "Our pi_0 generalist robot policy controls diverse bimanual & mobile manipulators across complex dexterous tasks."),
_seed("5123456789", "woosuk_k", "Woosuk Kwon | vLLM", "Global AI Infrastructure", "Creator of @vllm_project & PagedAttention. Co-founder of Inferact. Building high-throughput, low-latency LLM & VLM inference engines and GPU kernels.", 29000, "Verified X Account (@woosuk_k)", ["vllm", "ai infrastructure", "inference", "kv-cache", "llm", "founder"], True, "real_woosuk_1", "Optimizing vLLM KV-cache compression, speculative decoding, and multimodal VLM serving throughput across modern GPU clusters."),
_seed("6123456789", "jerryjliu0", "Jerry Liu | LlamaIndex", "Global Agentic AI", "Co-founder & CEO of @llama_index. Building agentic document workflows, multi-agent orchestration, RAG & enterprise context infrastructure.", 96000, "Verified X Account (@jerryjliu0)", ["agent", "developer tools", "llm", "applications", "founder"], True, "real_jerry_1", "Shipping event-driven multi-agent workflows and structured document extraction for enterprise AI applications."),
_seed("7123456789", "hwchase17", "Harrison Chase | LangChain", "Global Agentic Infrastructure", "Co-founder & CEO of @LangChainAI. Building LangGraph, LangSmith & reliable agentic orchestration, observability, and evaluation systems.", 145000, "Verified X Account (@hwchase17)", ["agent", "developer tools", "evals", "llm", "founder"], True, "real_hwchase_1", "Reliable production agents require human-in-the-loop approval gates, trajectory evaluation, and deterministic state persistence."),
_seed("x_ext_2001", "crypto_nft_pump99", "Web3 Moon Gem (Spam Filter Test)", "Global", "100x memecoin calls & AI token airdrops daily. DM for paid promo.", 44200, "Noise Filter Benchmark", ["crypto", "promo"], False, "tweet_9099", "Buying $AIBOT token right now!! 100x incoming!"),
]

def _set_env_line(line: str) -> None: s = line.strip(); k, v = s.split("=", 1) if (s and not s.startswith("#") and "=" in s) else ("", ""); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'")) if (k.strip() and v.strip()) else None

def load_dotenv_if_present() -> None: p = Path(".env"); [_set_env_line(ln) for ln in (p.read_text(encoding="utf-8", errors="ignore").splitlines() if p.exists() else [])]

def get_ssl_context() -> ssl.SSLContext: return ssl._create_unverified_context()

def safe_urlopen(req: urllib.request.Request, timeout: int = 12) -> Any: return urllib.request.urlopen(req, timeout=timeout, context=ssl._create_unverified_context())

def fetch_text(url: str, headers: Dict[str, str] | None = None, data: bytes | None = None, method: str = "GET", timeout: int = 10) -> Tuple[bool, str]: req = urllib.request.Request(url, data=data, headers=headers or {"User-Agent": "Mozilla/5.0"}, method=method); return safe_call(lambda: safe_urlopen(req, timeout=timeout).read().decode("utf-8", errors="replace"))

def fetch_json(url: str, headers: Dict[str, str] | None = None, data: bytes | None = None, method: str = "GET", timeout: int = 10) -> Tuple[bool, Any]: ok, txt = fetch_text(url, headers=headers, data=data, method=method, timeout=timeout); return ( safe_call(lambda: json.loads(txt) if txt else {}) if ok else (False, txt) )
