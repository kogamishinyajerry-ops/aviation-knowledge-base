# docs/GLOSSARY.md — Bilingual Aviation Terminology

> **AI 接力开发指南** (AIH-04): A fresh Claude / Codex / DeepSeek session can use this
> glossary to (a) translate user queries between Chinese and English without guessing,
> (b) verify entity-type names match the canonical schema label, (c) seed the RAG
> bilingual expansion dictionary (`.planning/design/RAG_PIPELINE.md` §4.2 / §7,
> expansion weight = 0.3).
>
> Status: v0.1 seed (Phase 6, AIH-04). Target: ≥50 entries; this file currently
> contains 65 rows. Future phases append; do **not** reorder existing rows (would
> break URL fragment links from `RAG_PIPELINE.md`, `PRD_v0.md` / `PRD_v1.md`).

## How to Use

- **For RAG retrieval**: this file is consumed by `scripts/exporters/to_ragflow.py`
  as a synonym dictionary (Phase 7 wiring). Expansion weight = 0.3 per
  `.planning/design/RAG_PIPELINE.md` §4.2 (cross-language hit rate validated at
  100% ZH→EN / 80% EN→ZH on the AeroPower-RAG benchmark — see
  `.planning/research/PITFALLS.md` Pitfall 6/7).
- **For schema authors**: every entity type in `ontology/schemas/entity.*.schema.json`
  has a row here. Adding a new entity type? Add a glossary row in the same PR
  (enforced by `06-VALIDATION.md` link-coverage check).
- **For human readers**: the "Cross-reference" column points at the canonical home
  of the term (entity schema, design doc, regulation, or external standard). Click
  through to find the authoritative definition.

## Conventions

- **Order**: alphabetical by English term (case-insensitive).
- **Columns** (4): 中文 | English | 1-line definition | Cross-reference path.
- **Schema cross-refs** use repository-relative paths
  (e.g. `ontology/schemas/entity.aircraft-model.schema.json`) — note the
  **kebab-case** filename pattern (`entity.<kebab-name>.schema.json`).
- **ATA chapter terms** reference `.planning/research/STACK.md#aviation-reference-standards`.
- **External standards** (FAR / EASA CS / CCAR) reference the
  `regulation-clause` entity's `jurisdiction` field with the issuing body code
  (FAA / EASA / CAAC).
- **Conditional rows** for ADR-deferred concepts (e.g. Configuration deferred per
  ADR-002) carry an explicit `(if accepted in ADR-...)` marker — leave the
  conditional language intact until the deferred ADR is decided.
- **Bilingual i18n pattern**: glossary mirrors the `i18n: { zh, en }` convention
  established by Phase 4 DEMO-07 (see
  `instances/entities/expert-note/cn-en-bilingual-fadec-note.yaml`).

## Glossary

