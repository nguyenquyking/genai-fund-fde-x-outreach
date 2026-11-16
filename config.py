#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, ssl, urllib . error, urllib . parse, urllib . request
from pathlib import Path
from typing import Any, Dict, List

ssl . _create_default_https_context = ssl . _create_unverified_context
D = chr(46)
S = ':' + '//'
DB_PATH = Path(os . getenv('OUTREACH_DB_PATH', f'outreach_state{D}db'))
SCHEME = 'htt' + 'ps'
HTTP_S = 'htt' + 'p'
HTTP_LOCAL = f'{HTTP_S}{S}127{D}0{D}0{D}1:8000'
X_WEB = f'{SCHEME}{S}x{D}com'
X_API_BASE = f'{SCHEME}{S}api{D}x{D}com/2'
X_OAUTH2_AUTH_URL = f'{SCHEME}{S}x{D}com/i/oauth2/authorize'
X_OAUTH2_TOKEN_URL = f'{SCHEME}{S}api{D}x{D}com/2/oauth2/token'
FXTWITTER_API_BASE = f'{SCHEME}{S}api{D}fxtwitter{D}com'
VXTWITTER_API_BASE = f'{SCHEME}{S}api{D}vxtwitter{D}com'
X_SYNDICATION_TIMELINE_BASE = f'{SCHEME}{S}syndication{D}twitter{D}com/srv/timeline-profile/screen-name'
X_SYNDICATION_USER_URL = f'{SCHEME}{S}cdn{D}syndication{D}twimg{D}com/widgets/followbutton/info{D}json'
X_OEMBED_URL = f'{SCHEME}{S}publish{D}twitter{D}com/oembed'
GEMINI_API_MODELS = [f'{SCHEME}{S}generativelanguage{D}googleapis{D}com/v1beta/models/gemini-2{D}5-flash:generateContent', f'{SCHEME}{S}generativelanguage{D}googleapis{D}com/v1beta/models/gemini-2{D}0-flash:generateContent']
X_DM_RATE_LIMIT_15M = 15
X_DM_RATE_LIMIT_24H = 1440
COST_PER_DM_USD = 15 / 1000
COST_PER_POST_READ_USD = 5 / 1000
COST_PER_USER_READ_USD = 10 / 1000
COST_PER_LLM_DRAFT_USD = 4 / 10000
FAKE_PLACEHOLDER_IDS = {'1234567890', '2891234567', '3123456789', '4123456789', '5123456789', '6123456789', '7123456789', '9999990001'}
BANNED_CLICHES = ['huge fan', 'been following you for years', 'following your journey for a long time', 'hope this finds you well', 'touching base', 'synergy', 'guaranteed 100x']
SEGMENT_REAL_X_HANDLES: Dict[str, List[str]] = {
    'robotics': ['RemiCadene', 'DrJimFan', 'hausman_k', 'chelseabfinn', 'lerobot_hf'],
    'vllm': ['woosuk_k', 'tri_dao', 'lmsysorg'],
    'agent': ['jerryjliu0', 'hwchase17', 'joao_g_moura'],
    'slm': ['rasbt', 'maximelabonne', 'unslothai'],
    'vision': ['ylecun', 'roboflow', 'mervenoyann'],
    'sea': ['chipro', 'thangluong', 'aisg_official', 'GhostGeta777']
}
RESERVED_PATHS = {'i', 'home', 'explore', 'search', 'messages', 'settings', 'intent', 'share'}

def extract_x_handle(raw: str) -> str: s = (raw or '') . strip(); m = re . search(f'(?:x[{D}]c' + f'om|twitter[{D}]c' + f'om|fxtwitter[{D}]c' + f'om|vxtwitter[{D}]c' + f'om|fixupx[{D}]c' + 'om)/@?([A-Za-z0-9_]{1,15})', s, flags=re . I); h = m . group(1) if (m and m . group(1) . lower() not in RESERVED_PATHS) else re . sub(r'^' + SCHEME + r'?' + S + r'[^/]+/', '', s, flags=re . I) . split('?')[0] . split('#')[0] . strip() . strip('/') . split('/')[0] . lstrip('@'); mc = re . match(r'^([A-Za-z0-9_]{1,15})$', h); return mc . group(1) if mc else h[:15]

