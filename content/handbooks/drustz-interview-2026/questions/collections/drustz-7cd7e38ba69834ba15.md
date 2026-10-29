---
id: drustz-7cd7e38ba69834ba15
section: collections
order: 24
level: A
title: Google DeepMind 题库（爬取全量） · ML System Design
quick: 作者文档章节 · Google DeepMind 题库（爬取全量） · ML System Design
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/gdm.md
    type: primary
---
## ML System Design

### IGotAnOffer ML design round: system-design-style but ML-first; constraints added iteratively; justify from first principles
*hard · 频率: high (multiple reports agree this is the hardest round) · 2025*

After the fundamentals round, RE candidates face one or more ML design interviews — 'the heart of the technical loop... regularly described as the hardest part of the process.' Format: like system design in that you outline a high-level approach, but you must develop a machine-learning solution and walk the full pipeline: data collection, preprocessing, model architecture, training, evaluation, deployment. Interviewers iteratively add constraints (Blind report: 7-8 constraints layered over each of 7-8 techniques discussed). You must justify every decision from first principles: if you choose a particular loss function, optimizer, or architecture, expect to explain why it's the right call. Related ML-aware design prompts circulating in prep material: 'Design a serving system for a 100B-parameter model at scale', 'Build an evaluation pipeline that runs thousands of benchmarks nightly', 'Design a feature store for an ML experimentation platform'.

**解法**: Practice the constraint-escalation game: take any design (recsys, LLM serving, eval pipeline) and re-solve under: 10x less labeled data → weak supervision/synthetic data; strict latency → distillation/quantization/caching; distribution shift → monitoring + continual finetuning; no user feedback → offline eval + proxy metrics. Always tie back to the objective/loss. (my inference)

来源: &lt;[来源链接](https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview&gt;)

### Applied AI Engineer 面试大纲（recruiter 官方给出，Blind 2025-09）
*hard · 频率: single report（但为 recruiter 官方大纲，可信度高） · 2025-09-30*

GDM Applied AI Engineer，recruiter 明确列出 ML system design 考察范围：1) System Architecture：high-level model choice, designing for scale；2) Retrieval (RAG)：factuality, grounding, implementation；3) Efficiency：quantization, distillation, optimization；4) Agent Frameworks：LangChain, LangGraph 等；5) Evaluation：aligning evals with problem formulation。楼主追问三点：设计题是否聚焦大规模生成式 AI（code assistant、RAG 系统）；“ML Debugging”轮的 bug 是什么样（社区共识：bugs are stupid, not hard）；理论 ML vs 分布式系统工程的比重。评论建议：“通常是 transformer based……读 ML system design 和 GenAI system design 教科书”。

**解法**: ML debugging 轮备考：练习找“蠢 bug”——张量 shape/broadcast 错误、softmax 维度错、CrossEntropyLoss 前多加 softmax、忘 zero_grad、dataloader 没 shuffle、train/eval 模式混用。

来源: &lt;[来源链接](https://www.teamblind.com/post/deepmind-applied-ai-engineer-interview-ml-system-design-deep-dive-j5n8qh3k&gt;)

### Google/DeepMind · ML System Design 题（Bot Detection + Address Autofill）
*medium · 频率: medium — Google 频率：Design A Bot Detection System 7(Onsite)、Design An Address Autofill System 4(Onsite) · 2026-02 至 2026-03*

Google 页面下仅有的 2 道 ML System Design（Onsite，正文需登录；practice URL .../google/ml-system-design/{id}/practice）：(1) Design A Bot Detection System [Medium, id 69f67e5830f41dfd539fbf82, companyFreq Google=7/Amazon=5]：区分真人流量与自动化 bot 的 ML 系统。(2) Design An Address Autofill System [Medium, id 6a094f91c84b6e8a3be17ce4, companyFreq Google=4/Amazon=4/Uber=6]：地址自动补全。这是站内 ML System Design track（较新上线）中与 Google 关联的题。

**解法**: （我的推断）Bot Detection 应覆盖：特征工程（行为/设备指纹/频率）、在线 vs 离线特征、标签获取与延迟反馈、对抗性演化下的模型再训练、精度/召回与误伤权衡、实时低延迟打分。Address Autofill：候选生成（Trie/倒排 + geo）+ 排序模型（学习排序）、个性化、拼写纠错、延迟预算。对该候选人的 post-training/数据管线经验是加分点。

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/google/ml-system-design&gt;)

### techinterview.org 2026: RE track rounds — distributed training design and evaluation infrastructure design
*hard · 频率: prep-site synthesis (unverified but consistent with candidate reports) · 2026*