| 中文 | English | Definition (1 line) | Cross-reference |
|------|---------|---------------------|-----------------|
| 事故案例 | AccidentCase | Investigated aircraft accident with causal factors and lessons learned. | `ontology/schemas/entity.accident-case.schema.json` |
| 迎角 | Angle of attack | Angle between the wing chord line and the relative wind direction. | external — aerodynamics fundamental |
| 适航指令 | Airworthiness Directive (AD) | Mandatory regulatory action requiring inspection / repair / modification on a fleet. | `ontology/schemas/entity.regulation-clause.schema.json` |
| 适航性 | Airworthiness | The condition of an aircraft being suitable and safe for flight per regulations. | `.planning/PROJECT.md` Core Value |
| 飞机型号 | AircraftModel | Top-level entity representing a certified aircraft variant (e.g. Boeing 737-800). | `ontology/schemas/entity.aircraft-model.schema.json` |
| 飞机系统 | AircraftSystem | A functional system (e.g. ATA-71 Powerplant, ATA-21 Air Conditioning). | `ontology/schemas/entity.aircraft-system.schema.json` |
| 机身 | Airframe | Aircraft structural body excluding powerplant and systems internals. | `ontology/schemas/entity.aircraft-system.schema.json` |
| 进近 | Approach | Flight phase where aircraft descends toward landing runway, typically last 5-10 nm. | `ontology/schemas/entity.procedure.schema.json` (flight phase enum) |
| ATA 章节 | ATA Chapter | iSpec 2200 chapter taxonomy used as `ata_chapter` field on systems/subsystems. | `.planning/research/STACK.md#aviation-reference-standards` |
| 中国民用航空规章 | CCAR (Chinese Civil Aviation Regulations) | Chinese airworthiness regulatory framework. | `regulation-clause.jurisdiction = CAAC` |
| CFD 方法 | CFDMethod | Computational fluid dynamics method (RANS / LES / DNS / hybrid). | `ontology/schemas/entity.cfd-method.schema.json` |
| 引用 | Citation | A retrievable pointer from an entity / answer back to a source document with locator. | `.planning/research/PITFALLS.md` Pitfall 1 |
| 爬升 | Climb | Flight phase where aircraft increases altitude after takeoff. | `ontology/schemas/entity.procedure.schema.json` (flight phase enum) |
| 燃烧室 | Combustor | Engine section where fuel and compressed air ignite to drive the turbine. | `ontology/schemas/entity.component.schema.json` |
| 部件 | Component | Individual hardware unit with part number, mass, dimensions, ATA chapter. | `ontology/schemas/entity.component.schema.json` |
| 压气机 | Compressor | Engine section that compresses inlet air before combustion. | `ontology/schemas/entity.component.schema.json` |
| 置信度 | Confidence | Calibrated score (0..1) on each entity reflecting source authority + verification depth. | `ontology/_meta.schema.json` `confidence` object |
| 构型 | Configuration | A specific physical / effectivity variant of an aircraft model. | `ontology/schemas/entity.configuration.schema.json` (deferred — if accepted in ADR-002 follow-up) |
| 关键设计评审 | Critical Design Review (CDR) | Engineering milestone gate confirming design is ready for production. | external — milestone vocab |
| 巡航 | Cruise | Flight phase where aircraft maintains roughly constant altitude and speed. | `ontology/schemas/entity.procedure.schema.json` (flight phase enum) |
| 直接数值模拟 | DNS (Direct Numerical Simulation) | CFD method resolving all turbulent scales without modeling. | `cfd-method.method_class` enum |
| 文档 | Document | Source artifact (PDF / regulation / paper / report) with metadata sidecar. | `ontology/schemas/entity.document.schema.json` |
| 欧洲适航规范 | EASA CS (Certification Specifications) | European Union Aviation Safety Agency airworthiness regulations. | `regulation-clause.jurisdiction = EASA` |
| 有效性范围 | Effectivity | The applicability scope of a configuration / requirement (e.g. serial number range). | `ontology/schemas/entity.configuration.schema.json` (deferred — if accepted in ADR-002 follow-up) |
| 尾翼 | Empennage | Rear stabilizing assembly: vertical + horizontal tail surfaces. | `ontology/schemas/entity.aircraft-system.schema.json` |
| 发动机 | Engine | Propulsion unit; aviation context = turbofan / turboprop / piston / turboshaft. | `ontology/schemas/entity.component.schema.json` |
| 专家笔记 | ExpertNote | Human-authored note with author, topic, related entities, full provenance. | `ontology/schemas/entity.expert-note.schema.json` |
| 联邦航空规章 | FAR (Federal Aviation Regulations) | U.S. Title 14 CFR airworthiness framework. | `regulation-clause.jurisdiction = FAA` |
| 失效模式 | FailureMode | Specific way a component / subsystem can fail, with conditions and effects. | `ontology/schemas/entity.failure-mode.schema.json` |
| 失效模式与影响分析 | Failure Mode and Effects Analysis (FMEA) | Systematic technique for evaluating failure modes against system effects. | external — safety analysis vocab |
| 飞行阶段 | Flight phase | Stage of flight (taxi / takeoff / climb / cruise / descent / approach / landing). | `ontology/schemas/entity.procedure.schema.json` |
| 全权限数字发动机控制 | FADEC (Full Authority Digital Engine Control) | Engine control system providing full digital authority over all engine parameters. | `instances/entities/expert-note/cn-en-bilingual-fadec-note.yaml` (DEMO-07 bilingual reference) |
| 进气道 | Inlet | Engine forward section that captures and decelerates incoming airflow. | `ontology/schemas/entity.component.schema.json` |
| 着陆 | Landing | Flight phase where aircraft touches down on runway. | `ontology/schemas/entity.procedure.schema.json` (flight phase enum) |
| 起落架 | Landing gear | Undercarriage system supporting aircraft on ground. | `ontology/schemas/entity.aircraft-system.schema.json` |
| 大涡模拟 | LES (Large Eddy Simulation) | CFD method resolving large turbulent scales, modeling small. | `cfd-method.method_class` enum |
| 马赫数 | Mach number | Ratio of flow velocity to local speed of sound. | external — aerodynamics fundamental |
| 维修任务 | MaintenanceTask | Scheduled maintenance action with interval, prerequisites, tools. | `ontology/schemas/entity.maintenance-task.schema.json` |
| 材料 | Material | Alloy / composite / polymer specification used in components. | `ontology/schemas/entity.material.schema.json` |
| 最低设备清单 | MEL (Minimum Equipment List) | Permitted dispatch with specified inoperative items listed. | `ontology/schemas/entity.regulation-clause.schema.json` |
| 网格要求 | MeshRequirement | CFD mesh constraints (y+, cell count, refinement zones). | `ontology/schemas/entity.mesh-requirement.schema.json` |
| 喷管 | Nozzle | Engine exhaust component shaping flow for thrust. | `ontology/schemas/entity.component.schema.json` |
| 组织 | Organization | Issuing body / manufacturer / regulator entity. | `ontology/schemas/entity.organization.schema.json` |
| 人员 | Person | Human actor (engineer / reviewer / regulator) referenced in provenance. | `ontology/schemas/entity.person.schema.json` |
| 俯仰 | Pitch | Rotation about lateral axis (nose up / down). | external — flight dynamics |
| 动力装置 | Powerplant | Aircraft propulsion installation (engine + nacelle + accessories), ATA-71/72/73/74. | `ontology/schemas/entity.aircraft-system.schema.json` |
| 初步设计评审 | Preliminary Design Review (PDR) | Engineering milestone gate confirming design is ready for detailed work. | external — milestone vocab |
| 程序 | Procedure | Operational / maintenance procedure with steps, prerequisites, hazards. | `ontology/schemas/entity.procedure.schema.json` |
| 螺旋桨 | Propeller | Rotating blade assembly converting engine torque to thrust. | `ontology/schemas/entity.component.schema.json` |
| 来源 | Provenance | Structured record of how / when / by whom a record was created. | `ontology/_meta.schema.json` `provenance` object |
| 雷诺平均 | RANS (Reynolds-Averaged Navier-Stokes) | CFD method using time-averaged equations + turbulence model. | `cfd-method.method_class` enum |
| 规章条款 | RegulationClause | Specific regulatory clause with jurisdiction, doc, status, effective date. | `ontology/schemas/entity.regulation-clause.schema.json` |
| 需求 | Requirement | Engineering / regulatory requirement with verification method and effectivity. | `ontology/schemas/entity.requirement.schema.json` |
| 雷诺数 | Reynolds number | Ratio of inertial to viscous forces in flow. | external — fluid dynamics |
| 修订 | Revision | Versioned change to an entity (referenced by `has_revision` relation; relation deferred). | `ontology/CHANGELOG.md` (semver per ontology/VERSION) |
| 滚转 | Roll | Rotation about longitudinal axis (wings up / down). | external — flight dynamics |
| 旋翼 | Rotor | Rotating airfoil assembly (helicopter main rotor / tail rotor). | `ontology/schemas/entity.component.schema.json` |
| 服务通告 | Service Bulletin (SB) | Manufacturer-issued recommended action on fielded aircraft. | `ontology/schemas/entity.regulation-clause.schema.json` |
| 仿真算例 | SimulationCase | A specific CFD run with method / mesh / turbulence / BC / results. | `ontology/schemas/entity.simulation-case.schema.json` |
| 标准 | Standard | Industry / issuing-body standard (RTCA / SAE / ASTM / ISO). | `ontology/schemas/entity.standard.schema.json` |
| 子系统 | Subsystem | Decomposition of an AircraftSystem with its own ATA subchapter. | `ontology/schemas/entity.subsystem.schema.json` |
| 替代关系 | Supersession | Relation where a newer regulation / note replaces an older one. | `ontology/schemas/relation.supersedes.schema.json` |
| 补充型号合格证 | Supplemental Type Certificate (STC) | Regulatory approval of a major modification to an existing type-certified design. | `ontology/schemas/entity.regulation-clause.schema.json` |
| 测试用例 | TestCase | A specific test definition (input / expected output / conditions). | `ontology/schemas/entity.test-case.schema.json` |
| 测试报告 | TestReport | Recorded result of running one or more TestCases. | `ontology/schemas/entity.test-report.schema.json` |
| 涡轮 | Turbine | Engine section extracting work from hot gas to drive compressor. | `ontology/schemas/entity.component.schema.json` |
| 湍流模型 | TurbulenceModel | RANS closure (SA / k-omega-SST / k-epsilon / RSM). | `ontology/schemas/entity.turbulence-model.schema.json` |
| 型号合格证 | Type Certificate (TC) | Regulatory approval of an aircraft design. | `ontology/schemas/entity.aircraft-model.schema.json` |
| 机翼 | Wing | Lift-generating airfoil assembly. | `ontology/schemas/entity.aircraft-system.schema.json` |
| 偏航 | Yaw | Rotation about vertical axis (nose left / right). | external — flight dynamics |
| y 加 | y+ | Dimensionless wall distance in CFD; constrains mesh near walls. | `ontology/schemas/entity.mesh-requirement.schema.json` |
| 混合检索 | Hybrid retrieval | Vector + BM25 + RRF (Reciprocal Rank Fusion) combined retrieval; Phase 5 default. | `.planning/design/RAG_PIPELINE.md` §4 |
| k-omega-SST 模型 | k-omega-SST | Two-equation RANS closure (Menter 1994); industry default for external aero. | `ontology/schemas/entity.turbulence-model.schema.json` |