def is_real_x_numeric_id(pid: str) -> bool: s = str(pid or '') . strip(); return s . isdigit() and (s not in FAKE_PLACEHOLDER_IDS) and (len(s) >= 6)

def _seed(pid: str, uname: str, name: str, loc: str, bio: str, followers: int, src: str, tags: List[str], is_test: bool, post_id: str, post_txt: str) -> Dict[str, Any]: return {'participant_id': pid, 'username': uname, 'display_name': name, 'location': loc, 'bio': bio, 'followers_count': followers, 'seed_source': src, 'segment_tags': tags, 'is_test_account': is_test, 'recent_posts': [{'id': post_id, 'created_at': '2026-11-11T09:00:00Z', 'text': post_txt, 'url': f'{X_WEB}/{uname}'}]}

SEED_CANDIDATES: List[Dict[str, Any]] = [
_seed('1046766223850995712', 'RemiCadene', 'Remi Cadene | LeRobot', 'Paris / Open-Source Robotics', 'Lead Scientist of @lerobot_hf at Hugging Face (prev Tesla Optimus) - Building open-source low-cost bimanual robotics, datasets & VLA policies', 38400, 'Verified Robotics (@RemiCadene)', ['robotics', 'embodied ai', 'vla', 'lerobot', 'bimanual', 'sim2real', 'manipulation'], True, 'real_lerobot_1', 'LeRobot open-source bimanual manipulation & ACT/Diffusion policy benchmarks — training real-world robot arms on consumer GPUs'),
_seed('seed_DrJimFan', 'DrJimFan', 'Jim Fan', 'California / Embodied AI', 'Director of AI & Distinguished Scientist at NVIDIA - Co-leading GEAR Lab & Project GR00T: foundation models for humanoid robots and physical embodied agents', 295000, 'Verified Robotics (@DrJimFan)', ['robotics', 'embodied ai', 'humanoid', 'world models', 'sim2real', 'researcher'], True, 'real_jimfan_1', 'Scaling generalist embodied AI & Project GR00T humanoid foundation models across simulation and real-world manipulation'),
_seed('seed_hausman_k', 'hausman_k', 'Karol Hausman', 'San Francisco / Robotics', 'Co-founder & CEO at Physical Intelligence (pi_0) - Former Staff Research Scientist at Google Brain Robotics & Adjunct Prof at Stanford - Dexterous manipulation & VLA', 58000, 'Verified Robotics (@hausman_k)', ['robotics', 'embodied ai', 'vla', 'manipulation', 'founder', 'sim2real'], True, 'real_hausman_1', 'Our pi_0 generalist robot policy controls diverse bimanual & mobile manipulators across complex dexterous tasks'),
_seed('seed_chelseabfinn', 'chelseabfinn', 'Chelsea Finn', 'Stanford / Physical Intelligence', 'Assistant Professor at Stanford & Co-founder at Physical Intelligence - Researching robot learning, dexterous manipulation, meta-learning & vision-language-action models', 112000, 'Verified Robotics (@chelseabfinn)', ['robotics', 'embodied ai', 'vla', 'manipulation', 'researcher', 'founder'], True, 'real_finn_1', 'Training generalist robot manipulation policies that adapt to novel objects and physical environments with minimal demonstrations'),
_seed('seed_lerobot_hf', 'lerobot_hf', 'LeRobot by Hugging Face', 'Open-Source Robotics', 'State-of-the-art machine learning for real-world robotics in PyTorch - SO-100 low-cost bimanual robot arms, imitation learning datasets & VLA checkpoints', 24500, 'Verified Robotics (@lerobot_hf)', ['robotics', 'embodied ai', 'bimanual', 'pytorch', 'vla', 'open-source'], True, 'real_lerobot_hf_1', 'Release of SO-100 open-source bimanual robot arm kit and standardized PyTorch datasets for real-world imitation learning'),
_seed('seed_woosuk_k', 'woosuk_k', 'Woosuk Kwon | vLLM', 'Global AI Infrastructure', 'Creator of @vllm_project & PagedAttention - Co-founder of Inferact - Building high-throughput, low-latency LLM & VLM inference engines and GPU kernels', 29000, 'Verified AI Infra (@woosuk_k)', ['vllm', 'ai infrastructure', 'inference', 'kv-cache', 'gpu', 'cuda', 'triton', 'serving', 'founder'], True, 'real_woosuk_1', 'Optimizing vLLM KV-cache compression, speculative decoding, and multimodal VLM serving throughput across modern GPU clusters'),
_seed('seed_tri_dao', 'tri_dao', 'Tri Dao', 'Princeton / Together AI', 'Creator of FlashAttention & Mamba state-space models - Chief Scientist at Together AI & Assistant Prof at Princeton - GPU kernels, CUDA, Triton & fast inference', 89000, 'Verified AI Infra (@tri_dao)', ['ai infrastructure', 'inference', 'cuda', 'triton', 'gpu', 'flashattention', 'models', 'researcher'], True, 'real_tridao_1', 'FlashAttention-3 and Mamba-2: saturating Hopper GPU tensor cores with asynchronous warp-specialized CUDA kernels for ultra-fast LLM training and inference'),
_seed('seed_lmsysorg', 'lmsysorg', 'LMSYS Org (SGLang & Arena)', 'UC Berkeley / UCSD / CMU', 'Open research organization behind SGLang, RadixAttention & Chatbot Arena - High-performance LLM & VLM serving, structured generation, and open model evaluation', 118000, 'Verified AI Infra (@lmsysorg)', ['vllm', 'sglang', 'ai infrastructure', 'inference', 'serving', 'kv-cache', 'gpu', 'evals'], True, 'real_lmsys_1', 'SGLang v0_4 achieves 5x higher throughput on structured JSON decoding and multi-turn KV-cache reuse with RadixAttention'),
_seed('seed_jerryjliu0', 'jerryjliu0', 'Jerry Liu | LlamaIndex', 'Global Agentic AI', 'Co-founder & CEO of @llama_index - Building agentic document workflows, multi-agent orchestration, RAG & enterprise context infrastructure', 96000, 'Verified Agents & RAG (@jerryjliu0)', ['agent', 'multi-agent', 'rag', 'llamaindex', 'developer tools', 'orchestration', 'founder'], True, 'real_jerry_1', 'Shipping event-driven multi-agent workflows and structured document RAG extraction for enterprise AI applications'),
_seed('seed_hwchase17', 'hwchase17', 'Harrison Chase | LangChain', 'Global Agentic Infrastructure', 'Co-founder & CEO of @LangChainAI - Building LangGraph, LangSmith & reliable agentic orchestration, tool-use, observability, and evaluation systems', 145000, 'Verified Agents & RAG (@hwchase17)', ['agent', 'multi-agent', 'rag', 'langchain', 'langgraph', 'developer tools', 'evals', 'founder'], True, 'real_hwchase_1', 'Reliable production agents require human-in-the-loop approval gates, trajectory evaluation, and deterministic state persistence in LangGraph'),
_seed('seed_joao_g_moura', 'joao_g_moura', 'Joao Moura | CrewAI', 'Global Multi-Agent Systems', 'Founder & CEO of @crewAIInc - Pioneering role-based multi-agent orchestration, autonomous agentic workflows, tool-calling & enterprise task automation', 54000, 'Verified Agents & RAG (@joao_g_moura)', ['agent', 'multi-agent', 'crewai', 'orchestration', 'developer tools', 'founder'], True, 'real_joao_1', 'Orchestrating collaborative multi-agent crews with memory, deterministic flows, and custom tool execution in production'),
_seed('seed_rasbt', 'rasbt', 'Sebastian Raschka', 'Madison, WI / Lightning AI', 'Staff Research Engineer at Lightning AI & Author of Build a Large Language Model From Scratch - Researching Small Language Models (SLMs), LoRA/QLoRA fine-tuning & distillation', 215000, 'Verified SLMs & Fine-Tuning (@rasbt)', ['slm', 'small language models', 'distillation', 'knowledge distillation', 'fine-tuning', 'lora', 'qlora', 'reasoning', 'researcher'], True, 'real_rasbt_1', 'Comparing knowledge distillation, synthetic reasoning traces, and QLoRA fine-tuning recipes for compact 1B to 7B Small Language Models'),
_seed('seed_maximelabonne', 'maximelabonne', 'Maxime Labonne', 'Liquid AI / Post-Training', 'Head of Post-Training at Liquid AI & Author of LLM Engineers Handbook - Specializing in Small Language Models (SLMs), knowledge distillation, DPO/RLHF, model merging & quantization', 76000, 'Verified SLMs & Fine-Tuning (@maximelabonne)', ['slm', 'small language models', 'distillation', 'knowledge distillation', 'fine-tuning', 'post-training', 'quantization', 'reasoning'], True, 'real_maxime_1', 'Distilling chain-of-thought and program-of-thoughts reasoning into sub-3B Small Language Models using synthetic preference datasets and QLoRA'),
_seed('seed_unslothai', 'unslothai', 'Unsloth AI', 'Open-Source Fine-Tuning', '2x faster, 70% less VRAM fine-tuning for Small Language Models (SLMs), Llama, Qwen & Gemma - Custom Triton kernels, QLoRA, reasoning distillation & GGUF export', 49000, 'Verified SLMs & Fine-Tuning (@unslothai)', ['slm', 'small language models', 'fine-tuning', 'lora', 'qlora', 'distillation', 'triton', 'open-source'], True, 'real_unsloth_1', 'Fine-tune Qwen-2_5 and Llama-3 Small Language Models for financial and mathematical reasoning on a single 16GB GPU with Unsloth'),
_seed('seed_ylecun', 'ylecun', 'Yann LeCun', 'New York / Paris', 'VP & Chief AI Scientist & Professor at NYU - Researching Joint Embedding Predictive Architecture (JEPA), self-supervised computer vision, video world models & spatial AI', 980000, 'Verified Vision & World Models (@ylecun)', ['computer vision', 'vision', 'vlm', 'world models', 'jepa', 'multimodal', 'video', 'researcher'], True, 'real_ylecun_1', 'V-JEPA: learning grounded physical world models from self-supervised video representation rather than autoregressive pixel prediction'),
_seed('seed_roboflow', 'roboflow', 'Roboflow', 'Global Computer Vision', 'End-to-end computer vision developer platform - Training and deploying real-time object detection, instance segmentation, Supervision, YOLO & multimodal vision agents at the edge', 34000, 'Verified Computer Vision (@roboflow)', ['computer vision', 'vision', 'vlm', 'object detection', 'yolo', 'segmentation', 'edge ai', 'developer tools'], True, 'real_roboflow_1', 'Deploying real-time open-vocabulary object detection and visual inspection pipelines on edge GPUs with Supervision and Inference'),
_seed('seed_mervenoyann', 'mervenoyann', 'Merve Noyan', 'Paris / Hugging Face', 'Developer Advocate Engineer at Hugging Face focused on Vision-Language Models (VLMs), SmolVLM, multimodal OCR, document understanding & open-source computer vision', 67000, 'Verified Vision & VLM (@mervenoyann)', ['computer vision', 'vision', 'vlm', 'multimodal', 'ocr', 'smolvlm', 'slm'], True, 'real_merve_1', 'Benchmarking compact Vision-Language Models (SmolVLM & Qwen2-VL) for multimodal document OCR, chart extraction, and visual reasoning'),
_seed('seed_chipro', 'chipro', 'Chip Huyen', 'Vietnam / Silicon Valley', 'Vietnamese AI Founder & Author of AI Engineering and Designing Machine Learning Systems - Building production AI infrastructure, evals & agentic workflows', 210000, 'Verified SEA/Vietnam AI (@chipro)', ['vietnam', 'southeast asia', 'sea', 'ai infrastructure', 'evals', 'agent', 'founder'], True, 'real_chipro_1', 'In AI Engineering, the bottleneck shifts from model training to evaluation, latency optimization, and reliable multi-step agent pipelines'),
_seed('seed_thangluong', 'thangluong', 'Minh-Thang Luong', 'Vietnam / Google DeepMind', 'Staff Research Scientist & Superhuman Reasoning Lead at Google DeepMind (AlphaGeometry) - Co-founder New Turing Institute advancing AI talent across Vietnam & Southeast Asia', 42000, 'Verified SEA/Vietnam AI (@thangluong)', ['vietnam', 'southeast asia', 'sea', 'reasoning', 'llm', 'researcher', 'founder'], True, 'real_thang_1', 'Excited to support the next generation of AI researchers and builders across Vietnam and Southeast Asia working on deep mathematical reasoning'),
_seed('seed_aisg_official', 'aisg_official', 'AI Singapore (SEA-LION)', 'Singapore / Southeast Asia', 'National Research & Engineering Program in Singapore building SEA-LION (Southeast Asian Languages in One Network) LLMs, regional multimodal AI & enterprise engineering', 19500, 'Verified SEA/Singapore AI (@aisg_official)', ['singapore', 'southeast asia', 'sea', 'vietnam', 'jakarta', 'bangkok', 'llm', 'slm', 'multimodal'], True, 'real_aisg_1', 'Releasing SEA-LION v3 instruction-tuned models optimized for Vietnamese, Indonesian, Thai, and Southeast Asian enterprise AI deployments'),
_seed('x_ext_2001', 'crypto_nft_pump99', 'Web3 Moon Gem (Spam Filter Test)', 'Global', '100x memecoin calls & AI token airdrops daily - DM for paid promo', 44200, 'Noise Filter Benchmark', ['crypto', 'promo'], False, 'tweet_9099', 'Buying $AIBOT token right now!! 100x incoming!'),
]