Research Engineer loop per same guide: (1) ML coding, 60 min — larger pipeline implementation pieces than the RS version. (2) Distributed training systems design, 60 min — design a training system for models exceeding single-accelerator capacity; expected topics: data/pipeline/tensor parallelism, ZeRO, DeepSpeed-style optimizations. (3) Evaluation infrastructure, 60 min — design an evaluation harness for a frontier model across many benchmarks; must address test-set contamination and reproducibility. (4) Standard coding, 60 min — medium-to-hard algorithmic problem, 'often unaided'; talk through approach and complexity out loud BEFORE typing. (5) Behavioral — collaboration in research teams, shifting priorities under research uncertainty, end-to-end ownership. Prep guidance: study Megatron/DeepSpeed/FSDP, build eval-harness design skills, practice ML coding without AI tools.

**解法**: Distributed training answer skeleton: memory math (params+grads+optimizer states ≈ 16 bytes/param for Adam mixed precision), then DP→ZeRO stages→TP within node→PP across nodes→activation checkpointing; interconnect-aware placement; failure recovery via checkpointing. Eval harness: versioned datasets, hermetic runs, seed control, contamination detection (n-gram/embedding overlap), CI-style nightly runs with regression alerts. (my inference)

来源: &lt;[来源链接](https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/&gt;)

### r/MachineLearning 2025-04: Gemini team ML system design — insider + coach guidance (sharding, KV cache, quantization, MoE)
*hard · 频率: single thread with insider + coach corroboration · 2025-04*

Thread by a candidate interviewing with the Gemini team for LLM system design. A self-identified DeepMind employee replied: for system design look at 'zero-1, zero-3 and megatron', linking the EEML tensor-parallelism tutorial (github.com/eemlcommunity/PracticalSessions2023/tree/main/tensor_parallelism); for culture fit, be collaborative and don't say anything offensive (people genuinely fail this); ask recruiter for Google mock interviews. An interview coach added, based on multiple Gemini-team candidates: ML system design differs from SWE system design — heavy focus on throughput, memory constraints, and latency tradeoffs specific to LLM deployments; be ready to discuss sharding strategies, KV cache optimization, quantization techniques; read up on MoE architecture (Gemini Ultra uses it); brush up distributed training (FSDP, DeepSpeed); read 'Transformer Inference Arithmetic'; articulate tradeoffs (precision vs latency, model size vs perf). Behavioral: prepare examples showing rapid progress amid ambiguity — 'apparently a big thing for them'; team moves very fast, values collaborative problem solving over solo brilliance.

**解法**: Core LLM-serving numbers to know: KV cache size = 2·layers·kv_heads·head_dim·bytes·seq_len per sequence; batching (continuous batching), paged attention, speculative decoding, quantization (int8/int4, AWQ/GPTQ), distillation. For training: ZeRO stage tradeoffs, TP communication cost (all-reduce per layer) vs PP bubble.

来源: &lt;[来源链接](https://old.reddit.com/r/MachineLearning/comments/1k8gy12/d_preparing_for_a_deepmind_gemini_team_interview/&gt;)

### Blind 2025-09: Applied AI Engineer loop — recruiter-listed ML system design focus areas (RAG, efficiency, agents, evals)
*hard · 频率: single report · 2025-09*

Candidate preparing for GDM Applied AI Engineer ML system design round shared the recruiter's stated focus points verbatim: (1) System Architecture: 'high-level model choice, designing for scale'; (2) Retrieval (RAG): 'factuality, grounding, implementation'; (3) Efficiency: 'quantization, distillation, optimization'; (4) Agent Frameworks: 'LangChain, LangGraph, etc.'; (5) Evaluation: 'aligning evals with problem formulation.' OP asked whether design problems center on large-scale generative AI systems (code assistants, RAG), expected depth on vector DBs and prompt orchestration, ML debugging round bug types (convergence issues, data leaks), and theory-vs-distributed-systems balance — no insider answers in comments, but the recruiter list itself is the signal.

**解法**: Design template for GDM applied rounds: problem formulation → model choice (API LLM vs finetuned vs distilled) → RAG pipeline (chunking, embeddings, hybrid retrieval, reranking, grounded generation with citations) → eval design FIRST-CLASS (offline evals aligned to task, LLM-judge with human calibration, regression suites) → efficiency levers (quantization, distillation, caching) → agent orchestration and failure handling. (my inference)

来源: &lt;[来源链接](https://www.teamblind.com/post/deepmind-applied-ai-engineer-interview-ml-system-design-deep-dive-j5n8qh3k&gt;)

### GDM RE 流程中的 ML Design 轮（2022 新增，地里公认无具体面筋）
*unknown · 频率: single report · 2022-10*

《Deepmind ML Design》2022-10-22。原文："楼主正在面deepmind的re，貌似会有一轮ml design，有没有朋友能指点一下他们大致会怎么面吗？地里好像没太有具体的面筋：（"。确认 2022 起 RE loop 含 ML design 轮，且 1p3a 上没有该轮的具体题目沉淀。可参照 825115 的遥测信号题风格：给一个实际业务/研究场景让你端到端设计 ML 方案。

**解法**: 我的推断：GDM 的 ML design 更偏 research-flavored（如何设计实验/训练方案/评估），不是 Meta 式推荐系统八股。按『问题定义→数据→模型选型与 scaling 考量→训练与评估→迭代』框架，主动讨论 ablation 和 failure mode 会加分。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-938855-1-1.html&gt;)

### techinterview.org 2026：Research Engineer track——分布式训练与评测基础设施设计轮
*hard · 频率: 聚合指南 · 2026*

RE 4-5 轮：1) ML Coding 60min（比 RS 版更工程化——实现更大的 pipeline 片段）；2) Distributed Training Systems Design 60min：为多加速器大模型设计训练系统，考 pipeline parallelism、tensor parallelism、ZeRO、DeepSpeed 式优化；3) Evaluation Infrastructure 60min：设计跨 benchmark 的评测 harness，必须处理 test set contamination 和 reproducibility；4) 标准算法 coding（medium-hard，与普通工程 loop 同一 bar）；5) Behavioral：与研究团队协作、优先级在不确定性下的切换。备考建议原文：“distributed training systems (Megatron, DeepSpeed, FSDP), evaluation harnesses, ML coding without AI tools”。

