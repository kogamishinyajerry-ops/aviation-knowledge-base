"""Generate demo/ask.html from scripts/rag/eval_results.json.

Renders 5 query→answer cards with citations, retrieved chunks (audit), and
guardrail status. Reuses the demo style.css.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS = Path(__file__).resolve().parent / "eval_results.json"
DEMO = ROOT / "demo"
OUT = DEMO / "ask.html"

CITE_RE = re.compile(r"\[CITE:(c_[0-9a-f]{8})\]")


def render_answer(answer: str, citations: list[dict]) -> str:
    cite_map = {c["chunk_id"]: c for c in citations}

    def replace(m):
        cid = m.group(1)
        if cid in cite_map:
            c = cite_map[cid]
            label = f"{c['document_id']} · {c['section'] or '—'}"
            return f'<a href="#cite-{cid}" class="cite-link" title="{html.escape(c["text_preview"])}">[{label}]</a>'
        return f'<span class="cite-bad">[CITE:{cid}]</span>'

    rendered = CITE_RE.sub(replace, html.escape(answer))
    return rendered.replace("\n", "<br>")


def card(result: dict, idx: int) -> str:
    meta = result.get("query_meta", {})
    qid = meta.get("query_id", "?")
    qtype = meta.get("type", "?")
    q = meta.get("query_en") or meta.get("query_zh") or result.get("query", "?")
    qzh = meta.get("query_zh") or ""

    type_class = {
        "factual": "tag-ok",
        "table": "tag",
        "procedural": "tag",
        "cross_lingual": "tag",
        "out_of_scope": "tag-warn",
    }.get(qtype, "tag")

    status_html = ""
    if result.get("guardrail_tripped"):
        status_html = (
            f'<span class="tag tag-warn">🛡️ GUARDRAIL</span> '
            f'<small>{html.escape(result.get("rejected_reason", ""))} · '
            f'LLM called: {result.get("llm_called", False)}</small>'
        )
    elif result.get("error"):
        status_html = f'<span class="tag tag-rej">❌ ERROR</span> {html.escape(result["error"])}'
    else:
        n = len(result.get("citations", []))
        status_html = f'<span class="tag tag-ok">✅ {n} citation{"s" if n != 1 else ""}</span>'

    answer_html = render_answer(result.get("answer", ""), result.get("citations", []))

    cit_rows = ""
    for c in result.get("citations", []):
        cit_rows += (
            f'<tr id="cite-{c["chunk_id"]}">'
            f'<td><code>{c["chunk_id"]}</code></td>'
            f'<td><a href="entities/document/{c["document_id"]}.html">{c["document_id"]}</a></td>'
            f'<td>{html.escape(c["section"] or "—")}</td>'
            f'<td>{c["score"]}</td>'
            f'<td><small>{html.escape(c["text_preview"])}</small></td>'
            f'</tr>'
        )

    retr_rows = ""
    for r in result.get("retrieved", []):
        in_cit = any(c["chunk_id"] == r["chunk_id"] for c in result.get("citations", []))
        used_marker = "✓" if in_cit else ""
        retr_rows += (
            f'<tr><td>{used_marker}</td>'
            f'<td><code>{r["chunk_id"]}</code></td>'
            f'<td>{r["document_id"]}</td>'
            f'<td>{r["score"]}</td>'
            f'<td><small>{html.escape(r["text_preview"][:80])}…</small></td></tr>'
        )

    return f"""
<div class="card" style="margin-bottom:2em;">
  <div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:0.5em;">
    <div>
      <span class="{type_class}">{qtype}</span>
      <span class="tag" style="background:#eee;color:#555;">{qid}</span>
    </div>
    <div>{status_html}</div>
  </div>
  <h3 style="margin-top:0.6em;">Q: {html.escape(q)}</h3>
  {f'<p style="color:#666;font-size:0.9em;">中文: {html.escape(qzh)}</p>' if qzh and qzh != q else ''}

  <h4>Answer</h4>
  <div style="background:#fff;padding:1em;border-left:3px solid #0066cc;border-radius:4px;">
    {answer_html}
  </div>

  {f'<h4>Citations resolved ({len(result.get("citations", []))})</h4><table><tr><th>chunk_id</th><th>document</th><th>section</th><th>score</th><th>preview</th></tr>{cit_rows}</table>' if result.get("citations") else ''}

  <details style="margin-top:1em;">
    <summary><strong>Audit trail — top-{len(result.get("retrieved", []))} retrieved chunks</strong> (✓ = used in citation)</summary>
    <table><tr><th>used</th><th>chunk_id</th><th>document</th><th>score</th><th>preview</th></tr>{retr_rows}</table>
  </details>
</div>
"""


def main():
    if not RESULTS.exists():
        print(f"ERROR: {RESULTS} not found. Run scripts.rag.eval_run first.")
        return 2

    data = json.loads(RESULTS.read_text())
    cards = "\n".join(card(r, i) for i, r in enumerate(data))

    body = f"""
<h2>🤖 Live RAG Query Demo (Phase 7)</h2>
<p>这些是用 <a href="https://github.com/kogamishinyajerry-ops/aviation-knowledge-base/blob/main/.planning/design/RAG_PIPELINE.md">RAG_PIPELINE.md</a> 设计实现的 RAG 流水线，对 <a href="https://github.com/kogamishinyajerry-ops/aviation-knowledge-base/blob/main/evaluation/queries.yaml">evaluation/queries.yaml</a> 中 5 个代表性问题真实跑出来的结果。<strong>每条 citation 都可点击跳到来源 chunk</strong>，每条 audit trail 都列出 top-K 检索结果的真实分数。</p>

