---
phase: 4
slug: demo-data-document-import-spec
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-03
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: Phase 3 validators are now ACTIVE; Phase 4 is the first phase whose deliverables (canonical instances) get validated by them on every commit.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | `python scripts/validate.py` (Phase 3 master CLI) + `pytest` (Phase 3 regression suite) |
| **Schema lib** | `jsonschema >= 4.21` (Draft 2020-12) |
| **YAML parser** | `ruamel.yaml >= 0.18` |
| **Quick run** | `python scripts/validate.py instances/<changed-file>` (per-file, <1s) |
| **Full suite** | `python scripts/validate.py instances/ && pytest tests/ -q` (full corpus + regression) |
| **Pre-commit** | `aviation-validate` hook auto-runs validate.py on staged YAMLs (Phase 3) |
| **CI** | GitHub Actions `validate` job runs `python scripts/validate.py instances/` on every push (Phase 3) |
| **Estimated runtime** | quick: <1s · full: <15s for ~30 instances + 23 fixtures |

Phase 4 ADDS NO new test infrastructure — it consumes Phase 3's validators as the gate.

---

## Sampling Rate

- **After every instance file commit:** `python scripts/validate.py instances/<changed-file>` (or whole `instances/` for cross-record validators) — ≤1s
- **After every plan wave:** `python scripts/validate.py instances/` exits 0 + `pytest tests/ -q` passes
- **Before phase verification:** Full `python scripts/validate.py instances/ docs/` exits 0; CI green on origin/main; `git ls-files docs/ | wc -l` ≥ 9 (3 source docs × 3 files each)
- **Max feedback latency:** 15 seconds (full suite); 1 second (per-file)

---

## Per-REQ-ID Verification Map

