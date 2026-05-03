# Backup & Restore (DEP-06)

> **AI 接力开发指南** — 本文是 v1 单机部署的**备份/恢复唯一契约**。核心信条："Git holds the truth; everything else is rebuildable." 任何接手 ops 的工程师/AI 应先读本文，确认理解"truth vs derivative"边界，再设计备份脚本或灾难恢复流程。

---

## TL;DR

- **Truth** (must back up): Git remote (push it) + Postgres (pg_dump it).
- **Derivative** (do NOT back up — rebuild from truth): RAGFlow Elasticsearch indexes, RAGFlow MinIO chunk blobs.
- **Rebuild path**: `git clone` → restore Postgres dump → `python scripts/exporters/to_ragflow.py --rebuild` → smoke test.

---

## Backup matrix

| Asset | Where it lives | Backup method | Restore-from-zero method | Frequency |
| --- | --- | --- | --- | --- |
| Ontology + instances + docs metadata + design docs | Git (truth) | `git push` to remote | `git clone` | Per commit |
| Wiki.js page content | Postgres (cache) AND Git (`wiki/` via Wiki.js Git Storage module) | `pg_dump` + Wiki.js Git push | Restore Postgres dump OR re-pull from Git via Wiki.js Git Storage | Nightly pg_dump; per-edit Git push |
| Wiki.js users / config | Postgres only | `pg_dump` | Restore from dump | Nightly |
| Source documents (PDFs, DOCX) | Git LFS (`docs/`) AND MinIO (RAGFlow originals) | `git push` (LFS) — MinIO is derivative | `git lfs pull` repopulates `docs/`; MinIO repopulates from `to_ragflow.py --rebuild` | Per commit |
| RAGFlow vector store (Elasticsearch indexes) | Elasticsearch volume | **NOT backed up** — REBUILDABLE from Git via `to_ragflow.py --rebuild` | Re-run ingestion | N/A |
| RAGFlow MinIO blobs (parsed chunks) | MinIO volume | **NOT backed up** — REBUILDABLE | Re-run ingestion | N/A |
| RAGFlow Postgres (citation metadata) | Postgres (separate DB or schema) | Optional `pg_dump` | Restore OR rebuild from Git | Optional nightly |

---

## Truth backup runbook (the only thing that MUST run)

### Daily

```bash
# 1. Postgres dump (Wiki.js page content + users + config)
pg_dump -h localhost -U "${WIKI_DB_USER}" "${WIKI_DB_NAME}" \
  > "backups/wiki_$(date +%F).sql"

# 2. Push truth to Git remote (assumes pre-commit / CI guarded)
git -C /path/to/aviation-knowledge-base push origin main
```

### Weekly

```bash
# 3. Off-host backup of the SQL dumps directory
rsync -avz backups/ user@offhost-backup:/srv/akb-backups/
# OR push to S3:
# aws s3 sync backups/ s3://akb-backups/ --storage-class STANDARD_IA
```

That's it. Three commands. Anything more elaborate is over-engineering for v1.

---

## Derivative rebuild runbook (after a worst-case rebuild)

When you've lost the host entirely (disk failure, ransomware, "rm -rf the wrong volume"):

### Step 1: Reclaim truth from Git

```bash
  $ git clone <canonical-repo-url> aviation-knowledge-base
  $ cd aviation-knowledge-base
  $ git lfs pull   # populate docs/ with PDFs/DOCX
```

### Step 2: Bring up Postgres + Wiki.js, restore page DB

```bash
  $ cd deploy
  $ cp docker-compose.yml.draft docker-compose.yml   # promote draft (one-time)
  $ cp .env.example .env && $EDITOR .env             # fill placeholders
  $ docker compose up -d postgres
  # Wait for healthcheck:
  $ until docker compose exec postgres pg_isready -U "${WIKI_DB_USER}"; do sleep 2; done
  # Restore the latest Postgres dump:
  $ docker compose exec -T postgres psql -U "${WIKI_DB_USER}" -d "${WIKI_DB_NAME}" < backups/wiki_<date>.sql
  $ docker compose up -d wiki
```

### Step 3: Bring up RAGFlow stack with empty volumes

```bash
  $ docker compose up -d elasticsearch minio redis ragflow
  # All volumes start empty; this is intentional.
```

### Step 4: Repopulate vector store from Git (the rebuildable step)

```bash
  $ python scripts/exporters/to_ragflow.py --rebuild
  # This re-ingests every canonical entity + every docs/ source PDF
  # into RAGFlow, repopulating MinIO chunk blobs and Elasticsearch indexes.
```

### Step 5: Smoke test

```bash
# Query a known fixture and verify citation resolves to the expected document.
# (Concrete script TBD in promotion phase; minimum: hit RAGFlow API with a
# canned query, assert ≥1 citation returned, assert citation.document_id
# matches a known canonical entity.)
```

If any step fails, the **truth backup is intact** — you can retry without data loss.

---

## Why the vector store is rebuildable, not backup-worthy

Three reasons, each independently sufficient:

1. **Cost asymmetry**: Elasticsearch indexes + MinIO chunk blobs can grow into hundreds of GB. Backing them up multiplies storage cost and lengthens restore time. The rebuild via `to_ragflow.py --rebuild` is bounded by ingest throughput (per STACK.md OpenDataLoader benchmarks: ~72 min per 10K pages on CPU).

2. **Version drift risk**: RAGFlow's index schema changes between minor versions. A 6-month-old Elasticsearch backup may not be compatible with the current RAGFlow image. Rebuilding is **always** compatible by definition.

3. **Truth + cache discipline** (PITFALLS.md Pitfall 11; ARCHITECTURE.md §"Storage Layer" key boundary "Git holds the truth"): if we backed up the vector store, we'd be tempted to treat it as truth, which would create a second source of truth — exactly the dual-truth anti-pattern we explicitly avoid.

The vector store is to the canonical YAML what an Elasticsearch search index is to a RDBMS table: derivative, **rebuildable**, never authoritative.

---

## Things this runbook intentionally does not cover

- **Hot standby / HA**: out of v1 scope. Single-host deployment. Add when scale demands.
- **Point-in-time recovery (PITR)**: nightly dumps suffice for v1. PITR with WAL archiving is a Phase 2+ topic.
- **Encrypted backups at rest**: rsync target should already be encrypted (LUKS / S3-SSE). Out of doc scope.
- **Cross-region disaster recovery**: out of v1 scope.

---

## Cross-references

| File | What it provides |
| --- | --- |
| `deploy/topology.md` | Truth vs derivative diagram |
| `deploy/docker-compose.yml.draft` | The compose draft these runbooks promote |
| `.planning/research/ARCHITECTURE.md` | §"Storage Layer" — the "Git holds the truth" principle |
| `.planning/research/PITFALLS.md` | Pitfall 11 (Wiki/RAGFlow truth + cache discipline) |
| `scripts/exporters/to_ragflow.py` | The `--rebuild` flag locked in Phase 5 plan 05-03 |

---

## Open questions (deferred)

- **Off-host destination**: S3 / rsync / NAS / tape — picked per deployer.
- **Retention policy**: how many nightly dumps to keep before pruning? Suggest 14 daily + 8 weekly + 6 monthly, but defer to ops.
- **Backup verification**: nightly dumps should be test-restored monthly to a scratch DB to verify integrity. Not implemented in v1; document the gap.