**解法**: 评测 harness 设计要点：版本化数据集+prompt 模板、n-gram/embedding 去污染检测、固定 seed+温度记录、并行调度与缓存、人工/LLM-judge calibration——正中候选人 Reflection.ai 数据管线经验，可主动映射。

来源: &lt;[来源链接](https://www.techinterview.org/post/3233474918/deepmind-interview-process-2026/&gt;)

### ML design 轮真题四道（IGotAnOffer verbatim）
*hard · 频率: 聚合（多条报告） · 2026-06*

RE ML design 轮（被普遍称为整个 loop 最难）真题：1) How would you build, train, and deploy a system that detects if multimedia and/or ad content violates terms or contains offensive materials?（多模态内容审核系统全链路）；2) Design autocomplete and/or spell check on a mobile device（端侧约束）；3) Design autocomplete and/or automatic responses for email（Smart Compose/Smart Reply）；4) Design the YouTube recommendation system。要求从第一性原理为 loss/optimizer/架构选择辩护，讲清 pipeline：数据收集→预处理→模型→训练→部署→评测。

**解法**: 每题按：需求/约束澄清 → 指标（在线+离线）→ 数据与标注 → baseline→ 模型迭代（说明 trade-off）→ serving（延迟/端侧量化）→ 监控与反馈回路。移动端题要主动谈模型压缩（distillation/量化/剪枝）。

来源: &lt;[来源链接](https://igotanoffer.com/en/advice/google-deepmind-research-engineer-interview#q3&gt;)

### Applied AI Research Manager onsite：coding + ML Design + Applied Fundamental ML（Blind 2025-09）
*hard · 频率: single report · 2025-09-07*

Meta Ads Ranking 背景候选人报告 GDM Applied AI research manager onsite 构成：coding 面（bar 类似 Google/Meta）、ML Design 轮、Applied Fundamental ML 轮。其焦虑点是被要求“design an LLM based system end to end”而自己缺 LLM 系统设计实战。Google 员工建议：“Practice designing popular LLM products”（练习设计主流 LLM 产品）。

**解法**: 准备 3-4 个端到端 LLM 产品设计模板：RAG 问答/企业搜索、代码助手、聊天助手（含安全护栏）、Agent 工作流，每个含数据飞轮与评测方案。

来源: &lt;[来源链接](https://www.teamblind.com/post/what-to-expect-for-deepmind-applied-ai-research-manager-interview-os1sve2c&gt;)

### DeepMind ML Design 面: 化学分子反应预测建模 (2025-08)
*medium · 频率: 1 (2025-08 同一套 GDM ML 面) · 2025-08*

岗位: DeepMind ML Engineering, ML Design/建模 视频面 (伦敦小哥面试官, 友好)。题目: 有一个 chemistry molecule dataset, 数据形式为 (molecule1_name, molecule2_name, reaction factor)。要求建模预测 reaction factor。英文摘要点明期望方向: EDA techniques + transformer models ('molecule reaction prediction using transformer models and EDA techniques')。开放式 ML 建模讨论，从数据探索到特征化到模型选择到评测。

**解法**: 推断解题框架: (1) EDA: 分子名分布/去重/reaction factor 分布(是否长尾/需 log 变换)、数据泄漏(molecule pair 对称性)检查; (2) 特征化: 把 molecule_name 转成结构表示 (SMILES tokenize / 指纹 Morgan fingerprint / 学习 embedding); (3) 模型: 分子对 -> transformer/GNN 编码后回归 reaction factor, 或对称双塔; (4) 评测: RMSE/MAE, 按分子 scaffold split 防泄漏, 交叉验证; (5) 讨论冷启动/未见分子泛化。

来源: &lt;[来源链接](https://www.1point3acres.com/bbs/thread-1141657-1-1.html&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/gdm.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/gdm.md)。作者整理资料；许可和第三方来源范围见阅读指南。