| REQ-ID | Plan | Wave | Behavior | Test Type | Automated Command | Status |
|--------|------|------|----------|-----------|-------------------|--------|
| **DOC-01** | 04-01 | 1 | `docs/<domain>/<doc-id>/{source.{pdf,md},processed.md,metadata.yaml}` layout exists for ≥3 documents | shell | `find docs -mindepth 3 -name 'metadata.yaml' \| wc -l \| awk '{ if ($1 < 3) exit 1 }'` | ⬜ pending |
| **DOC-02** | 04-01 | 1 | Each metadata.yaml has all 11 mandatory fields (title, doc_type, language, source_url, publication_date, effective_date, confidentiality, domain_tags, version, file_hash, processed_by) | shell + python | `for f in docs/*/*/metadata.yaml; do for k in title doc_type language source_url publication_date effective_date confidentiality domain_tags version file_hash processed_by; do grep -q "^$k:" "$f" \|\| { echo MISSING $k in $f; exit 1; }; done; done` | ⬜ pending |
| **DOC-03** | 04-04 | 2 | `docs/README.md` documents manual + scripted import workflow + reviewer roles + AI-extracted entity destination + confidentiality gating | grep | `for term in "Manual Import" "Scripted Import" "AI 接力" "confidentiality" "_pending"; do grep -q "$term" docs/README.md \|\| { echo MISSING $term; exit 1; }; done` | ⬜ pending |
| **DOC-04** | 04-04 | 2 | `docs/README.md` documents the confidentiality-gating rule (`restricted`/`itar_ear` not ingested by default) AND lists all 4 confidentiality enum values; demo docs are intentionally all `public` (no restricted demos shipped) | grep | `grep -q "not ingested by default" docs/README.md && grep -q "restricted" docs/README.md && grep -q "itar_ear" docs/README.md` | ⬜ pending |
| **DEMO-01** | 04-02 + 04-03 | 1 | ≥1 instance per entity type (22 types: 17 baseline + 5 ADR-002) | shell | `for t in aircraft-model aircraft-system subsystem component requirement regulation-clause standard procedure failure-mode maintenance-task cfd-method simulation-case mesh-requirement turbulence-model accident-case document expert-note material test-case test-report person organization; do find instances/entities/$t -name '*.yaml' \| head -1 \| grep -q . \|\| { echo MISSING $t; exit 1; }; done` | ⬜ pending |
| **DEMO-02** | 04-04 | 2 | ≥3 relation instances spanning ≥3 different relation types | shell + python | `python -c "from pathlib import Path; import yaml; rels = [yaml.safe_load(open(p)) for p in Path('instances/relations').rglob('*.yaml')]; types = set(r.get('type') for r in rels); assert len(rels) >= 3 and len(types) >= 3, f'have {len(rels)} relations of {len(types)} types'"` | ⬜ pending |
| **DEMO-03** | 04-01 | 1 | 3 source documents (regulation, CFD paper, accident report) each with full DOC-02 metadata + processed.md | shell | `test -d docs/regulations && test -d docs/cfd-papers && test -d docs/accident-reports && find docs -name 'processed.md' \| wc -l \| grep -q '^[3-9]$'` | ⬜ pending |
| **DEMO-04** | 04-02 + 04-04 | 1+2 | One ExpertNote with canonical provenance/source/confidence, cited in `docs/README.md` `AI 接力开发指南` | grep | `find instances/entities/expert-note -name '*.yaml' \| head -1 \| xargs grep -l "provenance:" && grep -q "expert-note.*canonical" docs/README.md` | ⬜ pending |
| **DEMO-05** | 04-02 + 04-04 | 1+2 | One RegulationClause with `status: superseded` + `superseded_by` → active replacement RegulationClause | shell + grep | `grep -l "status: superseded" instances/entities/regulation-clause/*.yaml \| head -1 \| xargs grep -q "superseded_by:"` | ⬜ pending |
| **DEMO-06** | 04-04 | 2 | One AI-extracted record in `instances/_pending/` (NOT in canonical, grep-verified) | shell | `find instances/_pending -name '*.yaml' \| wc -l \| awk '{ if ($1 < 1) exit 1 }' && ! find instances -path instances/_pending -prune -o -type f -name '*.yaml' -print \| xargs grep -l "method: ai_extracted" 2>/dev/null \| grep -v _pending` | ⬜ pending |
| **DEMO-07** | 04-02 | 1 | One bilingual entity using `i18n: { zh, en }` pattern | grep | `find instances/entities -name '*.yaml' \| xargs grep -l "i18n:" \| head -1 \| xargs grep -E "^\s+(zh\|en):"` | ⬜ pending |
| **Cross-cutting (validators stay green)** | all | all | After every wave, `python scripts/validate.py instances/` exits 0 (zero ERROR-severity findings; warnings OK) | shell | `python scripts/validate.py instances/` | ⬜ pending |
| **Cross-cutting (CI green)** | 04-05 | 3 | After phase close-out commit, GitHub Actions CI green on main | shell | `gh run list --branch main --limit 1 --json conclusion --jq '.[0].conclusion' \| grep -q success` | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Phase 4 has **NO Wave-0 deliverables** — Phase 3 already shipped:
- `scripts/validate.py` master CLI (works on `instances/` even when empty — exits 0)
- `scripts/validators/*.py` (5 active validators)
- `pre-commit` aviation-validate hook
- GitHub Actions CI lint + validate + test jobs
- pytest suite (Phase 4 instance additions extend the corpus index automatically)

Phase 4 is purely about **populating** the validated artifacts.

---

## Manual-Only Verifications

| Behavior | REQ-ID | Why Manual | Test Instructions |
|----------|--------|------------|-------------------|
| Source-document `processed.md` faithfully represents source content (no fabrication) | DOC-02, DEMO-03 | Subjective fidelity check — only a human can confirm the Markdown extract matches the PDF/source | Reviewer opens source.{pdf,md} and processed.md side-by-side; confirms key claims preserved, no hallucinated content added by extraction tool |
| `docs/README.md` 5-minute stranger test | DOC-03, AIH-02 | Self-explanation quality is human judgment | Reviewer reads docs/README.md cold (no prior context); asserts after 5 minutes: knows where to put a new doc, knows when to use `_pending/`, knows what `confidentiality: restricted` means for ingestion |
| Bilingual entity `i18n.zh / i18n.en` translations are accurate | DEMO-07 | Translation quality is human judgment | Reviewer (bilingual) confirms zh translation matches en intent; not just literal token-by-token transliteration |

---

## Validation Sign-Off

- [ ] All 11 phase REQ-IDs map to either an `<automated>` verify or a manual sign-off entry
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify (planner enforces)
- [ ] `python scripts/validate.py instances/` exits 0 after every wave
- [ ] `pytest tests/ -q` exits 0 after every wave
- [ ] CI green on main after phase close commit
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s for full suite
- [ ] `nyquist_compliant: true` set in this frontmatter once all entries are ✅

**Approval:** pending (planner sets `nyquist_compliant: true` after task-level mapping; phase verifier flips after CI green-run)