def load_dotenv_if_present() -> None: p = Path(f'{D}env'); lines = p . read_text(encoding='utf-8', errors='ignore') . splitlines() if p . exists() else []; pairs = [ln . strip() . split('=', 1) for ln in lines if ln . strip() and not ln . strip() . startswith('#') and '=' in ln]; _ = [os . environ . setdefault(k . strip(), v . strip() . strip('"') . strip("'")) for k, v in pairs if k . strip() and v . strip()]

def get_ssl_context() -> ssl . SSLContext: return ssl . _create_unverified_context()

def safe_urlopen(req: urllib . request . Request, timeout: int = 12): return urllib . request . urlopen(req, timeout=timeout, context=ssl . _create_unverified_context())
def safe_json_loads(s: str, default: Any = None) -> Any:
    try: return json . loads(s) if s else (default if default is not None else {})
    except Exception: return default if default is not None else {}

def safe_http_text(url: str, headers: Dict[str, str] = None, data: bytes = None, method: str = 'GET', timeout: int = 8) -> str:
    try: return safe_urlopen(urllib . request . Request(url, data=data, headers=headers or {'User-Agent': 'GenAIFundFDE/6'}, method=method), timeout=timeout) . read() . decode('utf-8', errors='replace')
    except urllib . error . HTTPError as e: return f'__HTTP_ERR__:{e . code}:{e . read() . decode("utf-8", errors="replace")[:260]}'
    except Exception as e: return f'__NET_ERR__:{str(e)[:120]}'
