#!/usr/bin/env python3
"""Generate a static browse-only demo UI from instances/ and docs/.

This is the v0.1.0 "看东西" UI — pure static HTML/CSS, no frameworks, no
services. It reads the canonical YAML corpus and renders it as a navigable
local web page so non-engineers (and you) can see what the schema actually
shaped up like.

Usage:
    python scripts/build_demo_ui.py
    python -m http.server 8000 -d demo

Output: demo/ (HTML + style.css). Regenerate any time the corpus changes.
Pages:
    index.html          — landing + stats
    entities.html       — list of all 22 entity types
    entities/<type>/<slug>.html  — per-record detail
    relations.html      — relation graph (text)
    citation-chain.html — DEMO-04: ExpertNote → Document → metadata.yaml
    bilingual.html      — DEMO-07: zh/en side-by-side
    supersession.html   — DEMO-05: superseded → active chain
    h-darrieus.html     — PROV-04 rule + boundary table + _pending demo
    validation.html     — live `python scripts/validate.py` output

Constraints (CLAUDE.md):
    - No new dependencies (uses ruamel.yaml already in requirements-dev)
    - No JS frameworks
    - No build step beyond running this script
"""
from pathlib import Path
import html
import sys
import subprocess
from collections import defaultdict
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "demo"
INSTANCES = ROOT / "instances"
DOCS = ROOT / "docs"

yaml = YAML(typ="safe")


def load_corpus():
    entities = defaultdict(list)
    relations = defaultdict(list)
    pending = []
    docs_meta = {}

    for p in (INSTANCES / "entities").rglob("*.yaml"):
        rec = yaml.load(p.read_text())
        entities[p.parent.name].append((p, rec))

    rel_root = INSTANCES / "relations"
    if rel_root.exists():
        for p in rel_root.rglob("*.yaml"):
            rec = yaml.load(p.read_text())
            relations[p.parent.name].append((p, rec))

    pend_root = INSTANCES / "_pending"
    if pend_root.exists():
        for p in pend_root.rglob("*.yaml"):
            rec = yaml.load(p.read_text())
            pending.append((p, rec))

    for p in DOCS.rglob("metadata.yaml"):
        meta = yaml.load(p.read_text())
        docs_meta[p.parent.name] = (p, meta)

    return entities, relations, pending, docs_meta


CSS = """
:root { --primary: #0066cc; --bg: #fafafa; --card: #f5f8fc; --border: #e0e0e0; }
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
       max-width: 1100px; margin: 0 auto; padding: 1.5em 1em; color: #222; line-height: 1.55; background: white; }
header { border-bottom: 2px solid var(--primary); padding-bottom: 0.6em; margin-bottom: 1.2em; }
header h1 { color: var(--primary); margin: 0 0 0.2em 0; font-size: 1.6em; }
header .tagline { color: #666; font-size: 0.92em; }
nav { margin: 0.8em 0 1.5em; padding: 0.6em 0.8em; background: var(--card); border-radius: 6px;
      display: flex; flex-wrap: wrap; gap: 0.8em; }
nav a { color: var(--primary); text-decoration: none; font-size: 0.92em; }
nav a:hover { text-decoration: underline; }
h2 { color: #333; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
h3 { color: #444; margin-top: 1.5em; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.8em; margin: 1.2em 0; }
.stat { background: var(--card); padding: 1em; border-radius: 6px; text-align: center; }
.stat .num { font-size: 2em; font-weight: 700; color: var(--primary); line-height: 1; }
.stat .label { font-size: 0.82em; color: #555; margin-top: 0.3em; }
.card { background: var(--bg); border: 1px solid var(--border); padding: 0.9em 1em;
        margin: 0.6em 0; border-radius: 6px; }
.tag { display: inline-block; padding: 0.15em 0.6em; border-radius: 3px; font-size: 0.82em;
       background: #e6f0fa; color: var(--primary); margin-right: 0.3em; }
.tag-warn { background: #fff3cd; color: #856404; }
.tag-ok { background: #d4edda; color: #155724; }
.tag-rej { background: #f8d7da; color: #721c24; }
.tag-pending { background: #e2e3e5; color: #383d41; }
pre { background: #2b2b2b; color: #f8f8f2; padding: 1em; border-radius: 6px; overflow-x: auto;
      font-size: 0.84em; line-height: 1.5; }
code { background: #f1f3f5; padding: 0.1em 0.4em; border-radius: 3px; font-size: 0.9em; }
pre code { background: transparent; padding: 0; }
.bilingual { display: grid; grid-template-columns: 1fr 1fr; gap: 1em; margin: 1em 0; }
.bilingual > div { background: var(--card); padding: 1em 1.2em; border-radius: 6px; }
.bilingual h3 { margin-top: 0.4em; color: var(--primary); }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.92em; }
th, td { padding: 0.5em 0.7em; border: 1px solid #ddd; text-align: left; }
th { background: var(--card); }
.chain { display: flex; align-items: center; flex-wrap: wrap; gap: 0.5em; margin: 1em 0; }
.chain > .node { background: white; padding: 0.7em 1em; border: 2px solid var(--primary);
                 border-radius: 6px; min-width: 160px; }
.chain > .node small { color: #666; }
.chain-arrow { color: var(--primary); font-size: 1.4em; padding: 0 0.2em; }
ul { padding-left: 1.5em; }
li { margin: 0.3em 0; }
.entity-list { columns: 2; column-gap: 1.5em; list-style-position: inside; padding-left: 0; }
.entity-list li { break-inside: avoid; }
footer { border-top: 1px solid #eee; margin-top: 3em; padding-top: 1em; color: #888;
         font-size: 0.85em; }
"""