## Index by Cluster

For readers grepping by domain rather than alphabet:

- **Entity-type cluster** (one row per `ontology/schemas/entity.*.schema.json`):
  AccidentCase, AircraftModel, AircraftSystem, CFDMethod, Component, Document,
  ExpertNote, FailureMode, MaintenanceTask, Material, MeshRequirement,
  Organization, Person, Procedure, RegulationClause, Requirement,
  SimulationCase, Standard, Subsystem, TestCase, TestReport, TurbulenceModel.
- **Aviation structure cluster**: Airframe, Empennage, Engine, Inlet,
  Landing gear, Nozzle, Powerplant, Propeller, Rotor, Turbine, Wing.
- **Regulatory cluster**: AD (Airworthiness Directive), Airworthiness, CCAR,
  EASA CS, FAR, MEL, RegulationClause, Service Bulletin, STC, TC.
- **CFD cluster**: CFDMethod, DNS, Hybrid retrieval, k-omega-SST, LES,
  MeshRequirement, RANS, Reynolds number, SimulationCase, TurbulenceModel, y+.
- **Flight-dynamics cluster**: Angle of attack, Approach, Climb, Cruise,
  Flight phase, Landing, Mach number, Pitch, Roll, Yaw.
- **Provenance / audit cluster**: Citation, Confidence, FADEC (bilingual demo),
  Provenance, Revision, Supersession.
- **Engineering process cluster**: CDR, Configuration (deferred),
  Effectivity, FMEA, PDR.

## Update Discipline

- New entity schema → new glossary row in same PR.
- Renamed term → mark old row `(deprecated, use <new>)` for one minor release; do
  not delete (RAG bilingual expansion still keys off old entries).
- Adding a row: maintain alphabetical-by-English ordering; rebuild the cluster
  index above only when a new cluster is introduced.
- This file is consumed by `to_ragflow.py`; do not insert HTML / non-ASCII
  punctuation that breaks Markdown table parsers.
