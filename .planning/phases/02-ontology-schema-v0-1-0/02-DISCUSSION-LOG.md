# Phase 2: Ontology Schema v0.1.0 — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `02-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-05-03
**Phase:** 02-ontology-schema-v0-1-0
**Areas discussed:** Entity additions, Relation additions + boundaries, Provenance/Confidence/i18n field shape, Triple-export + schema versioning placement
**Mode:** discuss (interactive AskUserQuestion)
**Facilitator:** Claude Opus 4.7 (1M ctx)

---

## Gray Area Selection

User selected ALL 4 proposed gray areas (multiSelect AskUserQuestion):

| Area | Selected? |
|------|-----------|
| Entity additions ADR (ONT-E-19..22) | ✓ |
| Relation additions + boundaries (ONT-R-15..19) | ✓ |
| Provenance / Confidence / i18n 字段形状 | ✓ |
| Triple-export ADR + schema versioning placement | ✓ |

Areas NOT presented (deferred to research phase): ATA chapter enum strictness; S1000D Issue 6 DMC shape.

---

## Area 1: Entity additions

### Q1.1 — Material entity in v0.1.0?

| Option | Description | Selected |
|--------|-------------|----------|
| 接受 (Recommended) | 陆航重型依赖材料证据（舵机合金、复材损伤容限）；以后补 = 要从 Component.composition 重抽 | ✓ |
| 推到 v0.2.0 | v0.1.0 先用 Component.material 存为自由文本；干净但重抽成本高 | |

**Rationale:** Material is first-class in aerospace. Deferring forces free-text in Component.composition with high re-extraction cost.

### Q1.2 — TestCase / TestReport entity?

| Option | Description | Selected |
|--------|-------------|----------|
| 接受 (Recommended) | 适航需要 verified_by 指向具体试验；现在 Requirement.verified_by 类型仅是 Procedure 太窄 | ✓ |
| 推到 v0.2.0 | 临时用 Procedure 为万能验证载体，重抽代价中等 | |

**Rationale:** DO-160/DO-178C/DO-254 audit trail requires distinct test-evidence entity. Procedure is too generic.

### Q1.3 — Configuration / EffectivityRange?

| Option | Description | Selected |
|--------|-------------|----------|
| 推到 v0.2.0 (Recommended) | FEATURES.md 已将其标为 v1.x；现阶段 demo data 尚未紧迫需要 SN/configuration 范围实体 | ✓ |
| 接受 | AD/SB applicability 本质上需要范围表达，预留者现在结构面更后期低 | |

**Rationale:** Demo data won't exercise serial-number applicability in v0.1.0. Defer until AD/SB data lands.

### Q1.4 — Person / Organization?

| Option | Description | Selected |
|--------|-------------|----------|
| 接受 (Recommended, must) | provenance.actor / reviewer / source.published_by 全部是 Person/Org URI；不接受则这些字段退化为自由文本，违反 Core Value | ✓ |
| 仅接受作为 Stub | 只定义 Person/Org 最小 schema (id + name + type)，详细字段推到 v0.2.0 | |

**Rationale:** Provenance fields already point at Person URIs. Without the schema they degrade to strings and break the H-Darrieus lock.

---

## Area 2: Relation additions + boundaries

### Q2.1 — interfaces_with + boundary with `requires`?

| Option | Description | Selected |
|--------|-------------|----------|
| 接受，边界如上 (Recommended) | interfaces_with = peer-tier system↔system; requires = cross-tier (component requires task / sim requires mesh)。ADR 记入 例子 | ✓ |
| 推到 v0.2.0 | v0.1.0 先用 part_of 隶属表达接口；会丢语义但可加 | |

### Q2.2 — complies_with (vs constrained_by)?

| Option | Description | Selected |
|--------|-------------|----------|
| 接受 (Recommended) | complies_with = 明确规范遵从（FAR §25.305）；constrained_by = 一般约束 | ✓ |
| 不接受，用 constrained_by | 语义重叠；区分价值低 | |

### Q2.3 — has_revision processing?

| Option | Description | Selected |
|--------|-------------|----------|
| 不作关系，收进实体 version_history[] 字段 (Recommended) | Revision 是内容演化属性，嵌入实体更自然；schema_version 仍然单独留 | ✓ |
| 作为关系接受 | 顯化版本链，但产生大量低价值节点 | |

### Q2.4 — applicable_during_phase + generated_by?

| Option | Description | Selected |
|--------|-------------|----------|
| applicable_during_phase 接受作关系；generated_by 作为字段入 provenance (Recommended) | 飞行阶段是独立语义，需专门关系；generated_by 有 provenance.actor / source.tool 已能表达 | ✓ |
| 两者都推到 v0.2.0 | 节省 ADR 面积，但 procedure/req 与飞行阶段的关联会丢到自由文本里 | |

---

## Area 3: Provenance / Confidence / i18n / version_history field shapes

### Q3.1 — confidence.score scale?

| Option | Description | Selected |
|--------|-------------|----------|
| decimal 0.0–1.0 + rationale (Recommended) | 调校空间细，能表达 `>0.85` 的 H-Darrieus 锁阈值；需 rationale 句子描述为什么评这个分 | ✓ |
| ordinal 5 级 (very_low…very_high) | 人工评分友好，但阈值锁会变 `>=high`，量化仓 粗 | |
| 混合 score(0–1) + tier(low/med/high) | 面积大；schema 复杂度 双倍，v0.1.0 不推荐 | |

