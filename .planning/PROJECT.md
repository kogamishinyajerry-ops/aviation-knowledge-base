# Aviation Knowledge Base MVP

## What This Is

一个面向航空领域（民用/军用航空、CFD、适航、飞机构型、系统、部件、标准、论文、项目经验）的工程级知识库底座。第一阶段不做复杂 AI Agent，先把"骨架 + 文档 + schema + 配置 + 最小 demo"做扎实，作为后续 GraphRAG / Agent / 知识图谱演化的可演化基线。面向用户：航空工程师、CFD/适航研究人员、以及后续接手开发的 AI 编码助手（Claude / Codex / DeepSeek）。

## Core Value

**每一条知识都可追溯来源，每一个 AI 回答都有 citation；schema 可演化、版本化、对人类和 AI 都可读。** 如果其他都失败，这一条不能失守 —— 否则就是另一个不可信的航空"AI 大模型聊天框"。

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

(None yet — greenfield)

### Active

<!-- Current scope. Building toward these. -->

- [ ] **R1** 项目目录结构 + Git 基线 + CI 占位（lint/schema validation）
- [ ] **R2** PRD（航空知识库产品需求文档），定义用户角色、场景、范围、非目标、成功指标
- [ ] **R3** Ontology schema：17 个核心实体类型（AircraftModel / AircraftSystem / Subsystem / Component / Requirement / RegulationClause / Standard / Procedure / FailureMode / MaintenanceTask / CFDMethod / SimulationCase / MeshRequirement / TurbulenceModel / AccidentCase / Document / ExpertNote）
- [ ] **R4** Ontology relations：13 个核心关系类型（part_of / applicable_to / constrained_by / verified_by / derived_from / supersedes / cites / causes / mitigated_by / requires / equivalent_to / conflicts_with / used_in）
- [ ] **R5** 每个实体/关系含 `confidence` 字段、`source` 字段、`provenance.method` (human / ai_extracted / hybrid) 区分人工 vs AI 抽取知识
- [ ] **R6** Schema 版本管理（每个 schema 文件含 `version`，遵循 semver；CHANGELOG.md 记录 breaking change）
- [ ] **R7** 文档导入与元数据规范：支持类型 (PDF / Markdown / HTML / DOCX 文档)、必备元数据字段（title / type / source_url / publication_date / language / confidentiality / domain_tags / version）
- [ ] **R8** RAG pipeline 设计文档：chunking 策略 / embedding 模型选型 / 检索（向量 + BM25 + RRF）/ citation 注入 / guardrail / 评估方法
- [ ] **R9** Wiki.js + RAGFlow 部署方案说明：架构图、容器拓扑、网络/存储/认证选型、docker-compose 草案（**不实跑**）、与未来 GraphRAG 的接口预留
- [ ] **R10** 最小 demo 数据样例：≥5 实体（含每个 17 类型至少 1 条覆盖性样例）+ ≥3 关系 + ≥3 文档元数据 + 1 条 ExpertNote 示范来源追溯写法
- [ ] **R11** 后续阶段路线图：GraphRAG / Agent / 知识图谱演化路径，附触发条件与依赖
- [ ] **R12** 设计文档可读性约束：所有设计文档含"AI 接力开发指南"小节，明确文件目录、schema 版本、术语表、未决项 —— 让 Claude / Codex / DeepSeek 后续可无损接力

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- **Dify** 不引入 — 第一阶段不做"自动决策型 Agent"，Dify 偏 Agent 编排，引入会增加耦合；后续若做工作流可补
- **复杂前端** — 第一阶段只用 Wiki.js 自带门户和 RAGFlow 自带 UI，不自研 Vue/React 前端
- **完整图数据库**（Neo4j/Nebula）— 第一阶段 schema 用 YAML + JSON Schema，等 GraphRAG 阶段再决定 backend
- **大规模自动爬虫** — 第一阶段只手动/批量导入文档，不做无限爬抓
- **决策型 Agent** — 不做"AI 自动调用工具/做决定"的 agentic loop（只做 retrieval-augmented Q&A）
- **无来源 AI 回答** — 不允许任何 AI 输出脱离 citation；幻觉零容忍
- **OCR / 图像理解** — 第一阶段只处理文本文档（PDF 文本层、MD、HTML、DOCX）；扫描件 OCR 推到后续阶段
- **多租户 / 复杂 RBAC** — 第一阶段单组织、单角色（admin + reader）；细粒度权限推到后续

