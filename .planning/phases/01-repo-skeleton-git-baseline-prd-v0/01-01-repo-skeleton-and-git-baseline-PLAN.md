---
phase: 01-repo-skeleton-git-baseline-prd-v0
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .gitignore
  - .gitattributes
  - ontology/.gitkeep
  - ontology/schemas/.gitkeep
  - ontology/vocabularies/.gitkeep
  - ontology/mappings/.gitkeep
  - instances/.gitkeep
  - instances/entities/.gitkeep
  - instances/relations/.gitkeep
  - instances/_pending/.gitkeep
  - docs/.gitkeep
  - wiki/.gitkeep
  - deploy/.gitkeep
  - deploy/caddy/.gitkeep
  - deploy/authentik/.gitkeep
  - scripts/.gitkeep
  - scripts/validators/.gitkeep
  - scripts/importers/.gitkeep
  - scripts/exporters/to_ragflow.py
  - scripts/exporters/to_rdf.py
  - scripts/exporters/to_neo4j.py
  - scripts/exporters/to_jsonl_triples.py
  - tests/.gitkeep
  - tests/fixtures/valid/.gitkeep
  - tests/fixtures/invalid/.gitkeep
  - evaluation/.gitkeep
  - process-log/.gitkeep
autonomous: true
requirements:
  - REPO-01
  - REPO-02

must_haves:
  truths:
    - "Top-level directory tree under repo root matches research/ARCHITECTURE.md (`ontology/`, `instances/`, `docs/`, `wiki/`, `deploy/`, `scripts/`, `tests/`, `evaluation/`, `process-log/`) — 9 directories visible at depth 1"
    - "`.gitattributes` configures Git LFS for `*.pdf`, `*.docx`, `*.xlsx`, `*.pptx` BEFORE any binary source document is added"
    - "`.gitignore` excludes secrets (`.env`, `*.key`, `*.pem`), Python/Node build artifacts, OS junk"
    - "Exporter stub files exist under `scripts/exporters/` (to_ragflow.py / to_rdf.py / to_neo4j.py / to_jsonl_triples.py) — placeholders with docstring + `NotImplementedError`, signaling future migration hooks (per ARCHITECTURE.md guardrail #3)"
    - "Empty subdirectories that are part of the locked layout retain their `.gitkeep` so the structure is committed and visible to a fresh clone"
  artifacts:
    - path: ".gitattributes"
      provides: "Git LFS routing for binary aviation source documents"
      contains: "*.pdf filter=lfs"
    - path: ".gitignore"
      provides: "Exclusion of secrets, build artifacts, OS files"
      contains: ".env"
    - path: "ontology/schemas/.gitkeep"
      provides: "Schema directory placeholder (Phase 2 fills it)"
    - path: "instances/_pending/.gitkeep"
      provides: "AI-extracted quarantine zone exists from day 1 (per Pitfall 2 / SUMMARY pinned decision #10)"
    - path: "scripts/exporters/to_ragflow.py"
      provides: "Future Git→RAGFlow exporter stub (per ARCHITECTURE.md Pattern 4 / SUMMARY decision #7)"
    - path: "scripts/exporters/to_rdf.py"
      provides: "Future YAML→RDF/Turtle exporter stub (GraphRAG migration hook)"
    - path: "scripts/exporters/to_neo4j.py"
      provides: "Future YAML→Cypher exporter stub (GraphRAG migration hook)"
    - path: "scripts/exporters/to_jsonl_triples.py"
      provides: "Future YAML→JSONL `{s,p,o,prov}` exporter stub (per SUMMARY open question #4)"
  key_links:
    - from: ".gitattributes"
      to: "Git LFS"
      via: "filter=lfs diff=lfs merge=lfs -text"
      pattern: "\\*\\.pdf filter=lfs"
    - from: "scripts/exporters/*.py"
      to: "future Phase 5 (RAGFlow) / future v2 (RDF/Neo4j)"
      via: "stub function bodies signaling intent"
      pattern: "NotImplementedError|TODO\\(phase"
---