<div class="stats">
  <div class="stat"><div class="num">{len(data)}</div><div class="label">问题</div></div>
  <div class="stat"><div class="num">{sum(1 for r in data if not r.get("guardrail_tripped") and not r.get("error"))}</div><div class="label">回答带 citation</div></div>
  <div class="stat"><div class="num">{sum(1 for r in data if r.get("guardrail_tripped"))}</div><div class="label">触发 guardrail</div></div>
  <div class="stat"><div class="num">{sum(len(r.get("citations", [])) for r in data)}</div><div class="label">总 citations</div></div>
</div>

<h3>流水线（实际代码：scripts/rag/）</h3>
<ol>
  <li><strong>chunker</strong> (<code>index.py</code>) — 按 RAG_PIPELINE §2.4 规则切块（regulation clause regex 锁定边界 / table 原子 / 512 tokens 默认）</li>
  <li><strong>embedder</strong> — Ollama bge-m3 通过 HTTP API（fallback: nomic-embed-text 演示用）</li>
  <li><strong>retriever</strong> (<code>query.py</code>) — 余弦相似度 top-K，<strong>guardrail</strong>: <code>min_chunk_score=0.5</code> AND <code>min_chunks_required=2</code></li>
  <li><strong>LLM</strong> — DeepSeek <code>deepseek-chat</code>，prompt 内嵌 <code>[CITE:c_xxxxxxxx]</code> token，禁止 LLM 自创 citation</li>
  <li><strong>post-validator</strong> — answer 中所有 citation 必须能在 retrieved chunk_ids 中解析，否则整条 answer 被替换为 canned no-context</li>
</ol>

<h3>5 个真实查询结果</h3>
{cards}

<h3>规格落地核对</h3>
<table>
<tr><th>RAG_PIPELINE.md 规格</th><th>实现位置</th><th>状态</th></tr>
<tr><td>§2.3 chunk_size=512, overlap=64</td><td><code>scripts/rag/index.py:24</code></td><td>✅</td></tr>
<tr><td>§2.4 regulation-clause regex 边界</td><td><code>scripts/rag/index.py:CLAUSE_RE</code></td><td>✅</td></tr>
<tr><td>§5.1 [CITE:c_&lt;8hex&gt;] token 格式</td><td><code>scripts/rag/index.py:chunk_id</code></td><td>✅</td></tr>
<tr><td>§5.3 post-generation citation validator</td><td><code>scripts/rag/query.py:validate_citations</code></td><td>✅</td></tr>
<tr><td>§6.1 min_chunk_score=0.5, required=2</td><td><code>scripts/rag/query.py:apply_guardrail</code></td><td>✅</td></tr>
<tr><td>§6.2 canned no-context (zh+en)</td><td><code>scripts/rag/query.py:CANNED_NO_CONTEXT</code></td><td>✅</td></tr>
<tr><td>BGE-M3 embedding</td><td><code>EMBED_MODEL</code></td><td>⚠️ 当前用 nomic-embed-text fallback；bge-m3 拉好后重 index 即生效</td></tr>
</table>

<h3>重新生成</h3>
<pre>ollama pull bge-m3                  # one-time, ~2GB
export DEEPSEEK_API_KEY=sk-...      # already set
source .venv/bin/activate
python -m scripts.rag.index         # ~10s for 3 docs
python -m scripts.rag.eval_run      # ~30s for 5 queries
python -m scripts.rag.build_ask_page</pre>
"""
    OUT.write_text(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Live RAG Demo — Aviation KB</title>
<link rel="stylesheet" href="./style.css">
<style>
.cite-link {{ color: #0066cc; background: #e6f0fa; padding: 0.05em 0.4em; border-radius: 3px; text-decoration: none; font-size: 0.9em; }}
.cite-link:hover {{ background: #0066cc; color: white; }}
.cite-bad {{ background: #f8d7da; color: #721c24; padding: 0.05em 0.4em; border-radius: 3px; }}
details summary {{ cursor: pointer; padding: 0.4em; background: #f5f8fc; border-radius: 4px; }}
</style>
</head>
<body>
<header>
  <h1>✈️ Aviation Knowledge Base — v0.1.0 Demo</h1>
  <div class="tagline">每条知识可追溯 · AI 回答带 citation · 人工 vs AI 抽取标记</div>
</header>
<nav>
  <a href="./index.html">🏠 首页</a>
  <a href="./entities.html">📦 实体浏览</a>
  <a href="./relations.html">🔗 关系图</a>
  <a href="./citation-chain.html">📍 引用链路</a>
  <a href="./bilingual.html">🌐 双语</a>
  <a href="./supersession.html">🔄 supersession</a>
  <a href="./h-darrieus.html">🛡️ H-Darrieus</a>
  <a href="./validation.html">✅ 验证</a>
  <a href="./ask.html"><strong>🤖 问答</strong></a>
</nav>
{body}
<footer style="border-top:1px solid #eee;margin-top:3em;padding-top:1em;color:#888;font-size:0.85em;">
  Generated from scripts/rag/eval_results.json · regenerate via <code>python -m scripts.rag.build_ask_page</code>
</footer>
</body>
</html>""")
    print(f"✓ Wrote {OUT}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