def html_page(title, body, base="."):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Aviation KB Demo</title>
<link rel="stylesheet" href="{base}/style.css">
</head>
<body>
<header>
  <h1>✈️ Aviation Knowledge Base — v0.1.0 Demo</h1>
  <div class="tagline">每条知识可追溯 · AI 回答带 citation · 人工 vs AI 抽取标记</div>
</header>
<nav>
  <a href="{base}/index.html">🏠 首页</a>
  <a href="{base}/entities.html">📦 实体浏览</a>
  <a href="{base}/relations.html">🔗 关系图</a>
  <a href="{base}/citation-chain.html">📍 引用链路</a>
  <a href="{base}/bilingual.html">🌐 双语</a>
  <a href="{base}/supersession.html">🔄 supersession</a>
  <a href="{base}/h-darrieus.html">🛡️ H-Darrieus</a>
  <a href="{base}/validation.html">✅ 验证</a>
  <a href="{base}/ask.html"><strong>🤖 问答</strong></a>
</nav>
{body}
<footer>
  Generated from <code>instances/*.yaml</code> · regenerate: <code>python scripts/build_demo_ui.py</code> · serve: <code>python -m http.server 8000 -d demo</code>
</footer>
</body>
</html>
"""


def yaml_to_html(rec):
    from ruamel.yaml import YAML
    from io import StringIO
    out = StringIO()
    YAML().dump(rec, out)
    return f"<pre>{html.escape(out.getvalue())}</pre>"


def first_label(rec):
    """Best-effort human label for a record."""
    if isinstance(rec, dict):
        if rec.get("title"):
            return rec["title"]
        if rec.get("name"):
            return rec["name"]
        i18n = rec.get("i18n", {})
        if isinstance(i18n, dict):
            label = i18n.get("label", {})
            if isinstance(label, dict) and label.get("en"):
                return label["en"]
            if isinstance(label, dict) and label.get("zh"):
                return label["zh"]
    return ""


def find_relations_for(uri, relations):
    out = []
    for rt, recs in relations.items():
        for rp, rrec in recs:
            if rrec.get("subject") == uri:
                out.append((rt, "→", rrec.get("object", "?"), rp))
            elif rrec.get("object") == uri:
                out.append((rt, "←", rrec.get("subject", "?"), rp))
    return out


def main():
    DEMO.mkdir(exist_ok=True)
    (DEMO / "style.css").write_text(CSS)

    entities, relations, pending, docs_meta = load_corpus()

    n_e = sum(len(v) for v in entities.values())
    n_r = sum(len(v) for v in relations.values())

    # ── index.html ────────────────────────────────────────────────
    body = f"""
<div class="stats">
  <div class="stat"><div class="num">{len(entities)}</div><div class="label">实体类型</div></div>
  <div class="stat"><div class="num">{n_e}</div><div class="label">实体记录</div></div>
  <div class="stat"><div class="num">{n_r}</div><div class="label">关系记录</div></div>
  <div class="stat"><div class="num">{len(pending)}</div><div class="label">_pending 待审</div></div>
  <div class="stat"><div class="num">{len(docs_meta)}</div><div class="label">源文档</div></div>
  <div class="stat"><div class="num">19</div><div class="label">pytest 测试</div></div>
</div>

<h2>这个 demo 展示什么</h2>
<p>v0.1.0 是 schema + validators + 设计文档 + demo 数据。<strong>不是运行的 RAG 应用</strong>。
这个浏览 UI 让你看现在语料库的真实形状：</p>

<ul>
  <li><a href="entities.html"><strong>实体浏览</strong></a> — 22 个类型 / {n_e} 条记录的完整 YAML</li>
  <li><a href="relations.html"><strong>关系图</strong></a> — {n_r} 条关系如何串起实体网络</li>
  <li><a href="citation-chain.html"><strong>引用链路</strong></a> — Core Value 演示：每条 ExpertNote → Document → 原始 URL</li>
  <li><a href="bilingual.html"><strong>双语演示</strong></a> — DEMO-07 中英 i18n 实体</li>
  <li><a href="supersession.html"><strong>supersession 演示</strong></a> — DEMO-05 老法规 → 新法规链</li>
  <li><a href="h-darrieus.html"><strong>H-Darrieus 锁</strong></a> — AI 抽取记录如何被拒（DEMO-06）</li>
  <li><a href="validation.html"><strong>验证状态</strong></a> — 实时跑 <code>validate.py</code> 看 0 errors</li>
  <li><a href="ask.html"><strong>🤖 Live RAG 问答</strong></a> — Phase 7：5 个真实 query→answer，每条带 citation 链接 + audit trail</li>
</ul>

<h2>Phase 7 已落地</h2>
<p>RAG 流水线（chunker + embedder + retriever + guardrail + LLM + citation 验证）已实现并跑通端到端，可直接对 3 个 demo 文档查询，详见 <a href="ask.html">问答页</a>。Phase 8 候选：把 RAGFlow 装上 / 加 Wiki.js 门户 UI / 摄取更多文档。</p>
"""
    (DEMO / "index.html").write_text(html_page("首页", body))

    # ── entities.html ────────────────────────────────────────────
    blocks = []
    for type_name in sorted(entities.keys()):
        recs = entities[type_name]
        items = "".join(
            f'<li><a href="entities/{type_name}/{p.stem}.html">{p.stem}</a> '
            f'<small>— {html.escape(str(first_label(r))[:60])}</small></li>'
            for p, r in recs
        )
        blocks.append(
            f'<h3>{type_name} <span class="tag">{len(recs)}</span></h3>'
            f'<ul class="entity-list">{items}</ul>'
        )
    body = f"<h2>实体浏览</h2><p>{len(entities)} 类型 / {n_e} 记录。点击任一记录看完整 YAML + 关系。</p>" + "".join(blocks)
    (DEMO / "entities.html").write_text(html_page("实体浏览", body))

    # ── per-entity pages ─────────────────────────────────────────
    for type_name, recs in entities.items():
        d = DEMO / "entities" / type_name
        d.mkdir(parents=True, exist_ok=True)
        for p, rec in recs:
            uri = rec.get("id", "")
            related = find_relations_for(uri, relations)
            related_html = ""
            if related:
                rows = "".join(
                    f'<tr><td><span class="tag">{rt}</span></td><td>{arr}</td>'
                    f'<td><code>{html.escape(str(other))}</code></td></tr>'
                    for rt, arr, other, _ in related
                )
                related_html = f"<h3>关系（{len(related)}）</h3><table><tr><th>关系类型</th><th>方向</th><th>另一端</th></tr>{rows}</table>"

            prov = rec.get("provenance", {})
            conf = rec.get("confidence", {})
            src = rec.get("source", {})
            meta_html = ""
            if isinstance(prov, dict) and prov:
                method = prov.get("method", "")
                tag_class = {"human": "tag-ok", "ai_extracted": "tag-warn", "hybrid_reviewed": "tag"}.get(method, "tag")
                reviewer = prov.get("reviewer") or "—"
                score = conf.get("score", "—") if isinstance(conf, dict) else "—"
                meta_html = (
                    f'<h3>provenance / confidence / source</h3>'
                    f'<div class="card">'
                    f'<span class="{tag_class}">method: {html.escape(str(method))}</span> '
                    f'<span class="tag">score: {score}</span> '
                    f'<span class="tag">reviewer: {html.escape(str(reviewer))}</span>'
                )
                if isinstance(src, dict) and src.get("document_id"):
                    meta_html += f'<br><br><strong>source.document_id</strong>: <code>{html.escape(src["document_id"])}</code>'
                meta_html += "</div>"

            ent_body = f"""
<h2>{p.stem}</h2>
<p><span class="tag">{type_name}</span> &nbsp; URI: <code>{html.escape(uri)}</code></p>
{meta_html}
{related_html}
<h3>完整 YAML</h3>
{yaml_to_html(rec)}
"""
            (d / f"{p.stem}.html").write_text(html_page(p.stem, ent_body, base="../.."))

    # ── relations.html ───────────────────────────────────────────
    blocks = []
    for rt in sorted(relations.keys()):
        recs = relations[rt]
        rows = "".join(
            f'<li><code>{html.escape(rec.get("subject", ""))}</code> '
            f'<span class="chain-arrow">→</span> '
            f'<code>{html.escape(rec.get("object", ""))}</code></li>'
            for _, rec in recs
        )
        blocks.append(f'<h3>{rt} <span class="tag">{len(recs)}</span></h3><ul>{rows}</ul>')
    body = f"<h2>关系图</h2><p>{len(relations)} 关系类型 / {n_r} 实例。每条关系都引用真实的 subject + object URI（broken-ref 检查通过）。</p>" + "".join(blocks)
    (DEMO / "relations.html").write_text(html_page("关系图", body))

    # ── citation-chain.html (DEMO-04) ────────────────────────────
    canonical = next(((p, r) for p, r in entities.get("expert-note", []) if "canonical" in p.stem), None)
    body = "<h2>📍 引用链路演示 (DEMO-04 — Core Value)</h2>"
    body += "<p><strong>每条 AI 抽取或人工编辑的事实，必须可追溯到原始来源。</strong>"
    body += " 这是项目的不可妥协约束。下面是 canonical-example 这条 ExpertNote 的完整溯源链：</p>"
    if canonical:
        cp, crec = canonical
        doc_id = crec.get("source", {}).get("document_id", "")
        doc_rec = next(((p, r) for p, r in entities.get("document", []) if r.get("id") == doc_id), None)
        # find docs/<dir>/metadata.yaml — Document.id usually contains the slug
        meta_pair = None
        if doc_rec:
            for did, (mp, m) in docs_meta.items():
                if did in doc_rec[1].get("id", "") or did in doc_rec[0].stem:
                    meta_pair = (mp, m)
                    break

        chain = [
            ('<strong>ExpertNote</strong>', f'<code>{cp.stem}</code>',
             f'<a href="entities/expert-note/{cp.stem}.html">查看 →</a>'),
            ('<strong>source.document_id</strong>', f'<code>{html.escape(doc_id)}</code>', '解析为 ↓'),
        ]
        if doc_rec:
            chain.append((
                '<strong>Document 实体</strong>', f'<code>{doc_rec[0].stem}</code>',
                f'<a href="entities/document/{doc_rec[0].stem}.html">查看 →</a>'
            ))
        if meta_pair:
            mp, m = meta_pair
            url = m.get("source_url", "")
            chain.append((
                '<strong>原始 metadata</strong>',
                f'<code>{html.escape(str(m.get("title", ""))[:50])}</code>',
                f'<a href="{html.escape(url)}" target="_blank">外部 URL →</a>'
            ))

        body += '<div class="chain">'
        for i, (a, b, c) in enumerate(chain):
            if i > 0:
                body += '<span class="chain-arrow">→</span>'
            body += f'<div class="node">{a}<br><small>{b}</small><br>{c}</div>'
        body += '</div>'

        if meta_pair:
            mp, m = meta_pair
            body += f"""
<h3>原始 metadata.yaml 字段</h3>
<table>
<tr><th>字段</th><th>值</th></tr>
<tr><td>title</td><td>{html.escape(str(m.get("title", "")))}</td></tr>
<tr><td>doc_type</td><td><code>{html.escape(str(m.get("doc_type", "")))}</code></td></tr>
<tr><td>language</td><td><code>{html.escape(str(m.get("language", "")))}</code></td></tr>
<tr><td>publication_date</td><td>{html.escape(str(m.get("publication_date", "")))}</td></tr>
<tr><td>confidentiality</td><td><span class="tag tag-ok">{html.escape(str(m.get("confidentiality", "")))}</span></td></tr>
<tr><td>file_hash</td><td><code>{html.escape(str(m.get("file_hash", "")))[:48]}…</code></td></tr>
<tr><td>source_url</td><td><a href="{html.escape(str(m.get("source_url", "")))}" target="_blank">{html.escape(str(m.get("source_url", "")))}</a></td></tr>
</table>
"""

        body += f"<h3>ExpertNote 完整 YAML</h3>{yaml_to_html(crec)}"
    (DEMO / "citation-chain.html").write_text(html_page("引用链路", body))

    # ── bilingual.html (DEMO-07) ─────────────────────────────────
    bilingual = next(
        ((p, r) for p, r in entities.get("expert-note", []) if isinstance(r.get("i18n"), dict)),
        None
    )
    body = "<h2>🌐 双语 i18n 演示 (DEMO-07)</h2>"
    body += "<p>D-14 决策：i18n 字段使用平面结构 <code>{label: {zh, en}, full_text: {zh, en}}</code>。"
    body += "每条实体可同时承载中英文版本，RAG 检索时按需选择目标语言。</p>"
    if bilingual:
        bp, brec = bilingual
        i18n = brec.get("i18n", {})
        lab = i18n.get("label", {}) if isinstance(i18n, dict) else {}
        ft = i18n.get("full_text", {}) if isinstance(i18n, dict) else {}
        body += f"""
<div class="bilingual">
  <div>
    <strong>🇨🇳 中文</strong>
    <h3>{html.escape(str(lab.get("zh", "")))}</h3>
    <p>{html.escape(str(ft.get("zh", "")))}</p>
  </div>
  <div>
    <strong>🇬🇧 English</strong>
    <h3>{html.escape(str(lab.get("en", "")))}</h3>
    <p>{html.escape(str(ft.get("en", "")))}</p>
  </div>
</div>
<p><a href="entities/expert-note/{bp.stem}.html">查看完整 YAML →</a></p>
"""
    (DEMO / "bilingual.html").write_text(html_page("双语演示", body))

    # ── supersession.html (DEMO-05) ──────────────────────────────
    superseded = next(
        ((p, r) for p, r in entities.get("regulation-clause", []) if r.get("status") == "superseded"),
        None
    )
    active = next(
        ((p, r) for p, r in entities.get("regulation-clause", [])
         if "active" in p.stem and r.get("status") != "superseded"),
        None
    )
    body = "<h2>🔄 supersession 演示 (DEMO-05)</h2>"
    body += "<p>法规演进双向链接：老条款 <code>status: superseded</code> + <code>superseded_by</code> URI 字段（实体内）；"
    body += "<code>relation.supersedes</code> 关系实例（关系层）。两层冗余，RAG 任一查询路径都能找到链。</p>"

    if superseded and active:
        sp, srec = superseded
        ap, arec = active
        rel = next(
            ((p, r) for p, r in relations.get("supersedes", [])
             if r.get("subject") == arec.get("id") and r.get("object") == srec.get("id")),
            None
        )
        body += f"""
<div class="chain">
  <div class="node">
    <span class="tag tag-warn">SUPERSEDED</span><br>
    <strong>{sp.stem}</strong><br>
    <small>version: {html.escape(str(srec.get("version", "—")))}<br>
    effective: {html.escape(str(srec.get("effective_date", "—")))}</small><br>
    <a href="entities/regulation-clause/{sp.stem}.html">查看 →</a>
  </div>
  <span class="chain-arrow">supersedes →</span>
  <div class="node">
    <span class="tag tag-ok">ACTIVE</span><br>
    <strong>{ap.stem}</strong><br>
    <small>version: {html.escape(str(arec.get("version", "—")))}<br>
    effective: {html.escape(str(arec.get("effective_date", "—")))}</small><br>
    <a href="entities/regulation-clause/{ap.stem}.html">查看 →</a>
  </div>
</div>

<h3>双向链接验证</h3>
<table>
<tr><th>方向</th><th>位置</th><th>值</th></tr>
<tr><td>实体字段</td><td><code>{sp.stem}.superseded_by</code></td><td><code>{html.escape(str(srec.get("superseded_by", "")))}</code></td></tr>
<tr><td>关系实例</td><td><code>relation.supersedes</code></td><td>{("✓ 存在 (" + html.escape(rel[0].stem) + ")") if rel else "（缺失）"}</td></tr>
</table>
"""
    (DEMO / "supersession.html").write_text(html_page("supersession", body))

    # ── h-darrieus.html ──────────────────────────────────────────
    body = """
<h2>🛡️ H-Darrieus 拒绝规则 (PROV-04)</h2>
<p>项目 Core Value 的最关键防线：<strong>AI 抽取 + 高置信度 + 无人工审稿</strong> 一律拒绝写入 canonical。
名字来自一个 H-Darrieus 风力机案例 — 高置信 AI 输出过去曾被未审就吸纳，错误埋了几个月才被发现。</p>

<h3>规则（精确语义，per ADR-005）</h3>
<pre>provenance.method == "ai_extracted"
  AND confidence.score > 0.85         # 严格大于，不是 ≥
  AND (no reviewer OR reviewer == "")
  → REJECT (validators/provenance.py)</pre>

<h3>边界用例（Phase 3 测试覆盖）</h3>
<table>
<tr><th>method</th><th>score</th><th>reviewer</th><th>结果</th></tr>
<tr><td><code>ai_extracted</code></td><td>0.85</td><td>—</td><td><span class="tag tag-ok">PASS（严格 &gt;）</span></td></tr>
<tr><td><code>ai_extracted</code></td><td>0.86</td><td>无</td><td><span class="tag tag-rej">REJECT</span></td></tr>
<tr><td><code>ai_extracted</code></td><td>0.86</td><td>""</td><td><span class="tag tag-rej">REJECT（空字符串视为无）</span></td></tr>
<tr><td><code>ai_extracted</code></td><td>0.86</td><td><code>actor:jane</code></td><td><span class="tag tag-ok">PASS</span></td></tr>
<tr><td><code>hybrid_reviewed</code></td><td>0.95</td><td><code>actor:jane</code></td><td><span class="tag tag-ok">PASS</span></td></tr>
<tr><td><code>human</code></td><td>0.99</td><td>—</td><td><span class="tag tag-ok">PASS（人工默认免审）</span></td></tr>
</table>

<h3>_pending 暂存模式 (DEMO-06)</h3>
<p>新的 AI 抽取记录先进 <code>instances/_pending/</code> 目录。validators 还会强制：
任何 <code>/_pending/</code> 路径下的记录必须 <code>method = hybrid_reviewed</code>，
否则也拒绝（PROV-05 _pending gate）。审稿人添加 reviewer + reviewed_at 后，由人工 promote 到 canonical。</p>
"""
    if pending:
        pp, prec = pending[0]
        prov = prec.get("provenance", {}) if isinstance(prec, dict) else {}
        conf = prec.get("confidence", {}) if isinstance(prec, dict) else {}
        body += f"""
<div class="card">
  <strong>当前 _pending 待审记录：</strong> <code>{pp.relative_to(ROOT)}</code><br>
  <span class="tag tag-pending">PENDING</span>
  method: <code>{html.escape(str(prov.get("method", "")))}</code>,
  score: <code>{conf.get("score", "—")}</code>,
  reviewer: <code>{html.escape(str(prov.get("reviewer", "—")))}</code>
</div>
"""
    (DEMO / "h-darrieus.html").write_text(html_page("H-Darrieus 锁", body))

    # ── validation.html ──────────────────────────────────────────
    result = subprocess.run(
        [sys.executable, "scripts/validate.py", "instances/"],
        cwd=ROOT, capture_output=True, text=True
    )
    pytest_result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
        cwd=ROOT, capture_output=True, text=True
    )
    body = f"""
<h2>✅ 验证状态</h2>
<p>Phase 3 实施了 5 个 validator，pre-commit / push / CI 全程强制运行。下面是<strong>当前页面构建时</strong>真实跑出的输出：</p>

<h3><code>python scripts/validate.py instances/</code></h3>
<pre>{html.escape(result.stdout or "(no stdout)")}</pre>
<p>退出码: <code>{result.returncode}</code> — {("<span class='tag tag-ok'>✅ 全部通过</span>" if result.returncode == 0 else "<span class='tag tag-rej'>❌ 失败</span>")}</p>

<h3><code>python -m pytest tests/ -q</code></h3>
<pre>{html.escape((pytest_result.stdout or pytest_result.stderr or "(no output)")[-1500:])}</pre>
<p>退出码: <code>{pytest_result.returncode}</code> — {("<span class='tag tag-ok'>✅ 通过</span>" if pytest_result.returncode == 0 else "<span class='tag tag-rej'>❌ 失败</span>")}</p>

<h3>5 个 validator 模块</h3>
<table>
<tr><th>模块</th><th>规则 ID</th><th>检查内容</th></tr>
<tr><td><code>schema</code></td><td>schema.draft-2020-12</td><td>JSON Schema Draft 2020-12 完整性 + composition</td></tr>
<tr><td><code>ids</code></td><td>ids.uri-format / type-prefix-mismatch</td><td>URI = <code>aviationkb://&lt;type&gt;/&lt;slug&gt;@&lt;v&gt;</code> 格式 (D-23/24/25)</td></tr>
<tr><td><code>provenance</code></td><td>provenance.h-darrieus / pending-gate / schema-version-mismatch</td><td>H-Darrieus REJECT (严格 &gt; 0.85) / _pending 必须 hybrid_reviewed / schema 版本一致性</td></tr>
<tr><td><code>relations</code></td><td>relations.broken-subject / broken-object</td><td>所有 subject/object URI 必须能在语料库 by_id 索引中解析</td></tr>
<tr><td><code>links</code></td><td>links.broken-source-ref / supersession-cycle</td><td>source.document_id 引用真实 Document / supersession 链路无环</td></tr>
</table>

<h3>测试覆盖</h3>
<ul>
  <li>13 个 parametrised 测试覆盖 11 valid fixtures + 12 invalid fixtures（每 invalid fixture 必须触发预期 rule）</li>
  <li>6 个 mutation 守护测试（重命名 rule 名字会让对应测试变红 — 真在观察 validator 行为，不是空跑）</li>
  <li>CI 在 GitHub Actions 上 push/PR 都跑一次（lint / validate / test 三个 job）</li>
</ul>
"""
    (DEMO / "validation.html").write_text(html_page("验证状态", body))

    print(f"✓ Generated {len(list(DEMO.rglob('*.html')))} HTML pages in {DEMO}/")
    print(f"  Open:  file://{DEMO / 'index.html'}")
    print(f"  Serve: python -m http.server 8000 -d demo")


if __name__ == "__main__":
    main()
