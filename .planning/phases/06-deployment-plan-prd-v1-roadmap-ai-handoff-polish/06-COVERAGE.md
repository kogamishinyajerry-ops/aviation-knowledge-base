# 06-COVERAGE.md — Phase 6 REQ-ID Coverage Matrix

**Phase:** 6 (Deployment + PRD v1 + Roadmap + AI Handoff Polish)
**Date:** 2026-05-03
**Status:** Phase 6 complete; 13/13 REQ-IDs covered

> Per ROADMAP.md "Coverage Summary" pattern (Phase 5 plan 05-04 set the
> precedent): every phase produces a COVERAGE.md mapping each REQ-ID assigned
> to the phase to its (a) closing plan, (b) closing task within that plan,
> (c) verification command. Auditing v1.0.0 = running every Verification cell
> from the project root and observing all 13 PASS.

---

## Phase 6 REQ-IDs (13)

| REQ-ID | Plan | Task | Artifact | Verification (run from repo root) | Status |
|--------|------|------|----------|------------------------------------|--------|
| DEP-01 | 06-01 | Task 1 | `deploy/docker-compose.yml.draft` | `grep -q "DRAFT — NOT FOR PRODUCTION" deploy/docker-compose.yml.draft && .venv/bin/python -c "import yaml; yaml.safe_load(open('deploy/docker-compose.yml.draft'))"` | Covered |
| DEP-02 | 06-01 | Task 1 | `deploy/.env.example` | `test "$(grep -c '<CHANGE_ME>' deploy/.env.example)" -ge 5` | Covered |
| DEP-03 | 06-01 | Task 1 | `deploy/topology.md` | `grep -q "Git" deploy/topology.md && grep -q "Wiki.js" deploy/topology.md && grep -q "RAGFlow" deploy/topology.md && grep -q "Caddy" deploy/topology.md` | Covered |
| DEP-04 | 06-01 | Task 2 | `deploy/wiki-git-storage.md` | `grep -q "wiki/ ONLY" deploy/wiki-git-storage.md` | Covered |
| DEP-05 | 06-01 | Task 2 | `deploy/authentik-phase2.md` + commented authentik block in compose | `grep -q "12568" deploy/authentik-phase2.md && grep -qE "^\s*#\s*authentik:" deploy/docker-compose.yml.draft` | Covered |
| DEP-06 | 06-01 | Task 2 | `deploy/backup-restore.md` | `grep -q "rebuildable" deploy/backup-restore.md && grep -q "to_ragflow.py --rebuild" deploy/backup-restore.md` | Covered |
| AIH-04 | 06-02 | Task 1 | `docs/GLOSSARY.md` | `test "$(awk -F'\|' '/^\| [^-]/ && NF>=4 && !/^\| 中文/' docs/GLOSSARY.md \| wc -l)" -ge 50` | Covered |
| AIH-03 | 06-02 (T2) + 06-04 (T2) | various | `process-log/README.md`, `process-log/phase-{1..6}-completion.md` | `for i in 1 2 3 4 5 6; do test -f "process-log/phase-$i-completion.md" \|\| exit 1; done && test -f process-log/README.md` | Covered |
| ROAD-01 | 06-03 | Task 1 | `.planning/ROADMAP_FUTURE.md` | `test "$(grep -cE '^## ' .planning/ROADMAP_FUTURE.md)" -ge 7` | Covered |
| ROAD-02 | 06-03 | Task 1 | `.planning/ROADMAP_FUTURE.md` | `test "$(grep -c 'Promote when' .planning/ROADMAP_FUTURE.md)" -ge 7` | Covered |
| PRD-02 | 06-04 | Task 1 + Task 2 | `.planning/design/PRD_v1.md` + sign-off in `ontology/CHANGELOG.md` | `grep -q "PRD_v1" ontology/CHANGELOG.md && grep -q "AI 接力开发指南" .planning/design/PRD_v1.md` | Covered |
| AIH-01 | 06-05 | Task 1 | every `.planning/design/*.md` has AI 接力 section + GLOSSARY ref + bidirectional PRD_v0/v1 link | `for f in $(find .planning/design -name '*.md' -type f); do grep -q "AI 接力开发指南" "$f" \|\| exit 1; grep -q "GLOSSARY" "$f" \|\| exit 1; done && grep -q "PRD_v1.md" .planning/design/PRD_v0.md && grep -q "PRD_v0.md" .planning/design/PRD_v1.md` | Covered |
| AIH-02 | 06-05 | Task 2 | `.planning/phases/06-*/06-STRANGER-TEST.md` ≥3 docs PASS | `test "$(grep -c '^### Verdict: \*\*PASS' .planning/phases/06-deployment-plan-prd-v1-roadmap-ai-handoff-polish/06-STRANGER-TEST.md)" -ge 3` | Covered |

---

## Verification one-liner (audit script)

To re-run all 13 commands in sequence and confirm Phase 6 is green:

