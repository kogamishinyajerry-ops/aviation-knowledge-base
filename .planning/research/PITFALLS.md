# Pitfalls Research

**Domain:** Aviation Knowledge Base (Wiki.js + RAGFlow + YAML/JSON Schema + Git)
**Researched:** 2026-05-03
**Confidence:** HIGH for ontology/provenance/RAG pitfalls (grounded in user's prior projects: AeroPower-RAG hybrid retrieval, cfd-harness-unified Notion/git dual-truth, H-Darrieus Case 3 hallucination incident, cfd-ai-workbench audit-trail philosophy). MEDIUM for Wiki.js+RAGFlow integration specifics (general RAG-stack knowledge, not first-hand verified). HIGH for AI-handoff pitfalls (user has explicit R12 "AI 接力开发指南" requirement).

> **Reading order**: Critical Pitfalls (P1–P12) first — these are the ones that, if missed, force a rewrite or violate Core Value ("每一条知识可追溯，每一个 AI 回答有 citation"). Then Technical Debt, Integration Gotchas, Performance Traps, Security, UX, "Looks Done But Isn't", Recovery Strategies, Phase Mapping.

---

## Critical Pitfalls

### Pitfall 1: 来源字段做成自由文本（"source: 某航空手册"）

**What goes wrong:**
`source` 字段允许自由文本，于是出现 "FAR Part 25"、"民航局文件"、"内部资料 v3" 这类无法回查的字符串。AI 引用照搬，用户点开 citation 发现指向"Document XYZ"但没有页码、章节、URL、document_id —— 整个"可追溯"承诺崩塌。这是 Core Value 的直接违反，也是用户在 cfd-ai-workbench / H-Darrieus 案例中亲历过的"看起来有 citation 实际不可验证"陷阱。

**Why it happens:**
- 早期 demo 数据为了快，YAML 里写一行 `source: FAR 25.1309` 就 push
- JSON Schema 没把 `source` 定成结构化对象（只是 `string`）
- 没人想清楚"一条规章引用最少需要哪些字段才算可验证"
- AI 抽取时模型输出什么就存什么，没强制 normalize

**How to avoid:**
- `source` 在 JSON Schema 里强制成结构化对象，最少必填字段：
  ```yaml
  source:
    document_id: DOC-FAA-FAR25-2024-03   # 必填，全局唯一，对应 Document 实体
    locator:                              # 必填，至少一个
      page: 47
      section: "25.1309(b)"
      paragraph: 2
    retrieval:                            # 必填
      url: "https://www.ecfr.gov/..."     # 或 internal_path
      accessed_at: "2026-05-03"
      content_hash: "sha256:abc..."       # 抓时的内容指纹
    effective_date: "2024-03-15"          # 必填
    superseded_by: null                   # 显式 null，不是省略
  ```
- CI 跑 JSON Schema 校验，缺字段直接 fail（不是 warning）
- 任何 `source` 不能解析回真实文档的实体，禁止 promote 到 canonical

**Warning signs:**
- YAML 里出现 `source: "FAR Part 25"` 这种纯字符串
- `grep -r "source:" data/ | grep -v document_id` 有命中
- AI 回答里 citation 链接是 "[Document XYZ]" 而非具体段落
- 用户问"这条引用对应原文哪一页"时答不上来

**Phase to address:**
**Phase 2 (Schema 设计)** — 必须在第一份 schema 落地前定下来，事后改是 breaking change。

---

### Pitfall 2: AI 抽取的实体未经审核就 promote 到 canonical

**What goes wrong:**
RAGFlow 或 LLM 从 PDF 自动抽取出 "Component: 高压涡轮 / 推力: 12000 lbf"，没有人工 review 直接进 YAML。下游 RAG 检索把 AI 抽错的数字当事实回答用户。这就是 H-Darrieus Case 3 "捏造图表" 的同类问题 —— AI 生成的内容混入"权威源"。

**Why it happens:**
- `provenance.method` 字段被设计成可选或默认 `human`
- 没有 staging 区，AI 抽取直接写主分支
- review gate 是"人工偶尔抽查"而非强制 PR
- confidence score 来自模型自己（self-reported，不可信）

**How to avoid:**
- `provenance.method` 必填，枚举严格限制：`human` / `ai_extracted` / `hybrid_reviewed`（"hybrid"必须有人审过的字段记录）
- AI 抽取的实体先写 `data/staging/ai_extracted/`，**永不**直接进 `data/canonical/`
- promote 流程：人工 review → 把 `provenance.method` 改成 `hybrid_reviewed` 并加 `reviewed_by` + `reviewed_at` → PR 合并到 canonical
- RAG 检索时对 `ai_extracted` 实体加显著标记（"⚠️ 未经人工审核的 AI 抽取内容"）
- CI 检查：canonical 目录下不允许 `provenance.method == ai_extracted`

**Warning signs:**
- `git log` 显示 canonical 数据有"AI 批量导入"commit 没经 review
- canonical 目录下 grep `provenance.method: ai_extracted` 有命中
- 用户提交 bug 报告 "知识库说 X 是 Y 但原文不是这样"
- review 速度跟不上 AI 抽取速度，staging 堆积

**Phase to address:**
**Phase 2 (Schema)** 定义字段；**Phase 3 (Demo 数据)** 演示 staging→canonical 流程；**Phase 5 (RAG 设计)** 在检索层做 provenance-aware 标注。

---

### Pitfall 3: Confidence 分数是猜的，不是校准的

**What goes wrong:**
每个实体都有 `confidence: 0.85` 字段，但这个数字是怎么来的？人工录入的 0.85 vs AI 抽取的 0.85 vs 多源一致的 0.85 完全不可比。下游用 confidence 做 ranking / filtering 时，相当于按噪声排序。AeroPower-RAG 时代用户已经吃过"伪 confidence"亏。

**Why it happens:**
- 字段定义时只写 `confidence: number 0..1`，没规定语义
- 不同录入者凭感觉打分
- AI 模型 self-report 的 confidence 直接抄进字段
- 没有 calibration 实验（confidence=0.9 的实体真实正确率是多少？）

**How to avoid:**
- `confidence` 拆成结构化对象：
  ```yaml
  confidence:
    score: 0.85
    rationale: "single_authoritative_source"  # 枚举：multi_source_agreement / single_authoritative_source / ai_extracted_unverified / expert_judgment / heuristic
    calibration_set: "v1_eval_2026Q2"        # 可选，校准集 ID
  ```
- 文档里写明每个 `rationale` 对应的语义和典型分数区间
- 至少有 1 个 calibration set（30–50 条手工标注金标），定期跑 confidence vs 真实正确率回归
- AI self-reported confidence 不直接采用，必须经过校准映射

**Warning signs:**
- 不同实体的 0.9 含义不同，问录入者也说不清
- confidence 分布异常集中（全是 0.8 或 0.9）
- 没有 calibration set
- 下游说"按 confidence 过滤效果不好"

**Phase to address:**
**Phase 2 (Schema)** 定义 rationale 枚举；**Phase 6 (路线图)** 列入"未来引入 calibration set"，**Phase 1 MVP 不强求做校准**，但 schema 必须留位。

---

### Pitfall 4: Schema 演进没有 migration 路径

**What goes wrong:**
Schema v1.0 用 `failure_modes`，v1.1 改成 `failure_mode_refs`。已存在的 100 条数据没自动迁移，部分 YAML 用新字段、部分用旧字段，CI 校验有的过有的不过。最终发现得手工改所有 YAML 才能修复 —— 在 200+ 实体规模下这是 1–2 天工作量。

**Why it happens:**
- schema 当代码改，没把数据当一等公民
- 没有 `schema_version` 字段 per-entity
- 没有 migration script 概念
- CHANGELOG 只记 schema 改了什么，没记数据怎么迁

**How to avoid:**
- 每个实体 YAML 顶部必填 `schema_version: "1.0.0"`（semver）
- schema 文件改 minor/major 时，必须同时提交 `migrations/v1.0_to_v1.1.py`（即使是空 op，也要有文件证明考虑过）
- CHANGELOG.md 每条 schema 变更包含：
  - 影响实体类型
  - 字段重命名/新增/删除清单
  - migration 脚本路径
  - 是否 breaking
- CI 检测：发现 entity 的 `schema_version` < 当前 schema 版本，必须有对应 migration 已跑过的证据（可以是 `migrations/applied.log`）
- breaking change 必须走双版本并行期：v1 reader 仍能读 v2 数据（至少 1 个 sprint）

**Warning signs:**
- schema 文件改了，CHANGELOG 只写"调整字段"
- 没有 `migrations/` 目录
- 不同实体的 `schema_version` 字段值不一致且没人解释
- CI 偶尔过偶尔挂，看起来跟新增数据有关

**Phase to address:**
**Phase 2 (Schema)** 设计阶段就必须把 `schema_version` 和 migration 流程写进去。**R6 已经显式要求 schema 版本管理**，这个 pitfall 在 R6 验收时必须被检查。

---

### Pitfall 5: 监管文献的"超期失效"链条断裂

**What goes wrong:**
FAA AC 25.1309-1A 被 -1B 取代，知识库里 -1A 的条款仍标记为 active，AI 回答时引用过时规章。在适航场景这是直接导致工程错误的事故级 bug。中国 CCAR / 欧洲 EASA CS 同号不同义，混用更危险。

**Why it happens:**
- `RegulationClause` 实体没有 `effective_date` / `superseded_by` / `jurisdiction` 必填字段
- 导入时只看文档标题，没追 supersession chain
- AI 不知道哪条是最新，看到哪条用哪条

**How to avoid:**
- `RegulationClause` schema 强制：
  ```yaml
  jurisdiction: "FAA" | "EASA" | "CAAC" | "MIL" | "ICAO"   # 必填，枚举
  document_number: "AC 25.1309-1B"
  effective_date: "1988-06-21"                             # 必填
  superseded_by: "AC 25.1309-1B"                           # null 或指向另一个 RegulationClause id
  status: "active" | "superseded" | "withdrawn"            # 必填
  ```
- 导入新规章时，CI 跑一个 `regulation_chain_validator`：发现同 `document_number` 不同 `jurisdiction` 必须显式 disambiguation；发现 superseded 链有循环或断点报错
- RAG retrieval 默认过滤 `status != active`，要查历史版本必须显式 query
- guardrail 在生成答案前检查引用条款的 `status`，非 active 必须警告

**Warning signs:**
- 两个 RegulationClause 实体 `document_number` 同字符串但 `jurisdiction` 不同（无 disambiguation 字段）
- AI 回答引用 `effective_date < 5 年前` 的 AC（aviation 行业大量 AC 在 5–10 年迭代）
- `superseded_by` 字段大量空缺
- 用户问"FAR 25.1309 现在最新版是什么"，AI 答 -1A

**Phase to address:**
**Phase 2 (Schema)** 必填字段；**Phase 3 (Demo 数据)** 至少 1 条覆盖 supersession 关系；**Phase 5 (RAG)** retrieval 层做 status 过滤。

---

### Pitfall 6: Chunking 策略破坏表格/公式（PDF 适航文档高发）

**What goes wrong:**
RAGFlow 默认按 token / 段落切 chunk，遇到适航文档常见的"表 25-1 失效模式与等级"或公式块，chunk 边界把表头和数据切开。检索时召回表头那一 chunk，但答案在数据 chunk 里，user 问"哪个失效模式属于 Catastrophic"得到"见表 25-1"这种废话。AeroPower-RAG 时代用户在中文 PDF 上踩过这坑。

**Why it happens:**
- 直接用默认 chunking，没针对航空文档的表格密集特点调
- 没在 ingestion 阶段做 PDF 结构识别（page/table/figure/section）
- 评估集没有"表格类问题"

**How to avoid:**
- RAGFlow ingestion 配置：开启表格识别（RAGFlow 文档明确支持），表格作为整体 chunk 不切割
- 公式块（含 `$$...$$` 或 LaTeX）作为整体 chunk
- chunking 策略写进 `R8 RAG Pipeline 设计文档`，明确：
  - 段落级 chunk size（建议 512–1024 token）
  - 重叠（overlap）大小
  - 结构化块（表格/公式/代码块）保留策略
- 评估集 ≥20% 的问题来自表格/公式
- 失败 case 入"chunking_failures.md" 知识库，作为后续优化输入

**Warning signs:**
- 检索 top-k 命中"见表 25-1"这种引用 chunk 但没有数据
- 用户问表格类问题，召回率明显低于段落类
- evaluation set 里没有表格类样例

**Phase to address:**
**Phase 5 (RAG Pipeline 设计)** —— `R8` 验收必须明确 chunking 策略 and 在 evaluation 设计里覆盖表格场景。

---

### Pitfall 7: Embedding 模型不识别中英航空术语

**What goes wrong:**
"涡轮"和 "turbine" 在 embedding 空间距离远，用户搜"涡轮叶片失效"召回不到英文 "turbine blade failure" 的 chunk。或反过来。AeroPower-RAG 时代用户已经为此打过仗（recall@3=100% 是流血换的）。

**Why it happens:**
- 默认用 RAGFlow 内置 embedding 模型（可能是 BGE-zh 或 nomic-embed-text），未必擅长中英 cross-lingual 航空术语
- 没有同义词扩展层
- 没建术语表（glossary）

**How to avoid:**
- 直接复用 AeroPower-RAG 已验证的方案：
  - 候选 embedding：`nomic-embed-text` (768d) / `bge-m3` (天然多语言) / `multilingual-e5-large`
  - 在 R8 文档里跑一次小规模对比（30 条中英对照 query），择优
- 引入 BM25 + 向量 + RRF（用户已有经验，直接复用）
- 维护 `data/glossary/aviation_terms.yaml`：
  ```yaml
  - canonical: turbine_blade
    zh: ["涡轮叶片", "涡轮工作叶片", "动叶"]
    en: ["turbine blade", "rotor blade"]
    ata_code: "72-30"
    notes: "区分 stator vane vs rotor blade"
  ```
- 检索前做 query expansion：term → synonyms (weight 0.3，承袭 AeroPower-RAG 配置)
- evaluation set 必须含中英对照 query（至少 ZH→EN 和 EN→ZH 各 10 条）

**Warning signs:**
- 中文 query 召回的全是中文 chunk，英文文档"消失"
- evaluation 跨语言召回率 < 70%
- 用户报告"我搜中文找不到，搜英文才找到"

**Phase to address:**
**Phase 5 (RAG)** —— R8 必须显式覆盖 cross-lingual 检索方案。

---

### Pitfall 8: Citation 注入幻觉（页码捏造）

**What goes wrong:**
LLM 生成回答时被 prompt 要求"必须给出 citation 含页码"。模型为了满足格式要求，**编造**页码（"见 FAR 25 第 47 页"），实际原文在第 52 页。这是 H-Darrieus Case 3 "捏造图表"的姊妹问题 —— 模型为了合规而幻觉。Core Value 直接失守。

**Why it happens:**
- prompt 让模型"自己写 citation"，没用程序化注入
- 检索结果传给 LLM 时丢失了 page/section 元数据
- 没有 post-generation 验证：模型说的 page 是不是真的在 retrieved chunk 的 metadata 里

**How to avoid:**
- **Citation 由系统注入，模型只能引用 retrieved chunk 的 ID**：
  - retrieval 返回 chunk 时附带 `chunk_id`
  - prompt 给模型的格式：`[CITE:chunk_id_xxx]`，模型不能自己写页码
  - 渲染层把 `[CITE:chunk_id_xxx]` 替换为真实的 (document, page, section, url)
- post-generation guardrail：扫描模型输出，所有 citation 必须能映射回某个 retrieved chunk_id；找不到 → 标红或 reject
- evaluation 集里加 "citation accuracy" 指标：抽样人工核对 citation 是否真的对应原文

**Warning signs:**
- 用户点开 citation，对照原文发现对不上
- citation 页码格式由模型自由生成而非模板替换
- guardrail 没有 "citation must resolve to retrieved chunk" 检查

**Phase to address:**
**Phase 5 (RAG Pipeline 设计)** —— R8 的 citation injection 章节必须说清"chunk_id 注入 + 渲染替换 + post-validation"流程。

---

### Pitfall 9: Guardrail 在检索失败时被绕过

**What goes wrong:**
用户问一个偏题问题（比如 "讲个笑话"），retrieval 返回 0 chunk 或全是低分 chunk。LLM 在没有 retrieved context 时**仍然生成答案**（用自己的世界知识），这答案没有 citation 可附，但 UI 已经渲染。用户看到一个看起来权威但其实毫无来源的航空答案。这是航空场景下最危险的失败模式。

**Why it happens:**
- guardrail 只在 "有 citation 但格式不对" 触发，不在 "检索失败" 触发
- retrieval threshold 没设
- "无答案" 回退路径没设计

**How to avoid:**
- retrieval threshold：top-1 score < T 或 top-k 全部 < T2 → 直接走 "no_context" 路径
- "no_context" 路径强制返回固定文案：
  > "知识库中未检索到相关内容。可能原因：(1) 您的问题不在当前知识库覆盖范围；(2) 关键词不匹配，请尝试换种问法。本系统不在无来源时生成答案。"
- guardrail 是 hard constraint：模型不论怎么 prompt，只要 retrieved_context 为空，pipeline 直接短路返回上述文案，不调 LLM
- evaluation set 必须包含 "out-of-scope query"（≥10 条），验证 100% 走 no_context 路径

**Warning signs:**
- 用户问无关问题，系统给出听起来合理但无 citation 的答案
- 日志里有 `retrieved_chunks=[]` 但 `response_generated=true` 的记录
- guardrail 配置里没有 "no context → fixed response" 分支

**Phase to address:**
**Phase 5 (RAG)** —— guardrail 设计必须在 R8 里独立成节，不是 retrieval 子项。

---

### Pitfall 10: Wiki.js 与 RAGFlow 内容失同步

**What goes wrong:**
工程师在 Wiki.js 编辑了一篇文档，RAGFlow 的向量索引没更新，AI 答案引用的还是旧版。或反过来：导入到 RAGFlow 的 PDF 没在 Wiki.js 有对应页面，user 在 Wiki 里搜不到。两边各说各话，"门户 vs 检索"的双系统问题。cfd-harness-unified 的 Notion/git dual-truth 经验直接对应 —— 必须有显式的 sync 协议和 truth source 决议。

**Why it happens:**
- Wiki.js 和 RAGFlow 把内容当各自的存储，没有统一 source
- 没定义谁是 truth source
- 索引重建是手动的、偶发的

**How to avoid:**
- 显式定义 truth source 层级：
  - **Tier 1 (canonical truth)**: Git 仓库里的 `docs/` 目录（Markdown）+ `data/` 目录（YAML）
  - **Tier 2 (rendered portal)**: Wiki.js 从 Git 同步（Wiki.js 有 Git storage backend，开启）
  - **Tier 3 (search/RAG index)**: RAGFlow 从 Git 同步（用 webhook 或 cron 重建）
- Git push hook → 触发两边的 re-ingest（CI job）
- ingestion 失败要在 dashboard 里 alarm，不是静默
- 文档头加 `last_synced` 字段（Wiki.js side） / `indexed_at`（RAGFlow side），和 Git commit hash 比对

**Warning signs:**
- Wiki.js 显示的内容和 Git HEAD 对不上
- RAGFlow 检索到的 chunk 内容是 1 周前的版本
- 没有 cron / webhook 触发 re-ingest 的证据

**Phase to address:**
**Phase 4 (部署方案)** —— R9 的 docker-compose 草案和架构图必须明确 sync flow（即使不实跑，方案要写清）。

---

### Pitfall 11: AI 接力上下文丢失（下一个 AI 不知道为什么这么设计）

**What goes wrong:**
6 个月后另一个 Claude/Codex 接手项目，发现 schema 里有奇怪字段（`legacy_ata_chapter_ref`），不知道是干嘛的，问用户也忘了。next AI 决定"清理掉"，结果是 3 个月前的关键 migration 字段。R12 直接对应这个问题 —— 用户已经识别到这是核心风险。

**Why it happens:**
- 决策没记录 rationale，只记录 outcome
- 隐式约定（"我们用 ENT-XXX 作 ID 前缀"）没写下来
- 文档假设"读者知道项目历史"

**How to avoid:**
- 每个设计文档强制 "AI 接力开发指南" 小节（R12 已要求），最少包含：
  - **目录结构**：每个目录是什么、不放什么
  - **命名约定**：实体 ID 格式、文件名格式、分支命名
  - **schema 版本号怎么读**：当前是多少、历史 breaking change 在哪
  - **术语表 / glossary**：项目特有词汇（如 "canonical promotion"）的定义
  - **未决项 (Open Questions)**：明确"目前没决定怎么处理 X"
  - **决策日志链接**：所有 ADR / Key Decisions 的入口
- 每个 schema 字段在 JSON Schema 里必须有 `description`（CI 检查空 description fail）
- 重大决策走 ADR (Architecture Decision Record)：背景 / 选项 / 选定 / rationale / consequences
- README 顶部一行: "如果你是 AI 接力来的，先读 `docs/ai-handoff-guide.md`"

**Warning signs:**
- 设计文档没有"如何接力"章节
- schema 字段 description 留空
- 决策只在 chat / commit message 里，没沉淀到文档
- 有人（人或 AI）问"为什么这么做"答不上来

**Phase to address:**
**Phase 1 (基线)** 设立目录约定；**所有 phase** 持续纪律，每个产出物 review 时检查 R12。

---

### Pitfall 12: 评估集（eval set）缺失，无法判断 RAG 是否退化

**What goes wrong:**
RAG pipeline 上线后改了 chunk size、换了 embedding、加了 reranker，每次都说"主观感觉变好了"。3 个月后某个改动让召回率从 90% 跌到 70%，没人知道，直到用户投诉才发现。AeroPower-RAG 时代用户已知这是底线。

**Why it happens:**
- 评估集做起来烦，常被推迟
- 没把"通过 eval"做成 gate
- eval 数据是开发者自己造的，bias 严重

**How to avoid:**
- Phase 5 R8 验收必须包含一个 ≥30 条的初版 eval set，结构：
  ```yaml
  - query: "FAR 25.1309 关于 catastrophic 的定义？"
    query_lang: zh
    expected_chunks: ["chunk_id_a", "chunk_id_b"]   # 至少一个必须召回
    expected_answer_keywords: ["unable to continue safe flight", "灾难性"]
    expected_citations: ["DOC-FAA-FAR25-2024", "AC 25.1309-1B"]
    category: "regulation_definition"  # 用于按类别看 recall
  ```
- 类别覆盖：regulation_definition / failure_mode_lookup / cfd_method / cross_lingual / table_query / out_of_scope（每类 ≥3 条）
- CI 跑 eval：recall@3 / mrr / citation_accuracy 三个指标，回归就 fail PR
- eval set 在 Phase 1 demo 数据里就开始攒，不要等 Phase 5

**Warning signs:**
- 没有 `evaluation/` 目录
- "改了一下检索"但没说改前改后指标
- pipeline 升级 3 次都没回归测试

**Phase to address:**
**Phase 3 (Demo 数据)** 开始攒 ≥10 条；**Phase 5 (RAG)** 扩到 ≥30 条并接入 CI；**Phase 6 路线图** 列入"扩到 100+"作为后续目标。

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| YAML 里 `source: "FAR 25"` 字符串 | demo 快 1 小时 | Pitfall 1 全套 | **Never** —— Core Value 直接违反 |
| `confidence: 0.85` 不带 rationale | schema 简单 | Pitfall 3，下游不可比 | MVP demo 可接受 1 周，必须 Phase 2 末修 |
| schema 改了不写 migration | 改起来快 | Pitfall 4，数据漂移 | **Never**（migration 可以是空 op，但文件必须在）|
| AI 抽取直接进 canonical | 数据增长快 | Pitfall 2，Core Value 失守 | **Never** |
| 不做 eval set | 上线快 | Pitfall 12，盲飞 | MVP 第 1 周可缓，Phase 3 必须有 ≥10 条 |
| Wiki.js 内容不从 Git 同步 | 编辑顺手 | Pitfall 10，双 truth | **Never** —— Git 必须是 SSOT |
| 不写 ADR | 推进快 | Pitfall 11，AI 接力崩 | 小决策可省，schema/部署/RAG 关键决策 **Never** |
| Embedding 用默认不评估 | 配置简单 | Pitfall 7，cross-lingual 召回崩 | **Never** —— Phase 5 必须有 30 条 cross-lingual eval |
| Citation 让 LLM 自己写 | prompt 简单 | Pitfall 8，Core Value 失守 | **Never** |
| Guardrail 不检查 no-context | pipeline 简单 | Pitfall 9，无源回答 | **Never** |
| docker-compose 不写网络拓扑 | 文档短 | 部署阶段返工，Wiki/RAGFlow 联通问题 | 可以，但架构图必须有 |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Wiki.js storage | 用 PostgreSQL local store，不接 Git | 配置 Git Storage Module，repo 是 SSOT，Wiki.js 是 renderer |
| RAGFlow ingestion | 把整个 docs/ 目录扔进去，不分类 | 按 document type 分 dataset（regulations / cfd_papers / project_notes），每个 dataset 独立 chunking 配置 |
| RAGFlow embedding model | 用默认中文模型，不评估 cross-lingual | Phase 5 跑对比实验，候选：bge-m3 / multilingual-e5-large / nomic-embed-text |
| Wiki.js + RAGFlow auth | 两套独立账户，密码各管各 | Phase 4 方案文档必须涵盖：option A 反代+SSO；option B 单组织内部信任，不暴露公网；option C 后续接入 Authentik/Keycloak。MVP 选 B |
| RAGFlow upgrade | minor 版本就在生产升级，不测向量兼容 | 升级前 dump 一个 sample query 集，升后跑 diff；vector store schema 变化要走数据迁移脚本 |
| Git LFS 决策 | 直接 commit PDF，repo 涨到 GB | Phase 1 就开 Git LFS for `*.pdf`、`*.docx`、`*.zip`；非 LFS commit 在 pre-commit 拦截 |
| RAGFlow citation 元数据 | 默认配置只存 chunk text，丢 page/section | ingestion 配置显式保留 source metadata（RAGFlow 文档明确支持），rendering 时回填 |
| docker-compose volumes | named volume + bind mount 混用 | 按用途分：`db_data` (named) / `uploads` (bind to host path) / `vector_store` (named, backed up separately) |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| 单个 YAML 文件含全部实体 | git diff 慢，merge conflict 多 | 一个实体一个文件：`data/canonical/components/COMP-XXX.yaml` | ~500 实体 / 单文件 |
| Git 仓库塞满 PDF 不开 LFS | clone 慢、CI 拉取超时 | 第 1 个 PDF 进仓库前就开 LFS（`.gitattributes` 配好） | repo > 1 GB |
| RAGFlow 向量库放在容器内部 | 容器重建数据丢、不可备份 | volume 挂载到 host path，独立备份 | 重启容器即触发 |
| 全量 re-index every push | CI 跑 30+ 分钟 | 增量 ingest：webhook 只 reindex 变更文件 | 文档总数 > 100 |
| 评估集在 CI 里跑全量 LLM call | CI 费用 / 时间爆炸 | 分两层：retrieval-only eval (无 LLM) 每 PR 跑；end-to-end eval (含 LLM) 每天跑或 nightly | eval > 50 条 |
| YAML 校验单文件 schema lookup | CI 慢 | 用 `ajv` 等支持 schema bundle 的工具，一次加载 | 实体 > 1000 |
| Wiki.js 全文搜索覆盖 RAGFlow 已索引内容 | 用户混淆"门户搜索 vs Q&A" | UI 显式区分两个入口；或 Wiki.js 搜索结果列表里附"想问 AI?"按钮跳 RAGFlow | 始终 |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| ITAR/EAR 受控内容入 KB 没分级 | 法律风险，出口管制违规 | 每个 Document 必填 `confidentiality: public / internal / restricted / itar_ear`；`itar_ear` 实体 RAG 检索默认排除，必须显式有授权 |
| 公开版 Wiki.js 暴露内部规章原文 | 版权 / 合规问题 | Phase 4 部署方案明确：MVP 不公网；公网部署须先过 confidentiality 审核 |
| RAGFlow API key 硬编码在 docker-compose | 凭证泄露 | `.env` + `.gitignore`；`docker-compose.yml` 用 `${RAGFLOW_API_KEY}` 引用 |
| 用户上传 PDF 不扫描 | 恶意 PDF（含 JS / 嵌入恶意载荷）打穿 ingest | ingest pipeline 第一步 `clamav` 或同等扫描；可疑文件隔离 |
| 内部账号默认弱口令（admin/admin） | 横向移动 | Phase 4 部署文档明确"首次启动必须改密码"；docker-compose 用初始 random password 注入 |
| AI 抽取的实体含 PII（人员姓名、电话） | 隐私泄露 | provenance pipeline 加 PII scrubber（regex + NER），canonical 数据禁含 |
| audit log 不开 | 不可审计，违反 R12 / 工业软件交付要求 | Wiki.js 和 RAGFlow 都开 audit log，落到独立 volume，retention ≥ 1 年 |
| 跨 jurisdiction 数据混存（ITAR + 中国 GB） | 合规交叉违规 | 不同 jurisdiction 数据分 dataset，访问策略独立 |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| 门户搜索和 RAG Q&A 是两个入口 | 用户不知道用哪个 | 统一搜索框，后端先全文匹配，无命中或显式"问 AI"再走 RAG |
| Citation 显示成"Doc XYZ" 不可点 | 用户验证不了 | citation 必须可点，跳到 Wiki.js 对应章节或 PDF 对应页 |
| 检索失败时返回模型自由生成 | 用户被骗 | Pitfall 9 的 fixed response，明确"未检索到" |
| Confidence 直接显示数字（0.73） | 用户不知道意思 | 用语义 badge："高 / 中 / 低" + tooltip 说明 rationale |
| 中英混合 query 表现差但无提示 | 用户怪系统笨 | 检测到混合语言时建议"试试纯中文/英文重问" |
| AI 抽取内容和人工内容外观一致 | 用户当权威用 | UI 显著标记：⚠️ 黄色 banner "本条 80% 字段来自 AI 抽取，未经人工审核" |
| 没有 "feedback / 报错" 入口 | 错误无法收集 | 每个回答下"标记错误"按钮，回流到 staging issues |

---

## "Looks Done But Isn't" Checklist

- [ ] **R3 Schema 设计：** 常缺 `provenance.method` 枚举严格化、`schema_version` 必填、字段 `description` 非空 — 验证：用一份带异常字段的 YAML 跑 CI，是否 fail
- [ ] **R5 Confidence/Provenance：** 常缺 calibration 设计 / staging→canonical 流程文档 — 验证：能否从文档读出"AI 抽取的实体如何变成 canonical"步骤
- [ ] **R6 Schema 版本管理：** 常缺 migration 脚本目录 / breaking change 流程 — 验证：`migrations/` 目录是否存在、CHANGELOG 是否覆盖至少 1 个示例
- [ ] **R7 文档元数据：** 常缺 `confidentiality` 枚举、`content_hash` 字段 — 验证：导入 1 个文档，必填字段全填齐
- [ ] **R8 RAG Pipeline：** 常缺 chunking 表格策略 / cross-lingual 评估方案 / no-context guardrail / citation 注入流程 — 验证：文档目录是否覆盖这 4 节
- [ ] **R9 部署方案：** 常缺 sync flow（Git→Wiki.js / Git→RAGFlow）/ 备份方案 / 升级路径 — 验证：架构图是否含 3 条 sync 箭头 + 备份目标
- [ ] **R10 Demo 数据：** 常缺 supersession 关系样例 / `provenance.method: ai_extracted` 样例 / 表格类样例 — 验证：枚举所有样例，按 17 类型 + 关键场景过一遍
- [ ] **R11 路线图：** 常缺触发条件 / 依赖项；只列阶段名 — 验证：每阶段是否有"何时启动 / 依赖什么 / 何时算完"
- [ ] **R12 AI 接力指南：** 常缺术语表 / 未决项 / 决策日志链接 — 验证：陌生人测试 — 找一个没看过项目的人 5 分钟能否复述目录结构和当前阻塞
- [ ] **CI 占位 (R1)：** 常只有 lint 没有 schema validation — 验证：故意提交一个不合 schema 的 YAML，CI 是否拒绝
- [ ] **Citation 链路：** 常未做 chunk_id 注入 → 渲染替换 → post-validation 三步 — 验证：用一个测试 query，看输出 citation 是否能 100% 映射回 retrieved chunks
- [ ] **Eval set：** 常没有 out-of-scope category — 验证：eval set 里有 ≥3 条故意问无关问题，全部走 no_context 路径

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| P1 source 是自由文本 | MEDIUM (~实体数 × 5min) | 写一次性 migration 把 string source 解析尝试 → 解析不出的标 `needs_review` → 人工补全 |
| P2 AI 抽取已进 canonical | HIGH | 全量审计 `provenance.method`；不能确认人工审过的全部退回 staging；公布"过去 X 月数据需重新审核"通告 |
| P3 confidence 不可比 | LOW | 加 `rationale` 字段，default `legacy_unspecified`；新数据强制填，旧数据逐步补 |
| P4 schema 没 migration | HIGH | 临时容忍多版本并存，写 lazy migrator (read time 升级)，下个 sprint 全量批跑 |
| P5 监管失效链断 | MEDIUM | 跑 `regulation_chain_validator` 全量，输出 broken chain 列表；按 jurisdiction 分配 review |
| P6 chunking 破坏表格 | MEDIUM | 调整 RAGFlow ingestion 配置，全量 re-ingest；老 chunk 标 `deprecated` |
| P7 cross-lingual 召回差 | MEDIUM | 切换 embedding 模型 + 引入 glossary expansion；re-index；eval 验证 |
| P8 citation 幻觉 | MEDIUM | 改 prompt 模板用 chunk_id 注入；上线 post-validation；存量回答标"待重新生成" |
| P9 guardrail 绕过 | LOW | 加 retrieval threshold + no_context branch；redeploy |
| P10 Wiki/RAGFlow 失同步 | MEDIUM | 强制 Git → 双向 re-ingest；建 sync dashboard |
| P11 AI 接力上下文丢 | HIGH | 紧急写 ai-handoff-guide；遍历近 N 个决策补 ADR；下次接力前必读 |
| P12 没 eval set | LOW | 用现有 demo 数据手工标 30 条；接 CI |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| P1 来源自由文本 | **Phase 2** (Schema) | CI 用反例 YAML 验证拒绝；R3 验收 demo |
| P2 AI 抽取直进 canonical | **Phase 2** + **Phase 3** | staging/ 目录存在；canonical 里 grep `ai_extracted` 为空 |
| P3 confidence 不校准 | **Phase 2** (字段定义) + **Phase 6** (路线图列校准任务) | rationale 枚举写进 schema；calibration_set 字段存在 |
| P4 schema 无 migration | **Phase 2** (R6 验收时强制) | `migrations/` 目录 + CHANGELOG 含示例 |
| P5 监管失效链 | **Phase 2** (字段) + **Phase 3** (demo 含 supersession 样例) + **Phase 5** (retrieval 过滤) | demo 数据有 superseded 样例；retrieval 默认过滤 status |
| P6 chunking 破表格 | **Phase 5** (R8) | RAG 设计文档显式覆盖；eval 含表格类 query |
| P7 cross-lingual 召回 | **Phase 5** (R8) | embedding 选型对比文档；eval 含 ZH↔EN |
| P8 citation 幻觉 | **Phase 5** (R8) | citation 注入流程文档化；guardrail 含 post-validation |
| P9 guardrail 绕过 | **Phase 5** (R8) | retrieval threshold + no_context branch 文档化 |
| P10 Wiki/RAGFlow 失同步 | **Phase 4** (R9) | 架构图含 sync 箭头；docker-compose 草案含 webhook/cron 占位 |
| P11 AI 接力丢失 | **Phase 1** + **持续** | 每个产出物含 R12 章节 (CI 检查) |
| P12 无 eval set | **Phase 3** (≥10) + **Phase 5** (≥30) | `evaluation/` 目录有 yaml；CI 跑 retrieval-only eval |

---

## Sources

- **User's prior projects (HIGH confidence — first-hand)**:
  - AeroPower-RAG: hybrid retrieval (BM25+vector+RRF), recall@3=100%, cross-lingual ZH↔EN, Ollama nomic-embed-text 768d 已验证
  - cfd-harness-unified: Notion/git dual-truth pattern, audit trail discipline, RETRO-V61-001 risk-tier triggers
  - cfd-ai-workbench Case 3 (H-Darrieus): "捏造图表" 教训直接对应 Pitfalls 2 / 8 / 9
  - cfd-ai-workbench AI 过程可审计性 guidance：industrial software delivery requires full audit trail
- **Project context (HIGH)**: `.planning/PROJECT.md` Core Value、R1–R12 Active requirements、Out-of-Scope 边界、Key Decisions
- **General RAG / aviation domain knowledge (MEDIUM, training-data-based)**:
  - RAGFlow PDF parsing / table preservation features (官方文档可查证；Phase 5 实施前应用 Context7 / WebFetch 二次确认)
  - Wiki.js Git Storage Module (官方功能；Phase 4 实施前确认当前版本兼容性)
  - FAA AC supersession chain pattern (FAA 公开规则)
  - ITAR/EAR 受控物项规则 (US 出口管制公开法规)
  - JSON Schema validation tools (ajv 等)
- **MEDIUM confidence flags**:
  - 具体 embedding 模型在中英航空文献的相对表现 (建议 Phase 5 实跑对比验证，不要直接信)
  - RAGFlow 当前版本对表格 chunk 的支持程度 (建议 Phase 5 实施前 verify with Context7 / official docs)
  - Wiki.js + RAGFlow 升级兼容性 (没有公开矩阵，需用户长期维护)

---
*Pitfalls research for: Aviation Knowledge Base MVP (Wiki.js + RAGFlow + YAML/JSON Schema + Git)*
*Researched: 2026-05-03*