## Context

**为什么现在做：**
- 用户已沉淀大量航空 / CFD / 适航 / 飞机模型相关项目（cfd-ai-workbench、aircraft-cad-report、AeroPower-RAG、cfd-harness-unified 等），需要一个**结构化沉淀层**而不是分散在各项目 README 和 .planning/ 里
- 用户的 AeroPower-RAG 项目已经验证了 Hybrid Retrieval（BM25 + 向量 + RRF）在中文航空适航文档上的可行性（recall@3 = 100%），本项目需要把这种能力**通用化、可复用**
- cfd-harness-unified 的 Notion 同步经验证明了"决策门户 + 可读源"的双层架构有价值；本项目要把这个理念扩展到知识层

**技术环境：**
- 平台：macOS（Apple Silicon），开发工具链以 Node.js / Python 为主
- 现有相关项目可作为最小 demo 数据来源（航空发动机部件分析、CFD 案例、适航法规片段）

**用户研究/反馈主题：**
- 航空工业软件交付要求过程可审计 → 知识库每条记录必须可追溯
- AI 答案不带 citation = 不可用 → guardrail 必须在 RAG pipeline 设计阶段就考虑
- 论文复现存在"捏造图表"风险（Case 3 H-Darrieus 教训）→ AI 自动抽取知识必须和人工知识分开标记

**已知风险/技术债：**
- 航空 ontology 是开放性问题（ATA Spec 100 / S1000D / AP233 都不完全适用）；本项目自定义 ontology，但需要预留映射到这些标准的字段
- Wiki.js 和 RAGFlow 的认证体系不同（Wiki.js 用本地账户/OAuth，RAGFlow 用自己的 user system），需要设计单点认证或网关层

## Constraints

- **Tech Stack**: Wiki.js（门户）+ RAGFlow（RAG 工作流）+ YAML/Markdown（schema）+ JSON Schema（校验）+ Git（版本管理）— 已与用户对齐，不得变更
- **Excluded Tech**: Dify、复杂前端框架（Vue/React 自研）、图数据库（Neo4j/Nebula）、自动决策型 Agent、自动爬虫 — 第一阶段硬约束
- **Quality**: 每条知识可追溯来源；AI 回答必带 citation；实体/关系含 confidence；schema 版本化；区分人工 vs AI 抽取
- **Documentation**: 设计文档必须适合 Claude / Codex / DeepSeek 接力 —— 自含、可读、术语清晰、未决项明确
- **Deliverable Mode**: 第一阶段优先骨架 + 文档 + schema + 配置 + 最小 demo，**不写大量业务代码**
- **Deployment**: docker-compose 草案不要求实跑，第一阶段交付的是"部署方案选型 + 配置文件骨架"
- **Auditability**: 所有 schema 变更必须经 PR + CHANGELOG，Git 是真值

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 用 Wiki.js 做门户 | 开源、Markdown 原生、中英双语友好、可自托管、无 vendor lock-in | — Pending（部署阶段验证） |
| 用 RAGFlow 做 RAG 工作流 | 开源、表格/PDF 解析在中文工业文档上更稳、可本地部署、有 citation/visualization 内置 | — Pending（RAG 设计阶段验证） |
| 不引入 Dify | 第一阶段不做 Agent 编排；Dify 引入会增加耦合 | ✓ Good（明确边界） |
| Ontology 用 YAML + JSON Schema | 人读 + 机器校验同源；无需图数据库即可建模；后续可平滑升级到 RDF/OWL/Neo4j | — Pending（schema 阶段验证） |
| 不上图数据库 | 第一阶段 schema 还在迭代，过早绑 backend 浪费；YAML 足够支撑 ≤10K 三元组的 demo 规模 | — Pending（路线图阶段重审） |
| confidence + provenance.method 字段必填 | 区分人工 vs AI 抽取，避免 H-Darrieus 类"捏造图表"问题 | — Pending（schema 阶段固化） |
| 不实跑 docker-compose | 第一阶段交付"方案 + 选型说明"，避免陷入运维细节 | ✓ Good（节省第一阶段时间） |
| GSD workflow 强制走 | 用户 CLAUDE.md 硬性要求；保证规划-执行同步 | ✓ Good |
| 模型选型 Quality（Opus 主导）| 用户 CLAUDE.md v2.0 (2026-05-03) 把 Opus 4.7 1M 设为开发主驱动 | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-03 after initialization*