### Q3.2 — i18n field shape?

| Option | Description | Selected |
|--------|-------------|----------|
| 平面 {label:{zh,en}, full_text:{zh,en}} (Recommended) | 简单，足够表达「某实体召中英变体」；加译者/审译信息需要时从 source / provenance 取 | ✓ |
| 嵌套 {zh:{text,translator,reviewed_by}, en:{...}} | 逐译 provenance 加偏重；v0.1.0 demo 数据不需；适合顶川多语场景 | |
| 授权 Claude (根据字段类型决定) | 诸如 RegulationClause.full_text_zh / full_text_en 用 nested，但 AircraftSystem.label 用 flat — 实体粒度选 | |

### Q3.3 — provenance.method enum naming?

| Option | Description | Selected |
|--------|-------------|----------|
| human / ai_extracted / hybrid_reviewed (Recommended) | 与 research/SUMMARY.md 上下文一致；H-Darrieus 锁表达 `(method==ai_extracted) AND (score>0.85) AND (no reviewer)` 明确 | ✓ |
| manual / extracted / reviewed | 更短但 `extracted` 会被误读为 `从某文档抽取以后不意味 AI 生成` | |

### Q3.4 — version_history[] array shape?

| Option | Description | Selected |
|--------|-------------|----------|
| [{version, date, author, change_summary}] (Recommended) | 4 字段充足；author = Person URI；date = ISO8601；change_summary = 1 句 | ✓ |
| [{version, date, author, change_summary, source}] | 加 source = source object 引用滤改依据；适合重社อ场景，v0.1.0 代价高 | |

---

## Area 4: Triple-export + schema versioning + migrations

### Q4.1 — Triple-export format?

| Option | Description | Selected |
|--------|-------------|----------|
| JSONL `{s,p,o,prov,confidence}` (Recommended) | 一行一三元组；jq 友好；保留 prov+confidence 踢走 GraphRAG (避免丢 H-Darrieus 锁)；后期转 JSON-LD 成本低 | ✓ |
| JSON-LD | 带 @context，与 RDF 生态兑现好；但 v0.1.0 不推 RDF，独类型领走不下例 | |
| RDF / Turtle | 最"正统"；但 v0.1.0 手开贵价；prov 用 PROV-O 能作为 v0.3.0 升级路径 | |

### Q4.2 — Schema versioning placement?

| Option | Description | Selected |
|--------|-------------|----------|
| per-file `version` + per-record `schema_version` 两者都要 (Recommended) | per-file = ontology 本身进化版本（semver, ontology/VERSION = 0.1.0）；per-record schema_version = 每条记录发布时实体 schema 的 版本 快照；二者不同意 | ✓ |
| 只 per-record schema_version | 简单；但会丢 ontology 整体版本 进度详情（发布号 vs 记录带陶） | |
| 只 per-file `version` | 记录中没 schema_version；validator 难以拒 N-1 老记录。不推 | |

### Q4.3 — migrations/ language?

| Option | Description | Selected |
|--------|-------------|----------|
| Python (Recommended) | 与 validator 一致 (Phase 3 scripts/validators/ 为 Python)；jsonschema/ruamel.yaml 生态成熟 | ✓ |
| Node / TypeScript | ajv 生态；但 repo 没 Node 包，要额外引入 package.json | |
| Bash + yq | 轻量；但多文件 cross-ref migration 难表达 | |

### Q4.4 — Phase 2 stub scripts?

| Option | Description | Selected |
|--------|-------------|----------|
| 仅 stub `scripts/exporters/to_jsonl_triples.py` 框架 (Recommended) | Phase 1 已有该 stub。Phase 2 增 加 schema-to-triples 各设计说明/ADR，不实现 | ✓ |
| stub + minimal 实现（在 Phase 2 顺手走通） | Phase 2 代码量增加。 但可以提前验证转换逻辑 | |
| 都推到 Phase 5 (RAG pipeline) | Phase 5 本就设计 RAG 流水线； stub 在 Phase 1 已预留吃 | |

---

## Wrap-up

| Question | Answer |
|----------|--------|
| 还要开倍讨论哪些区域吗？ | I'm ready for context (Recommended) |

ATA chapter enum strictness and S1000D Issue 6 DMC field shape were intentionally **not discussed** — flagged for `/gsd-research-phase 2` to resolve via WebFetch.

## Claude's Discretion (no decision needed)

- Exact `_meta.schema.json` JSON Schema Draft 2020-12 syntax
- Internal directory layout under `ontology/schemas/`
- ADR file naming (`.planning/decisions/ADR-NNN-<slug>.md` proposed)
- ATA chapter list seeding source (research will confirm)

## Deferred Ideas

- Configuration / EffectivityRange entity → v0.2.0
- JSON-LD / RDF Turtle export → v0.3.0+
- Per-translation provenance on i18n → v0.2.0+
- DO-178C/DO-254-specific TestCase fields → v0.2.0+
- ATA chapter enum decision → research phase
- S1000D Issue 6 DMC shape → research phase
