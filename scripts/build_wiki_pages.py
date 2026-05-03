"""Generate wiki/ markdown from instances/ + docs/ for Wiki.js import.

Each entity / document / source becomes a Wiki.js page:
- wiki/index.md                            — landing
- wiki/entities/<type>/index.md           — type list
- wiki/entities/<type>/<slug>.md          — per-record markdown w/ YAML embed
- wiki/relations/index.md                 — relations index
- wiki/documents/<id>.md                  — source document with metadata
- wiki/glossary.md                        — bilingual glossary

Wiki.js page format: frontmatter + Markdown body (KaTeX-friendly).

Usage: python scripts/build_wiki_pages.py
Output: wiki/ subdirectory (gitignored from canonical scope per DEP-04;
        used as the local content source for Wiki.js Storage module sync).
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime

from ruamel.yaml import YAML
from io import StringIO

ROOT = Path(__file__).resolve().parent.parent
INSTANCES = ROOT / "instances"
DOCS = ROOT / "docs"
WIKI = ROOT / "wiki"
GLOSSARY_SRC = ROOT / "docs" / "GLOSSARY.md"

yaml = YAML(typ="safe")


def page_frontmatter(title: str, description: str, tags: list[str], path: str) -> str:
    """Wiki.js 2.x page frontmatter (front-matter format)."""
    today = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    tags_str = ", ".join(tags)
    return f"""---
title: {title}
description: {description}
published: true
date: {today}
tags: {tags_str}
editor: markdown
dateCreated: {today}
---

"""


def yaml_block(rec: dict) -> str:
    out = StringIO()
    YAML().dump(rec, out)
    return f"```yaml\n{out.getvalue()}```\n"


def slugify(s: str) -> str:
    return s.replace("_", "-").lower()


def main():
    if WIKI.exists():
        # Clean & regenerate
        import shutil
        shutil.rmtree(WIKI)
    WIKI.mkdir()

    # Load corpus
    entities: dict[str, list] = defaultdict(list)
    relations: dict[str, list] = defaultdict(list)
    pending: list = []
    documents: dict = {}

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
        documents[p.parent.name] = (p, meta)

    n_entities = sum(len(v) for v in entities.values())
    n_relations = sum(len(v) for v in relations.values())

    # ── wiki/index.md (Home) ─────────────────────────────────────
    body = f"""# ✈️ Aviation Knowledge Base

> v0.1.0 corpus portal · 每条知识可追溯 · AI 回答带 citation

