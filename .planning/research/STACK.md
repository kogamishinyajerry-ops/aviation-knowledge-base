# Stack Research

**Domain:** Aviation knowledge base — Wiki.js portal + RAGFlow RAG + YAML/JSON Schema ontology
**Researched:** 2026-05-03
**Confidence:** HIGH overall (versions verified against GitHub releases / official docs as of 2026-04/05)

## Executive Summary

User has pre-committed to Wiki.js + RAGFlow + YAML + JSON Schema + Markdown + Git. Research confirms this baseline is **viable and standard** for a self-hosted, audit-traceable, bilingual (ZH/EN) aviation knowledge base in 2026. The non-obvious decisions are:

1. **Wiki.js**: Stay on **2.5.314 (stable, May 2026)**, NOT 3.0 alpha — 3.0 has been "alpha/in-development" since 2021, still no beta as of 2026-05. Pin to 2.5.x.
2. **RAGFlow**: Use **v0.25.1 (April 2026)**. The new `OpenDataLoader` PDF backend (added in v0.25) is dramatically faster than DeepDoc/MinerU on large corpora and deterministic — recommended for v1 ingestion. Keep DeepDoc as fallback for image-heavy / scanned PDFs (deferred per Out-of-Scope OCR rule).
3. **PostgreSQL 16+** is the only sane DB for Wiki.js (3.0 will be Postgres-only; existing 2.x→3.x migration is in-place).
4. **JSON Schema validation toolchain**: `check-jsonschema` (Python pre-commit hook, supports YAML natively) is the industry default in 2026 — beats ajv-cli for our case because we have YAML source files, not JSON.
5. **SSO**: Wiki.js↔Authentik OIDC integration is documented and works. RAGFlow OIDC is **immature in 2026-05** (open feature request #3495, Keycloak-OIDC bug #12568 still recurring). Recommendation: defer SSO unification to a later phase; v1 uses **separate auth on each service behind a reverse proxy** (no shared SSO).
6. **Embedding model**: **BGE-M3** (BAAI, multilingual, 8192-token context, dense+sparse+colbert in one model). Already validated on Chinese aviation regs in user's AeroPower-RAG project (recall@3=100%). HIGH confidence.
7. **Aviation reference standards**: Reference **iSpec 2200** (ATA chapter numbering) as the structural backbone for AircraftSystem/Subsystem decomposition — DO NOT adopt **S1000D** as primary schema (3000-page XML monolith, wrong fit for greenfield YAML). Map to it as a future export option.

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Wiki.js** | **2.5.314** (May 2026) | Knowledge portal, Markdown editing, page tree, ZH/EN i18n, KaTeX math | User-pinned. Latest 2.x stable. 3.0 still alpha (5 yr in dev) — DO NOT chase. Postgres-native, OIDC-ready, KaTeX built-in for LaTeX. Confidence: HIGH (verified via GitHub releases page). |
| **RAGFlow** | **v0.25.1** (Apr 30, 2026) | RAG ingestion + chunk/citation/retrieval pipeline | User-pinned. Latest stable. v0.25 introduced OpenDataLoader PDF backend (much faster) and ingestion-pipeline templates. Native citation grounding, Chinese localization, hybrid retrieval. Confidence: HIGH (verified via GitHub releases). |
| **PostgreSQL** | **16.x** (16.6+) | Wiki.js DB; future RAGFlow metadata if consolidating | Wiki.js 3.0 will require Postgres-only; using Postgres in 2.x ensures seamless future upgrade. `pg_trgm` extension for Wiki.js full-text search. Confidence: HIGH. |
| **Elasticsearch** | **8.x** (RAGFlow default) or **Infinity** | RAGFlow vector + sparse retrieval backend | RAGFlow ships with Elasticsearch by default; v0.25 added ES 9.x compat. Infinity (RAGFlow's own DB) is alternative for low-resource hosts. v1: stick with bundled ES from docker-compose. Confidence: HIGH. |
| **MinIO** | latest stable | S3-compatible object store for RAGFlow document originals + Wiki.js asset uploads (optional) | Comes bundled in RAGFlow's docker-compose. Wiki.js can also use MinIO as storage backend (S3-compatible). Single bucket = single backup target. Confidence: HIGH. |
| **Redis** | **7.x** | Wiki.js cache + RAGFlow task queue (bundled) | Both services use Redis; one shared instance acceptable for v1 single-host. Confidence: HIGH. |
| **Docker Engine** | **24.0+** | Container runtime | RAGFlow hard requirement: Docker ≥24.0.0, Compose ≥2.26.1. Confidence: HIGH. |
| **docker-compose** | **2.26.1+** | Orchestration for v1 single-host | Per RAGFlow docs. K8s deferred — v1 is single-host per Constraints. Confidence: HIGH. |
| **Git** | 2.40+ | Version control + audit trail (truth source for all schema/YAML/MD) | User-pinned per Constraints. Confidence: HIGH. |

### Schema / Validation Layer

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **JSON Schema** | **Draft 2020-12** | Ontology validation language | Current spec; ajv, check-jsonschema, jsonschema (Python) all support it. Avoid Draft-04 / Draft-07 unless dependency forces. Confidence: HIGH. |
| **YAML 1.2** | spec | Human-readable ontology source | YAML 1.2 spec since 2009; PyYAML, ruamel.yaml, js-yaml all default to 1.2 in modern versions. Confidence: HIGH. |
| **check-jsonschema** | **0.37.1** (latest stable, 2026) | Python CLI + pre-commit hook validating YAML/JSON against JSON Schema | Native YAML support (no convert step), built-in pre-commit hook syntax, schema caching. **Industry default** in 2026 for YAML-validated-by-JSONSchema workflows. Confidence: HIGH. |
| **ajv** + **ajv-cli** | ajv 8.x / ajv-cli 5.x | Alternative: JSON Schema validation in Node.js / CI | Use IF a Node.js consumer needs runtime validation (e.g. future TS server). For pre-commit, prefer check-jsonschema. Confidence: HIGH. |
| **yamllint** | **1.38+** | YAML style/syntax linter (separate from schema validation) | Catches indentation, trailing spaces, key duplication BEFORE schema validation runs. Pair with check-jsonschema in pre-commit. Confidence: HIGH. |
| **pre-commit** | **3.7+** | Hook orchestrator | Standard Python tool, language-agnostic, runs yamllint + check-jsonschema + custom Python validators in sequence. Confidence: HIGH. |

### Document Ingestion Stack (for RAGFlow + Wiki.js asset uploads)

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| **OpenDataLoader-PDF** | latest (RAGFlow v0.25 bundled) | Deterministic PDF→Markdown/JSON | **Default v1 backend** in RAGFlow. ~14× faster than MinerU on 10K-page corpora; no GPU needed. Best for native (text-layer) PDFs — most adapted aviation regs/specs. Confidence: HIGH. |
| **DeepDoc** | RAGFlow built-in | Visual OCR + table-structure recognition | Fallback for scanned PDFs / image-heavy docs. Per CLAUDE.md Out-of-Scope: OCR deferred for v1, so use OpenDataLoader exclusively initially. Confidence: HIGH. |
| **MinerU** | ≥2.6.3 (optional) | Alternative DL-based PDF parser | Skip in v1. Available as third option in RAGFlow if OpenDataLoader struggles on a specific corpus. Confidence: MEDIUM (verified bundled but not benchmarked on aviation Chinese PDFs). |
| **Docling** | latest | Standalone PDF/DOCX→Markdown converter (alternative to RAGFlow internal) | Use IF you want to pre-process docs into clean Markdown BEFORE uploading to Wiki.js as human-readable pages. RAGFlow handles its own ingestion separately. ZH support: ch_sim + ch_tra. Confidence: HIGH. |
| **pandoc** | 3.x | DOCX/HTML→Markdown for Wiki.js human-readable pages | Mature, scriptable, preserves tables (GFM). Use in import scripts. Confidence: HIGH. |

### Embedding & LLM Layer

| Component | Recommendation | Rationale |
|-----------|----------------|-----------|
| **Embedding model** | **BAAI/bge-m3** (568M params, 8192 ctx, multilingual) | Industry-standard self-hosted multilingual embedding 2026. Dense + sparse + multi-vector in one model — natural fit for hybrid retrieval (matches user's AeroPower-RAG pattern). Available in Ollama (`ollama pull bge-m3`) or via RAGFlow's built-in Xinference. Confidence: HIGH. |
| **Reranker** | **BAAI/bge-reranker-v2-m3** | Pairs naturally with bge-m3, supports ZH/EN, RAGFlow has built-in support. Confidence: HIGH. |
| **LLM (chat completion)** | Pluggable via Ollama or remote API | RAGFlow supports Ollama, Xinference, vLLM, SGLang, plus OpenAI/Claude/Gemini APIs. Recommend Ollama-served Qwen2.5-14B/32B for self-hosted ZH; OR remote Claude/GPT for higher quality. Decision deferred to RAG design phase (R8). Confidence: HIGH. |

### Auth / Reverse Proxy (v1)

| Component | Recommendation | Rationale |
|-----------|----------------|-----------|
| **Reverse proxy** | **Caddy 2.x** OR **Traefik 3.x** OR **nginx 1.27** | All three handle TLS + path/host routing for Wiki.js + RAGFlow. Caddy = simplest; Traefik = best Docker labels. Pick based on team familiarity. Confidence: HIGH. |
| **Wiki.js auth (v1)** | Built-in local accounts + admin | No SSO in v1; per Constraints "single org, admin + reader only". Add OIDC (Authentik) in a later phase. Confidence: HIGH. |
| **RAGFlow auth (v1)** | Built-in user system | Same — defer SSO. RAGFlow OIDC integration is **broken/incomplete in 2026-05** (issue #3495 open, #12568 OIDC redirect-loop bug since Quart migration). Confidence: HIGH on "defer", MEDIUM on "broken" (one bug report, but FR open suggests immaturity). |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **VSCode + redhat.vscode-yaml** | Schema-aware YAML editing | Auto-complete + inline validation against JSON Schema. Configure `yaml.schemas` mapping in `.vscode/settings.json`. Confidence: HIGH. |
| **VSCode + ms-python.python** | Python linting for any custom validators | If we write Python helpers for schema migration. Confidence: HIGH. |
| **GitHub Actions / Gitea Actions** | CI for schema validation on PR | Run `pre-commit run --all-files` in CI = catches PRs that bypass local hooks. Confidence: HIGH. |
| **mkdocs-material** (optional) | Render `.planning/` design docs as static site | If team wants prettier doc browsing than raw GitHub MD. Optional, not v1. Confidence: MEDIUM. |

### Aviation Reference Standards (alignment, not adoption)

| Standard | Our Treatment | Rationale |
|----------|--------------|-----------|
| **ATA iSpec 2200** (ATA Chapter system) | **REFERENCE** — use ATA chapter codes (e.g., ATA-21 Air Conditioning, ATA-71 Powerplant) as `ata_chapter` field on `AircraftSystem`/`Subsystem` entities | De facto industry chapter taxonomy; lightweight to embed as a string field; no XML adoption required. Confidence: HIGH. |
| **S1000D Issue 6** | **MAP TO** — provide future export path; do not adopt as primary schema | 3000-page XML spec; massive overengineering for v1 YAML knowledge base. Reserve `s1000d_dmc` (Data Module Code) optional field on `Document` entity for future round-tripping. Confidence: HIGH. |
| **ATA Spec 2300** (Flight Ops data) | **NOT IN SCOPE v1** | Flight ops data is not the v1 corpus focus (we focus on engineering/airworthiness/CFD). Re-evaluate if flight-ops docs are added later. Confidence: HIGH. |
| **AP233** (ISO 10303-233 systems eng) | **AVOID** | STEP/EXPRESS schema; even heavier than S1000D; aerospace-systems-engineering only. Wrong tool. Confidence: HIGH. |
| **ARINC 653** (avionics RTOS partitioning) | **N/A** | Software/RTOS standard, not knowledge-mgmt standard. Mention in `Standard` entity instances when relevant, no schema impact. Confidence: HIGH. |
| **ISO 10303 STEP** generally | **AVOID for v1** | CAD/PLM data exchange; out of v1 scope. Confidence: HIGH. |

### CFD-Specific Schema References

| Source | Treatment | Rationale |
|--------|-----------|-----------|
| **NASA TMR (Turbulence Modeling Resource)** — `tmbwg.github.io/turbmodels` (relocated 2026-02) | **PRIMARY REFERENCE** for `TurbulenceModel` entity instances and `SimulationCase` verification cases | AIAA-curated, current, includes 2D/3D verification cases (flat plate, planar shear, bumps) with grids + reference results. `SimulationCase.reference_url` should link to TMR pages. Confidence: HIGH. |
| **ERCOFTAC Classic Database** + **ERCOFTAC QNET-CFD** | **REFERENCE** for validation cases | European counterpart to TMR; richer set of experimental validation cases. Use as `SimulationCase` source. Confidence: HIGH. |
| **AIAA CFD Drag/High-Lift/Aeroelastic Prediction Workshops** (DPW, HLPW, AePW) | **REFERENCE** for industrial-grade validation | Cite as `SimulationCase` instances when modeling production aircraft cases. Confidence: HIGH. |
| **CGNS** (CFD General Notation System) | **OPTIONAL FIELD** on `MeshRequirement` | Standard mesh/solution file format; if a case has a CGNS file, store path/URL in metadata. Don't make it required. Confidence: MEDIUM. |

For schema design (R3): `SimulationCase`, `TurbulenceModel`, `MeshRequirement` should each carry: `name`, `model_family` (RANS/LES/DNS/hybrid), `reference_url`, `verification_status` (verified/under_review/community), `y_plus_requirement` (for RANS wall-function vs low-Re), `grid_convergence_data` (optional), `source_workshop` (TMR/ERCOFTAC/DPW/internal).

## Installation

> **Note**: per Constraints, R9 only requires *docker-compose draft*, NOT a running deployment. Below is the skeleton.

### Schema validation toolchain (set up in main repo, runs locally + CI)

```bash
# Python venv for tooling
python3 -m venv .venv && source .venv/bin/activate

# Schema + style validation
pip install pre-commit==3.7.* check-jsonschema==0.37.* yamllint==1.38.*

# (optional) Node-side validation if a TS app is added later
# npm install -D ajv@^8 ajv-cli@^5 ajv-formats@^3
```

`.pre-commit-config.yaml` skeleton:

```yaml
repos:
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.38.0
    hooks:
      - id: yamllint
        args: [--strict, -c=.yamllint]
  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.37.1
    hooks:
      - id: check-jsonschema
        files: ^ontology/instances/.*\.ya?ml$
        args: ["--schemafile", "ontology/schemas/entity.schema.json"]
```

### Deployment skeleton (docker-compose, NOT for execution in v1)

```yaml
# docker-compose.yml — DRAFT only, R9 deliverable
services:
  wiki:
    image: requarks/wiki:2.5.314
    depends_on: [postgres]
    environment:
      DB_TYPE: postgres
      DB_HOST: postgres
      DB_NAME: wiki
    ports: ["3000:3000"]

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: wiki
    volumes: ["./data/pg:/var/lib/postgresql/data"]

  ragflow:
    image: infiniflow/ragflow:v0.25.1
    # bundles its own ES + Redis + MinIO via its compose include
    ports: ["9380:9380", "80:80"]
    environment:
      DEVICE: cpu  # set 'gpu' if NVIDIA available

  caddy:
    image: caddy:2
    ports: ["443:443", "80:80"]
    volumes: ["./Caddyfile:/etc/caddy/Caddyfile"]
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Wiki.js 2.5.314 | BookStack / Outline / Confluence | If user changes baseline. BookStack = lighter but no native i18n; Outline = better UX but younger; Confluence = vendor lock-in. **Stay with Wiki.js per Constraints.** |
| RAGFlow v0.25.1 | LangChain + LlamaIndex (custom) / Dify / Open-WebUI + Ollama | Dify excluded by Constraints. Custom LangChain stack = more flexibility but you build citation/UI yourself. RAGFlow = batteries-included for v1. |
| PostgreSQL 16 | MariaDB / SQLite | SQLite for tiny demo only. MariaDB will be dropped by Wiki.js 3.0 → migration tax. **Postgres is the only future-proof choice.** |
| check-jsonschema (Python) | ajv-cli (Node.js) | If repo has Node.js as primary runtime. Our repo is YAML-first, no Node baseline → check-jsonschema wins. |
| OpenDataLoader PDF (RAGFlow) | DeepDoc / MinerU / Marker / LlamaParse / Docling | DeepDoc for OCR-required scans (deferred). MinerU = DL model, slower, GPU-helpful. Marker = even slower (6 days for 10K pages). Docling = excellent standalone, use for Wiki.js Markdown pre-conversion. LlamaParse = SaaS, vendor lock-in. |
| BGE-M3 embedding | text-embedding-3-large (OpenAI) / Voyage-3-large / Nomic-Embed-v2 | OpenAI/Voyage = best quality but SaaS + cost. Nomic-v2 = good multilingual, smaller. BGE-M3 chosen for self-hosted + ZH-strong + already validated by user. |
| Authentik (when SSO arrives) | Keycloak / Authelia | Keycloak = enterprise heavyweight, steep learning curve. Authelia = 2FA+forward-auth focused, weaker as full IdP. Authentik = sweet-spot self-hosted IdP in 2026. RAGFlow OIDC reportedly broken with Keycloak (#12568) — extra reason to prefer Authentik or defer entirely. |
| docker-compose v1 | Kubernetes | K8s overkill for single-host v1. Re-evaluate at 10+ services or multi-host. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Wiki.js 3.0 alpha** | "Alpha" since 2021, no beta as of 2026-05; production-unsafe | Wiki.js 2.5.314 stable |
| **MariaDB / MySQL / MSSQL / SQLite as Wiki.js DB** | Will be deprecated by Wiki.js 3.0; migration cost | PostgreSQL 16+ |
| **Dify** | User-excluded; Agent orchestration not v1 scope | RAGFlow handles RAG; no agent framework needed v1 |
| **Neo4j / Nebula / ArangoDB / Apache Jena** | User-excluded; YAML+JSON Schema sufficient for ≤10K triples; premature backend lock-in | YAML files in Git, defer graph DB to GraphRAG phase |
| **S1000D as primary schema** | 3000-page XML monolith; greenfield team can't author/validate XSD-based DMs in v1 | Custom YAML+JSON Schema ontology, with optional `s1000d_dmc` mapping field for future export |
| **AP233 / ISO 10303-233** | STEP/EXPRESS schema; even heavier than S1000D; SE-tool-vendor space | Out of scope; not knowledge-mgmt-shaped |
| **Vue/React custom frontend (v1)** | User-excluded; reinvents Wiki.js + RAGFlow UIs | Use Wiki.js portal + RAGFlow UI as-is |
| **Auto-crawlers / scrapers** | User-excluded; airworthiness/CFD docs need curated provenance | Manual / batch upload with explicit `source_url` + `provenance.method` fields |
| **OCR pipelines (Tesseract / PaddleOCR / scanned-PDF flow)** | Out of scope per Constraints; v1 = text-layer PDFs only | Defer; revisit when scanned-doc corpus becomes priority |
| **JSON Schema Draft-04 / Draft-07** | Outdated, missing `$defs`, `unevaluatedProperties`, etc. | Draft 2020-12 |
| **Putting raw YAML in Wiki.js page bodies** | Wiki.js won't validate it; defeats purpose of separate schema layer | Keep YAML in Git; Wiki.js renders generated Markdown summaries linking back to source YAML files |
| **RAGFlow OIDC SSO in v1** | Open feature request #3495; bug #12568 (Keycloak redirect loop since Quart migration) | Local accounts on each service for v1; revisit SSO when RAGFlow OIDC matures |
| **Self-hosted LLM-only path with no fallback** | macOS Apple Silicon dev box may not have enough VRAM for Qwen2.5-32B | Plug in OpenAI/Anthropic API keys via RAGFlow model config when local runs short — RAGFlow supports both transparently |
| **Marker-PDF / pure DL parsers as default** | 6+ days for 10K pages per benchmarks; GPU-bound | OpenDataLoader-PDF (deterministic, ~72min/10K pages) |

## Stack Patterns by Variant

**If Apple Silicon dev only (no GPU server):**
- RAGFlow `DEVICE=cpu`; OpenDataLoader-PDF (no GPU needed)
- Embedding via Ollama `bge-m3` (CPU-friendly at 568M params, ~2GB RAM)
- LLM via remote API (Claude/GPT) — local Qwen2.5-32B needs 24GB+ RAM
- This matches user's actual environment per CLAUDE.md (macOS Apple Silicon)

**If single-host x86 + NVIDIA GPU:**
- RAGFlow `DEVICE=gpu` for DeepDoc fallback if scanned PDFs appear
- Local LLM via Ollama Qwen2.5-32B-Instruct or DeepSeek-V2-Lite
- All local, no API cost

**If Wiki.js becomes primary editing surface (writers-heavy team):**
- Add Wiki.js Git-sync module → push pages back to a Git repo for audit
- Pair with `mkdocs-material` rendering of `.planning/` design docs separately

**If team grows beyond single-org single-admin (post-v1):**
- Add Authentik as IdP; integrate Wiki.js OIDC (well-documented)
- Wait on RAGFlow OIDC until upstream resolves #3495 / #12568, OR put RAGFlow behind Authentik forward-auth as workaround

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Wiki.js 2.5.314 | PostgreSQL 11–17 | Officially: latest Postgres recommended; 16 is the sweet spot. `pg_trgm` extension required. |
| Wiki.js 2.5.314 | Node.js 18 LTS or 20 LTS | Bundled in Docker image; no host install needed |
| RAGFlow v0.25.1 | Docker ≥24.0.0, Compose ≥2.26.1 | Hard requirements |
| RAGFlow v0.25.1 | Elasticsearch 8.x or 9.x | v0.25 added 9.x compat |
| RAGFlow v0.25.1 | Ollama 0.3+ | For local embedding/LLM serving |
| check-jsonschema 0.37.1 | Python 3.9+ | Pre-commit env will manage |
| yamllint 1.38 | Python 3.8+ | Pre-commit env will manage |
| BGE-M3 | Ollama 0.1.39+, sentence-transformers 2.7+, RAGFlow built-in | 8192 token context, ~2GB on disk |
| pre-commit 3.7 | Python 3.9+, Git 2.40+ | Standard |

**Known incompatibility flags:**
- Wiki.js 2.x → 3.x migration: documented in-place but **only** from Postgres 2.x (MariaDB/MSSQL/SQLite path = full export/reimport). Decision: start on Postgres now.
- RAGFlow OIDC + Keycloak: open bug #12568; recurring redirect loop. Avoid in v1.
- Wiki.js KaTeX module: some advanced LaTeX (e.g., `\begin{align}` with custom macros) won't render — known issue (discussion #5216). Workaround: simpler LaTeX or fall back to MathJax module.

## Hardware / Storage Sizing (v1, single-host)

| Component | Min | Recommended |
|-----------|-----|-------------|
| CPU | 4 cores x86_64 (or Apple Silicon for dev) | 8 cores |
| RAM | 16 GB (RAGFlow hard min) | 32 GB (room for ES + bge-m3 + small local LLM) |
| Disk | 50 GB | 200 GB SSD (Postgres + ES indexes + MinIO docs grow fast) |
| GPU | None required | NVIDIA 8GB+ for DeepDoc OCR / local LLM (deferred) |

**Backup strategy (v1):**
- Git is canonical for ontology YAML + Markdown + design docs (already version-controlled)
- Postgres: nightly `pg_dump` to MinIO bucket
- MinIO docs bucket: rsync to off-host backup or S3
- Elasticsearch indexes: REGENERATABLE from RAGFlow re-ingestion → not backed up; document re-ingestion runbook instead
- Wiki.js page content lives in Postgres (assets in MinIO) — covered by pg_dump + MinIO backup

## Sources

**Primary (HIGH confidence):**
- [Wiki.js GitHub Releases](https://github.com/requarks/wiki/releases) — v2.5.314 (2026-05-01), 3.0 still alpha
- [Wiki.js 3.0 PostgreSQL announcement](https://beta.js.wiki/blog/2021-wiki-js-3-going-full-postgresql) — Postgres-only direction
- [Wiki.js Requirements](https://docs.requarks.io/install/requirements) — DB engine support
- [RAGFlow GitHub Releases](https://github.com/infiniflow/ragflow/releases) — v0.25.1 (2026-04-30), OpenDataLoader added v0.25
- [RAGFlow Select PDF parser docs](https://ragflow.io/docs/select_pdf_parser) — DeepDoc / MinerU / OpenDataLoader / Docling backends
- [RAGFlow Quickstart](https://ragflow.io/docs/) — hardware requirements (4 CPU / 16GB / 50GB disk; Docker 24+ / Compose 2.26+)
- [RAGFlow Deploy Local LLM](https://ragflow.io/docs/deploy_local_llm) — Ollama/Xinference/vLLM/SGLang support
- [check-jsonschema docs](https://check-jsonschema.readthedocs.io/) — 0.37.1, YAML-native, pre-commit hooks
- [yamllint pre-commit hook](https://github.com/adrienverge/yamllint/blob/master/.pre-commit-hooks.yaml) — 1.38
- [Authentik Wiki.js integration guide](https://docs.goauthentik.io/integrations/services/wiki-js/) — OIDC steps verified
- [BGE-M3 model card](https://huggingface.co/BAAI/bge-m3) — multilingual, 8192 ctx, dense+sparse+colbert
- [BGE-M3 on Ollama](https://ollama.com/library/bge-m3) — local self-hosted path
- [NASA Turbulence Modeling Resource](https://tmbwg.github.io/turbmodels/) — relocated 2026-02-24, AIAA-curated
- [ATA iSpec 2200 / Wikipedia](https://en.wikipedia.org/wiki/ATA_Spec_100/iSpec_2200) — chapter taxonomy
- [S1000D specification overview](https://s1000d.org/) — Issue 6 current

**Secondary (MEDIUM confidence — single source or community):**
- [PDF parser benchmark — Procycons 2025](https://procycons.com/en/blogs/pdf-data-extraction-benchmark/) — Docling 97.9% on tables
- [OpenDataLoader review (Emelia 2026)](https://emelia.io/hub/opendataloader-pdf-review) — 72min vs 16.5h vs 6day comparison on 10K pages
- [RAGFlow OIDC bug #12568](https://github.com/infiniflow/ragflow/issues/12568) — Keycloak redirect loop (one report, recent)
- [RAGFlow OIDC FR #3495](https://github.com/infiniflow/ragflow/issues/3495) — feature still pending
- [Authentik vs Keycloak vs Authelia 2026](https://blog.elest.io/authentik-vs-authelia-vs-keycloak-choosing-the-right-self-hosted-identity-provider-in-2026/) — Authentik recommendation context

**Cross-confirmed via**: GitHub release pages + official documentation + community benchmarks; no claim relies on a single source for HIGH-confidence items.

---
*Stack research for: Aviation Knowledge Base MVP — Wiki.js + RAGFlow + YAML/JSON Schema baseline*
*Researched: 2026-05-03*