```bash
cd /Users/Zhuanz/aviation-knowledge-base && \
echo "DEP-01" && grep -q "DRAFT — NOT FOR PRODUCTION" deploy/docker-compose.yml.draft && .venv/bin/python -c "import yaml; yaml.safe_load(open('deploy/docker-compose.yml.draft'))" && \
echo "DEP-02" && test "$(grep -c '<CHANGE_ME>' deploy/.env.example)" -ge 5 && \
echo "DEP-03" && grep -q "Git" deploy/topology.md && grep -q "Wiki.js" deploy/topology.md && grep -q "RAGFlow" deploy/topology.md && grep -q "Caddy" deploy/topology.md && \
echo "DEP-04" && grep -q "wiki/ ONLY" deploy/wiki-git-storage.md && \
echo "DEP-05" && grep -q "12568" deploy/authentik-phase2.md && grep -qE "^\s*#\s*authentik:" deploy/docker-compose.yml.draft && \
echo "DEP-06" && grep -q "rebuildable" deploy/backup-restore.md && grep -q "to_ragflow.py --rebuild" deploy/backup-restore.md && \
echo "AIH-04" && test "$(awk -F'|' '/^\| [^-]/ && NF>=4 && !/^\| 中文/' docs/GLOSSARY.md | wc -l)" -ge 50 && \
echo "AIH-03" && for i in 1 2 3 4 5 6; do test -f "process-log/phase-$i-completion.md" || exit 1; done && test -f process-log/README.md && \
echo "ROAD-01" && test "$(grep -cE '^## ' .planning/ROADMAP_FUTURE.md)" -ge 7 && \
echo "ROAD-02" && test "$(grep -c 'Promote when' .planning/ROADMAP_FUTURE.md)" -ge 7 && \
echo "PRD-02" && grep -q "PRD_v1" ontology/CHANGELOG.md && grep -q "AI 接力开发指南" .planning/design/PRD_v1.md && \
echo "AIH-01" && for f in $(find .planning/design -name '*.md' -type f); do grep -q "AI 接力开发指南" "$f" || exit 1; grep -q "GLOSSARY" "$f" || exit 1; done && grep -q "PRD_v1.md" .planning/design/PRD_v0.md && grep -q "PRD_v0.md" .planning/design/PRD_v1.md && \
echo "AIH-02" && test "$(grep -c '^### Verdict: \*\*PASS' .planning/phases/06-deployment-plan-prd-v1-roadmap-ai-handoff-polish/06-STRANGER-TEST.md)" -ge 3 && \
echo "ALL 13 GREEN"
```

Expected output ends with `ALL 13 GREEN`. If any line fails, the script
exits non-zero at the failing REQ — that REQ has regressed and must be
patched before tagging v1.0.0.

---

## v1 release readiness

After Phase 6 closes:

- **94 of 94 v1 REQ-IDs covered** (per `.planning/ROADMAP.md` Coverage Summary;
  Phase 1–5 contribute 81, Phase 6 contributes 13)
- **6 of 6 phases complete** (01-repo-skeleton, 02-ontology, 03-validators,
  04-demo-data, 05-rag-pipeline-design, 06-deployment-plan-prd-v1-roadmap-ai-handoff-polish)
- **v2+ posture**: see `.planning/ROADMAP_FUTURE.md` (≥7 deferred features
  with measurable Promote-when triggers)

---

## Next action — v1.0.0 release tag

The release tag is a manual step OUTSIDE Phase 6 scope; Phase 6 delivers
the artifacts that make tagging meaningful. Once the audit one-liner above
prints `ALL 13 GREEN` (and the equivalent audit scripts for Phases 1–5
also print green):

```bash
cd /Users/Zhuanz/aviation-knowledge-base
git tag -a v1.0.0 -m "Aviation Knowledge Base MVP v1.0.0 — schema + validators + demo data + RAG design + deployment draft + PRD v1 + roadmap + AI handoff polish"
git push origin v1.0.0  # only after user explicit approval per CLAUDE.md
```

The tag is the explicit handoff: everything below the tag is the v1
release surface; everything above is v2+ work driven by
`.planning/ROADMAP_FUTURE.md` triggers.

---

## Cross-references

- Plan: `.planning/phases/06-deployment-plan-prd-v1-roadmap-ai-handoff-polish/06-05-PLAN.md`
- Plan summaries (closing plans for each REQ):
  - `06-01-SUMMARY.md` (DEP-01..06)
  - `06-02-SUMMARY.md` (AIH-04 + AIH-03 part 1)
  - `06-03-SUMMARY.md` (ROAD-01..02)
  - `06-04-SUMMARY.md` (PRD-02 + AIH-03 part 2)
  - `06-05-SUMMARY.md` (AIH-01 + AIH-02 — written after this file)
- Stranger test results: `06-STRANGER-TEST.md` (this directory)
- REQ definitions: `.planning/REQUIREMENTS.md`
- Coverage precedent: `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-COVERAGE.md`