This is the Wiki.js portal mirroring the canonical YAML corpus at [GitHub](https://github.com/kogamishinyajerry-ops/aviation-knowledge-base). Pages here are auto-generated from `instances/` — edit YAML in Git, regenerate via `python scripts/build_wiki_pages.py`.

## 语料概览

- **{len(entities)}** 实体类型 / **{n_entities}** 实体记录
- **{len(relations)}** 关系类型 / **{n_relations}** 关系实例
- **{len(pending)}** AI 抽取待审 (`_pending/`)
- **{len(documents)}** 源文档（regulations / cfd-papers / accident-reports）

## 快速导航

- **[实体目录](/entities)** — 22 类型完整列表
- **[关系目录](/relations)** — 8 关系实例 × 6 类型
- **[源文档](/documents)** — FAR §25.1309 / NASA TM-2014-218175 / NTSB AAR-09-03
- **[术语表](/glossary)** — 73 双语条目
- **[设计文档](https://github.com/kogamishinyajerry-ops/aviation-knowledge-base/blob/main/.planning/design/PRD_v1.md)** — PRD v1 完整规格

## 编辑流程（DEP-04）

> **硬规则**：Wiki.js Git 同步范围 = `wiki/` **子目录**唯一。`instances/` / `ontology/` / `scripts/` 永不通过 Wiki.js 写。

1. 在 Wiki.js 编辑页面 → 自动 push 到 `wiki/` 分支
2. CI 跑 `python scripts/validate.py instances/` — 不影响 Wiki.js（Wiki.js 内容 ≠ canonical 数据）
3. 真要改 schema/instance：在 Git 改 `instances/*.yaml` → PR → 合并 → 重跑 `build_wiki_pages.py` 同步回 Wiki.js
"""
    (WIKI / "index.md").write_text(page_frontmatter(
        "Aviation Knowledge Base", "v0.1.0 corpus portal", ["index"], "/"
    ) + body)

    # ── wiki/entities/index.md ───────────────────────────────────
    (WIKI / "entities").mkdir()
    type_list = []
    for type_name in sorted(entities.keys()):
        recs = entities[type_name]
        type_list.append(f"- **[{type_name}](/entities/{type_name})** — {len(recs)} 条记录")
    body = f"""# 实体目录

{n_entities} 条记录跨 {len(entities)} 类型。每条点开看 YAML + 来源 + 关系。

{chr(10).join(type_list)}
"""
    (WIKI / "entities" / "index.md").write_text(page_frontmatter(
        "Entities", f"{n_entities} records across {len(entities)} types",
        ["entities"], "/entities"
    ) + body)

    # ── per-type + per-record pages ──────────────────────────────
    for type_name, recs in entities.items():
        type_dir = WIKI / "entities" / type_name
        type_dir.mkdir(exist_ok=True)
        # type index
        items = []
        for p, rec in recs:
            label = rec.get("title") or rec.get("name") or rec.get("id", "")
            items.append(f"- [{p.stem}](/entities/{type_name}/{p.stem}) — {label[:80]}")
        (type_dir / "index.md").write_text(page_frontmatter(
            type_name.replace("-", " ").title(),
            f"{len(recs)} {type_name} records",
            ["entities", type_name],
            f"/entities/{type_name}"
        ) + f"# {type_name}\n\n{len(recs)} 条记录。\n\n" + "\n".join(items))

        # per-record
        for p, rec in recs:
            uri = rec.get("id", "")
            prov = rec.get("provenance", {}) if isinstance(rec, dict) else {}
            method = prov.get("method", "") if isinstance(prov, dict) else ""
            reviewer = prov.get("reviewer", "—") if isinstance(prov, dict) else "—"
            conf = rec.get("confidence", {}) if isinstance(rec, dict) else {}
            score = conf.get("score", "—") if isinstance(conf, dict) else "—"

            # find relations involving this record
            related = []
            for rt, rrecs in relations.items():
                for _, rrec in rrecs:
                    if rrec.get("subject") == uri:
                        related.append(f"- `{rt}` → [{rrec.get('object', '?')}](/{rrec.get('object', '').replace('aviationkb://', '')})")
                    elif rrec.get("object") == uri:
                        related.append(f"- ← `{rt}` from [{rrec.get('subject', '?')}](/{rrec.get('subject', '').replace('aviationkb://', '')})")

            body = f"""# {p.stem}

**Type**: `{type_name}` &nbsp; **URI**: `{uri}`

## Provenance

| 字段 | 值 |
|------|-----|
| method | `{method}` |
| reviewer | `{reviewer}` |
| confidence.score | {score} |

"""
            src = rec.get("source", {}) if isinstance(rec, dict) else {}
            if isinstance(src, dict) and src.get("document_id"):
                body += f"**Source**: [{src['document_id']}](/documents/{src['document_id'].split('/')[-1].split('@')[0]})\n\n"

            if related:
                body += f"## Relations ({len(related)})\n\n" + "\n".join(related) + "\n\n"

            body += f"## YAML\n\n{yaml_block(rec)}\n"
            body += f"\n---\n\n*Source of truth: `instances/entities/{type_name}/{p.stem}.yaml` on Git. Edit YAML there; regenerate this page.*\n"

            (type_dir / f"{p.stem}.md").write_text(page_frontmatter(
                p.stem,
                str(rec.get("title") or rec.get("name") or "")[:120],
                ["entities", type_name],
                f"/entities/{type_name}/{p.stem}"
            ) + body)

    # ── wiki/relations/index.md ──────────────────────────────────
    (WIKI / "relations").mkdir()
    body = f"# 关系图\n\n{n_relations} 实例 / {len(relations)} 类型。\n\n"
    for rt in sorted(relations.keys()):
        recs = relations[rt]
        body += f"## {rt} ({len(recs)})\n\n"
        for p, rec in recs:
            body += f"- `{rec.get('subject', '')}` → `{rec.get('object', '')}`\n"
        body += "\n"
    (WIKI / "relations" / "index.md").write_text(page_frontmatter(
        "Relations", f"{n_relations} relation instances",
        ["relations"], "/relations"
    ) + body)

    # ── wiki/documents/index.md + per-doc ─────────────────────────
    (WIKI / "documents").mkdir()
    doc_list = []
    for did, (mp, m) in sorted(documents.items()):
        doc_list.append(f"- **[{did}](/documents/{did})** — {m.get('title', '')[:80]}")
    (WIKI / "documents" / "index.md").write_text(page_frontmatter(
        "Documents", f"{len(documents)} source documents", ["documents"], "/documents"
    ) + f"# 源文档\n\n{chr(10).join(doc_list)}\n")

    for did, (mp, m) in documents.items():
        doc_dir = mp.parent
        processed = (doc_dir / "processed.md").read_text() if (doc_dir / "processed.md").exists() else ""
        body = f"""# {m.get('title', did)}

| 字段 | 值 |
|------|-----|
| doc_id | `{did}` |
| doc_type | `{m.get('doc_type', '')}` |
| language | `{m.get('language', '')}` |
| publication_date | {m.get('publication_date', '')} |
| effective_date | {m.get('effective_date', '')} |
| confidentiality | `{m.get('confidentiality', '')}` |
| version | {m.get('version', '')} |
| file_hash | `{str(m.get('file_hash', ''))[:48]}…` |
| processed_by | {m.get('processed_by', '')} |
| source_url | [{m.get('source_url', '')}]({m.get('source_url', '#')}) |

## Processed Content

{processed}

---

*Source: `docs/{doc_dir.parent.name}/{did}/`*
"""
        (WIKI / "documents" / f"{did}.md").write_text(page_frontmatter(
            did, m.get("title", "")[:120], ["documents", m.get("doc_type", "")],
            f"/documents/{did}"
        ) + body)

    # ── wiki/glossary.md ──────────────────────────────────────────
    if GLOSSARY_SRC.exists():
        (WIKI / "glossary.md").write_text(page_frontmatter(
            "Glossary", "73 bilingual aviation terms", ["glossary"], "/glossary"
        ) + GLOSSARY_SRC.read_text())

    n_pages = sum(1 for _ in WIKI.rglob("*.md"))
    print(f"✓ Generated {n_pages} Wiki.js pages in {WIKI}/")
    print(f"  Import path: Wiki.js admin → Storage → Git/LocalFS module → point at {WIKI}/")


if __name__ == "__main__":
    main()