<objective>
Create the complete repo directory skeleton (9 top-level directories per ARCHITECTURE.md), configure Git LFS via `.gitattributes` BEFORE any binary lands, write `.gitignore` to keep secrets and noise out, and drop exporter STUB files under `scripts/exporters/` so the architectural intent ("all KB consumers go through exporters; adding a backend = new exporter, not refactor" — ARCHITECTURE.md guardrail #3) is visible to every future contributor.

Purpose: This is the foundation. Every later phase (Phase 2 schemas, Phase 3 validators, Phase 4 demo data, Phase 5 RAG pipeline, Phase 6 deployment) writes into directories that MUST exist and follow ARCHITECTURE.md exactly. Git LFS MUST be configured before the first PDF is committed, otherwise the repo gets polluted and recovery is expensive (P40 in PITFALLS technical debt table: "Git 仓库塞满 PDF 不开 LFS").

Output: Locked directory tree + `.gitignore` + `.gitattributes` + 4 exporter stubs, all committed atomically.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/research/ARCHITECTURE.md
@.planning/research/SUMMARY.md
@.planning/research/PITFALLS.md
@CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create the locked directory skeleton with .gitkeep placeholders</name>
  <files>
    ontology/.gitkeep, ontology/schemas/.gitkeep, ontology/vocabularies/.gitkeep, ontology/mappings/.gitkeep,
    instances/.gitkeep, instances/entities/.gitkeep, instances/relations/.gitkeep, instances/_pending/.gitkeep,
    docs/.gitkeep, wiki/.gitkeep,
    deploy/.gitkeep, deploy/caddy/.gitkeep, deploy/authentik/.gitkeep,
    scripts/.gitkeep, scripts/validators/.gitkeep, scripts/importers/.gitkeep,
    tests/.gitkeep, tests/fixtures/valid/.gitkeep, tests/fixtures/invalid/.gitkeep,
    evaluation/.gitkeep, process-log/.gitkeep
  </files>
  <read_first>
    - .planning/research/ARCHITECTURE.md (Recommended Project Structure section, lines 103–256 — defines the EXACT directory tree this task must materialize)
    - .planning/research/SUMMARY.md (Architecture > Repo structure block, lines 92–127)
  </read_first>
  <action>
Run from repo root `/Users/Zhuanz/aviation-knowledge-base`:

```bash
cd /Users/Zhuanz/aviation-knowledge-base

# Top-level dirs (9 per success criterion #1)
mkdir -p ontology/schemas ontology/vocabularies ontology/mappings
mkdir -p instances/entities instances/relations instances/_pending
mkdir -p docs wiki
mkdir -p deploy/caddy deploy/authentik
mkdir -p scripts/validators scripts/importers scripts/exporters
mkdir -p tests/fixtures/valid tests/fixtures/invalid
mkdir -p evaluation process-log

# .gitkeep placeholders so empty dirs commit
for d in \
  ontology ontology/schemas ontology/vocabularies ontology/mappings \
  instances instances/entities instances/relations instances/_pending \
  docs wiki \
  deploy deploy/caddy deploy/authentik \
  scripts scripts/validators scripts/importers \
  tests tests/fixtures/valid tests/fixtures/invalid \
  evaluation process-log
do
  touch "$d/.gitkeep"
done
```

Note: `scripts/exporters/` does NOT get a `.gitkeep` because Task 3 will populate it with 4 real stub `.py` files.

Do NOT create files inside `.planning/` — that directory is already managed by GSD.

Do NOT create `.github/workflows/` here — Plan 04 owns that path.

Do NOT create `README.md` here — Plan 02 owns it.
  </action>
  <verify>
    <automated>cd /Users/Zhuanz/aviation-knowledge-base &amp;&amp; test "$(find ontology instances docs wiki deploy scripts tests evaluation process-log -maxdepth 0 -type d 2>/dev/null | wc -l | tr -d ' ')" = "9" &amp;&amp; test -f ontology/schemas/.gitkeep &amp;&amp; test -f instances/_pending/.gitkeep &amp;&amp; test -f tests/fixtures/invalid/.gitkeep &amp;&amp; test -d scripts/exporters &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - `find /Users/Zhuanz/aviation-knowledge-base -maxdepth 1 -type d \( -name ontology -o -name instances -o -name docs -o -name wiki -o -name deploy -o -name scripts -o -name tests -o -name evaluation -o -name process-log \) | wc -l` returns `9`
    - `find /Users/Zhuanz/aviation-knowledge-base -name .gitkeep | wc -l` returns at least `21`
    - `test -d /Users/Zhuanz/aviation-knowledge-base/instances/_pending` exit 0 (P2 quarantine zone exists)
    - `test -d /Users/Zhuanz/aviation-knowledge-base/scripts/exporters` exit 0 (Task 3 will populate)
    - `test -d /Users/Zhuanz/aviation-knowledge-base/ontology/mappings` exit 0 (S1000D / ATA placeholder home per SUMMARY decision #6)
    - No files yet under `.github/` (Plan 04's territory) and no `README.md` yet (Plan 02's territory)
  </acceptance_criteria>
  <done>9 top-level directories exist, all empty subdirs carry `.gitkeep`, layout matches ARCHITECTURE.md tree exactly.</done>
</task>

<task type="auto">
  <name>Task 2: Write .gitignore and .gitattributes (Git LFS for binaries)</name>
  <files>.gitignore, .gitattributes</files>
  <read_first>
    - .planning/research/PITFALLS.md (Performance Traps row "Git 仓库塞满 PDF 不开 LFS" — lines around 440; Integration Gotchas row "Git LFS 决策" — line ~428)
    - CLAUDE.md (top-level project conventions, "Auditability: Git is truth")
  </read_first>
  <action>
From repo root, write `.gitignore` with this exact content (covers Python venvs, Node, OS junk, secrets, editor files):

```
# === Python ===
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
env/
.env
.env.*
!.env.example
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# === Node ===
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# === Secrets / credentials (NEVER commit) ===
*.key
*.pem
*.p12
*.pfx
secrets/
*.secret
.env.local
.env.production

# === Build / dist ===
dist/
build/
out/
.cache/

# === OS ===
.DS_Store
Thumbs.db
desktop.ini

# === Editors ===
.vscode/
!.vscode/settings.json.example
.idea/
*.swp
*.swo
*~

# === Logs ===
*.log
logs/

# === pre-commit local cache ===
.pre-commit-trash/

# === RAGFlow / Wiki.js local data (if anyone runs local services in dev — not v1) ===
deploy/data/
deploy/volumes/
```

Then write `.gitattributes` with this exact content (Git LFS for aviation binary doc types per REPO-02 + SUMMARY anti-pattern "raw PDF in repo without LFS"):

```
# === Git LFS for binary source documents ===
# Per REPO-02: configured BEFORE any source document is committed.
# Aviation source materials are typically PDF (regs, papers, accident reports),
# DOCX (vendor manuals), XLSX (test matrices, MMEL spreadsheets),
# PPTX (training slides, conference decks). Anything binary that is NOT
# code or YAML/JSON/Markdown belongs in LFS.

*.pdf  filter=lfs diff=lfs merge=lfs -text
*.docx filter=lfs diff=lfs merge=lfs -text
*.xlsx filter=lfs diff=lfs merge=lfs -text
*.pptx filter=lfs diff=lfs merge=lfs -text

# Common adjacent binaries (preempt future drift)
*.zip  filter=lfs diff=lfs merge=lfs -text
*.tar.gz filter=lfs diff=lfs merge=lfs -text
*.png  filter=lfs diff=lfs merge=lfs -text
*.jpg  filter=lfs diff=lfs merge=lfs -text
*.jpeg filter=lfs diff=lfs merge=lfs -text

# === Line endings: enforce LF for text files (cross-platform safety) ===
*.md   text eol=lf
*.yaml text eol=lf
*.yml  text eol=lf
*.json text eol=lf
*.py   text eol=lf

# === Markers ===
# .gitkeep files are empty placeholders; treat as text.
.gitkeep text
```

After writing both files, verify Git LFS is installed locally:
```bash
git lfs version 2>&1 | head -1
```
If `git lfs` is NOT installed, do NOT fail the task — just emit a clear warning in your task summary stating the user must run `brew install git-lfs && git lfs install` BEFORE the first PDF is added (this is a v1 setup note, not a hard blocker for this skeleton plan since no PDFs are being added in Phase 1).
  </action>
  <verify>
    <automated>cd /Users/Zhuanz/aviation-knowledge-base &amp;&amp; grep -q "^\\*\\.pdf filter=lfs" .gitattributes &amp;&amp; grep -q "^\\*\\.docx filter=lfs" .gitattributes &amp;&amp; grep -q "^\\*\\.xlsx filter=lfs" .gitattributes &amp;&amp; grep -q "^\\*\\.pptx filter=lfs" .gitattributes &amp;&amp; grep -q "^\\.env$" .gitignore &amp;&amp; grep -q "^node_modules/$" .gitignore &amp;&amp; grep -q "^__pycache__/$" .gitignore &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - `cat /Users/Zhuanz/aviation-knowledge-base/.gitattributes | grep -E "^\*\.(pdf|docx|xlsx|pptx) filter=lfs" | wc -l` returns at least `4`
    - `cat /Users/Zhuanz/aviation-knowledge-base/.gitignore | grep -E "^(\.env|node_modules/|__pycache__/|\*\.key)" | wc -l` returns at least `4`
    - `.gitignore` contains `!.env.example` (allow committing example, never the real one)
    - `.gitattributes` includes `*.zip` and `*.png` LFS rules (preempt future binary drift per Integration Gotchas table)
    - File `/Users/Zhuanz/aviation-knowledge-base/.env` does NOT exist (we MUST not commit one)
  </acceptance_criteria>
  <done>`.gitignore` and `.gitattributes` written; LFS configured for the 4 mandated binary types plus reasonable extras; secrets cannot leak via env files.</done>
</task>

<task type="auto">
  <name>Task 3: Drop exporter stub files signaling future migration hooks</name>
  <files>
    scripts/exporters/to_ragflow.py,
    scripts/exporters/to_rdf.py,
    scripts/exporters/to_neo4j.py,
    scripts/exporters/to_jsonl_triples.py
  </files>
  <read_first>
    - .planning/research/ARCHITECTURE.md (Pattern 4: Git-Bridge Sync, lines ~374–393; "Future-Proofing for GraphRAG/Agent/KG" section, lines ~810–826; "Guardrail Against Architectural Drift" rule #3 "all consumers go through scripts/exporters/", line ~826)
    - .planning/research/SUMMARY.md (Pinned decision #7 "Wiki.js + RAGFlow do NOT talk directly — all cross-talk via Git; scripts/exporters/to_ragflow.py watches Git")
  </read_first>
  <action>
Create 4 stub Python files. Each is a placeholder that documents the future contract and raises `NotImplementedError`. Real implementations land in Phase 5 (`to_ragflow.py`) and v2 (`to_rdf.py` / `to_neo4j.py` / `to_jsonl_triples.py`). The point of stubbing them NOW is architectural: future contributors see the migration hooks already exist, so adding a backend = filling in a stub, not refactoring.

Write `scripts/exporters/to_ragflow.py` with EXACTLY this content:

```python
"""
to_ragflow.py — Git → RAGFlow HTTP API exporter (STUB)

Status: STUB — implementation lands in Phase 5 (RAG Pipeline Design).
Architectural role: per .planning/research/ARCHITECTURE.md Pattern 4
("Git-Bridge Sync"), this script is the ONLY path by which knowledge
flows from Git into RAGFlow's vector store. Wiki.js and RAGFlow do
not talk to each other directly — Git is the audit log of every
cross-system message.

Contract (to be implemented in Phase 5):
- Watches/polls the Git repo for changes under `wiki/**.md` and
  `docs/**/processed.md`.
- Pushes new/changed Markdown to RAGFlow via its HTTP API
  (https://ragflow.io/docs/http_api_reference).
- Idempotent: uses content hash as the RAGFlow document_id, so
  re-uploading an unchanged file is a no-op.
- Supports `--rebuild` flag: drops RAGFlow's vector store and re-indexes
  everything from current Git HEAD. RAGFlow's vector store is declared
  rebuildable from Git in ARCHITECTURE.md ("Failure Modes & Recovery").

Inputs:
- env: RAGFLOW_API_BASE, RAGFLOW_API_TOKEN
- args: --rebuild, --dry-run, --since=<git-ref>

Outputs:
- stdout: JSON-Lines log of {file, action, ragflow_doc_id, status}
- exit 0 on success, non-zero on any upload failure

AI handoff note (per R12 / AIH-01): Future implementer should consult
.planning/research/ARCHITECTURE.md "Git Repo → RAGFlow" boundary table
for property-by-property contract. Do NOT index raw YAML from
`instances/` in v1 — short structured records embed poorly; use
narrative content (`wiki/**.md`, `docs/**/processed.md`) only.
"""
from __future__ import annotations


def main() -> int:
    raise NotImplementedError(
        "to_ragflow.py is a Phase-1 stub. Implementation lands in Phase 5 "
        "(RAG Pipeline Design). See module docstring for the contract."
    )


if __name__ == "__main__":
    raise SystemExit(main())
```

Write `scripts/exporters/to_rdf.py` with EXACTLY this content:

```python
"""
to_rdf.py — YAML instances → RDF/Turtle exporter (STUB)

Status: STUB — implementation deferred to v2 (GraphRAG / KG layer).
Architectural role: maps each YAML entity/relation file to RDF triples.
Listed in v1 PROJECT.md "Out of Scope" but the stub exists per
ARCHITECTURE.md "Future-Proofing for GraphRAG" hooks: presence of this
file signals to future contributors that URI scheme (`aviationkb://<type>/<slug>@<version>`)
and stable IDs were designed in v1 specifically to make this exporter
trivial later.

Contract (to be implemented in v2):
- Reads `instances/entities/<type>/<id>.yaml` and `instances/relations/<id>.yaml`
- Emits Turtle (.ttl) using URIs derived from the v1 ID scheme.
  - Entity URI: `https://akb.example.org/<type>/<slug>` (or aviationkb://...)
  - Predicate URI: namespaced under aviationkb relation vocabulary
  - Provenance: PROV-O (W3C PROV ontology) — provenance fields map directly.
- Output: single .ttl file or per-entity files, configurable.

AI handoff note: format choice (RDF/Turtle vs JSON-LD vs JSONL `{s,p,o,prov}`)
is OPEN in Phase 2 ADR (see .planning/research/SUMMARY.md open question #4).
This stub assumes Turtle; revisit if Phase 2 ADR picks a different format.
"""
from __future__ import annotations


def main() -> int:
    raise NotImplementedError(
        "to_rdf.py is a Phase-1 stub. Implementation deferred to v2 "
        "(GraphRAG / KG layer). See module docstring for the contract."
    )


if __name__ == "__main__":
    raise SystemExit(main())
```

Write `scripts/exporters/to_neo4j.py` with EXACTLY this content:

```python
"""
to_neo4j.py — YAML instances → Neo4j Cypher loader (STUB)

Status: STUB — implementation deferred to v2 (Graph DB backend).
Architectural role: writes Cypher CREATE/MERGE statements (or uses
the neo4j Python driver) to load YAML records into a graph DB.

Contract (to be implemented in v2):
- Each YAML entity → one Neo4j node, label = entity type, properties = YAML fields.
- Each YAML relation file → one Neo4j relationship, type = predicate,
  properties = relation metadata (provenance, confidence, validity).
- Idempotent: uses MERGE on the entity ID (not CREATE).

Architectural intent (per ARCHITECTURE.md Anti-Pattern 1): relations are
ALWAYS separate YAML files, never inline fields on entities. This is
exactly so that `to_neo4j.py` can map them to native Neo4j relationships
without a refactor. Don't violate this in v1 entity schemas.

AI handoff note: defer until v2 trigger fires. Triggers are documented
in .planning/ROADMAP_FUTURE.md (created in Phase 6).
"""
from __future__ import annotations


def main() -> int:
    raise NotImplementedError(
        "to_neo4j.py is a Phase-1 stub. Implementation deferred to v2 "
        "(Graph DB backend). See module docstring for the contract."
    )


if __name__ == "__main__":
    raise SystemExit(main())
```

Write `scripts/exporters/to_jsonl_triples.py` with EXACTLY this content:

```python
"""
to_jsonl_triples.py — YAML instances → JSONL `{s, p, o, prov}` triples (STUB)

Status: STUB — implementation deferred to v2.
Architectural role: simplest possible triple-export format — one JSON
object per line, fields {subject, predicate, object, provenance}. Useful
as a lightweight intermediate format for ad-hoc analysis or as input to
a graph-loader script that doesn't want to parse RDF/Turtle.

Contract (to be implemented in v2):
- For each entity record:
    {"s": "<entity_id>", "p": "rdf:type", "o": "<entity_type>", "prov": {...}}
    plus one triple per scalar field of the entity.
- For each relation file:
    {"s": "<subject_id>", "p": "<predicate>", "o": "<object_id>", "prov": {...}}

AI handoff note: per .planning/research/SUMMARY.md open question #4,
JSONL is the recommended default for v2 simplicity. If Phase 2 ADR
picks RDF/Turtle as the canonical export instead, this script can stay
as the "lightweight peer" of `to_rdf.py`.
"""
from __future__ import annotations


def main() -> int:
    raise NotImplementedError(
        "to_jsonl_triples.py is a Phase-1 stub. Implementation deferred to v2. "
        "See module docstring for the contract."
    )


if __name__ == "__main__":
    raise SystemExit(main())
```

After writing all 4 files, sanity-check that they are syntactically valid Python (no import-level execution should happen — just module load):

```bash
cd /Users/Zhuanz/aviation-knowledge-base
for f in scripts/exporters/to_ragflow.py scripts/exporters/to_rdf.py scripts/exporters/to_neo4j.py scripts/exporters/to_jsonl_triples.py; do
  python3 -c "import ast; ast.parse(open('$f').read()); print('OK $f')"
done
```
  </action>
  <verify>
    <automated>cd /Users/Zhuanz/aviation-knowledge-base &amp;&amp; for f in scripts/exporters/to_ragflow.py scripts/exporters/to_rdf.py scripts/exporters/to_neo4j.py scripts/exporters/to_jsonl_triples.py; do test -f "$f" || { echo "MISSING $f"; exit 1; }; python3 -c "import ast; ast.parse(open('$f').read())" || { echo "PARSE FAIL $f"; exit 1; }; grep -q "NotImplementedError" "$f" || { echo "NO STUB GUARD $f"; exit 1; }; done &amp;&amp; echo OK</automated>
  </verify>
  <acceptance_criteria>
    - All 4 stub files exist under `scripts/exporters/`
    - Each parses with `python3 -c "import ast; ast.parse(open(F).read())"` exit 0
    - Each contains the literal string `NotImplementedError` (proving the stub guard is present)
    - Each contains an "AI handoff note" line in its docstring (per R12 discipline starting day 1)
    - `to_ragflow.py` docstring mentions Phase 5; `to_rdf.py` / `to_neo4j.py` / `to_jsonl_triples.py` docstrings mention v2
    - No `scripts/exporters/.gitkeep` exists (the .py files themselves keep the dir non-empty)
  </acceptance_criteria>
  <done>4 exporter stubs in place; future contributors see migration hooks immediately when scanning the repo; architectural guardrail #3 from ARCHITECTURE.md is observable.</done>
</task>

</tasks>

<verification>
Phase-1 Plan-01 is complete when:
- [ ] `tree -L 2 -d /Users/Zhuanz/aviation-knowledge-base | head -40` shows 9 top-level directories matching ARCHITECTURE.md
- [ ] `cat .gitattributes` contains LFS rules for `*.pdf`, `*.docx`, `*.xlsx`, `*.pptx`
- [ ] `cat .gitignore` excludes `.env`, `node_modules/`, `__pycache__/`, `*.key`
- [ ] `ls scripts/exporters/` shows 4 `.py` stub files
- [ ] `python3 -c "import ast; [ast.parse(open(f).read()) for f in ['scripts/exporters/to_ragflow.py','scripts/exporters/to_rdf.py','scripts/exporters/to_neo4j.py','scripts/exporters/to_jsonl_triples.py']]"` exit 0
- [ ] No accidental files created under `.planning/`, `.github/`, or top-level `README.md`
</verification>

<success_criteria>
- Repo skeleton is the canonical layout for the entire 6-phase build (REPO-01)
- Git LFS configured BEFORE any binary doc lands, eliminating Performance-Trap "Git 仓库塞满 PDF" risk (REPO-02)
- Exporter stubs make the "all consumers via scripts/exporters/" architectural guardrail visible from day 1 (ARCHITECTURE.md guardrail #3)
- AI接力开发指南 discipline starts in stub docstrings (every stub references the relevant ARCHITECTURE.md / SUMMARY decision)
</success_criteria>

<output>
After completion, create `.planning/phases/01-repo-skeleton-git-baseline-prd-v0/01-01-SUMMARY.md` documenting:
- Directory tree before/after
- LFS rules added
- Stub files created and their architectural role
- Any deviation from the plan (none expected — all paths are concrete)
</output>
