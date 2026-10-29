---
id: drustz-fbbd841e4ebfe99434
section: mlsd
order: 70
level: A
title: 09 · ML System Design 题库 · E. Search / Exa 类系统（14 题）
quick: 作者文档章节 · 09 · ML System Design 题库 · E. Search / Exa 类系统（14 题）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/09_question_bank.md
    type: primary
---
## E. Search / Exa 类系统（14 题）

### E1. 训练一个 web search retriever，用什么数据？

答题锚点：query-doc clicks with debias、expert relevance、synthetic queries、anchor/citation pairs、hard negatives、freshness/source quality；query/time/domain split。

### E2. Retriever、reranker、answerer 分别怎么训？

答题锚点：dual-encoder contrastive、cross-encoder pair/listwise、answer SFT/preference/grounded outcome；每层 labels/metrics 不同。

### E3. 如何 post-train 一个多步 search agent？

答题锚点：demonstration trajectories + tool protocol SFT；outcome/evidence/cost reward；retrieved-token masking/trajectory credit；RL 只在环境与 verifier 可靠时。

### E4. 最终答案正确是否足够？

答题锚点：可能猜对/记住；要求 claim-level evidence、citation precision/recall、source authority/freshness、coverage、trajectory cost；counterfactual evidence tests。

### E5. Hard-negative mining 有什么坑？

答题锚点：top results 中有 unlabeled relevant docs，误当负例；pooling/adjudication、multi-positive/soft labels、refresh negatives；sampling 与 serving 一致。

### E6. Search freshness 如何进入训练和 eval？

答题锚点：crawl/index staleness SLO、time-aware features/labels、post-cutoff queries、source update events、freshness guardrail；模型知识不替代 current index。

### E7. 线上 CTR 上升但满意度下降，可能为什么？

答题锚点：clickbait/position bias、reformulation、dwell/task completion、答案让用户无需点击、latency；A/B + long-term guardrails。

---

**E8–E14 是为 Exa 第二轮（systems design，面试官做 reranking / snippet / alignment）补的。完整答案在 [20_case_exa_agentic_search.md](?book=drustz-interview-2026&section=mlsd&question=drustz-c5c2d47cc34774481f)。**

### E8. 设计一个 snippet / highlight 服务：给 (query, 一批网页) 返回最相关片段，p99 < 100ms。

答题锚点：目标是 **answer-in-context recall @ token budget**（groundedness），不是可读性；
切块 → 打分 → **预算约束下的子集选择**（不是 top-k）→ 拼装；
阶梯 bi-encoder（已索引文档 chunk embedding **预计算**）→ 小 cross-encoder（只跑 shortlist）→ span-level；
生成式出局（超预算 + hallucination + 不可引用）；
**算术**：`FLOPs ≈ 2·params·tokens`，100M encoder × 80k token ≈ 16 TFLOP ≈ 53ms；
p99 杀手是超长文档 → 分级路由 + 带 deadline 的降级 + **降级要打点**。→ [20 §3](?book=drustz-interview-2026&section=mlsd&question=drustz-c5c2d47cc34774481f)

### E9. 给 agent 用的 reranker 和给人用的有什么不同？

答题锚点：agent 把 5–10 条**全部**读进 context → **位置折扣基本不适用**，应优化 **set-level 覆盖 + 去冗余**（α-nDCG / set recall），不是 pointwise nDCG；
冗余是实打实的 context 成本；失败代价是 **agent 多搜一轮**（延迟 ×N、成本 ×N）；
没有 click，隐式信号只有「是否被引用 / 是否终止搜索 / 最终是否答对」，归因要用 **leave-one-out 反事实**；
query 分布是 agent 生成的（更长、带约束），**必须用真实 agent query 训和评**。→ [20 §4.1/4.4](?book=drustz-interview-2026&section=mlsd&question=drustz-c5c2d47cc34774481f)

### E10. 延迟预算 100ms、QPS 500，reranker 能重排多少候选？要多少卡？

答题锚点：`FLOPs = 2 × params × tokens`；100M 参数 × 512 token × N 个候选，30ms、H100 有效 300 TFLOP/s → **N ≈ 90**；
→ **候选数是算出来的，不是拍的**；1B 的 cross-encoder 直接出局 → web-scale reranker 的真实约束是「100M 参数内榨干质量」→ **distillation**；
容量：500 QPS × 30ms = **15 GPU-秒/秒 → 25–30 张卡**（含余量）；
降本三条：late interaction（doc 向量离线算，存储爆炸 → 量化）／文档侧截断（**先用 highlights 挑 256 token 再喂 reranker**）／蒸到更小。→ [20 §4.3](?book=drustz-interview-2026&section=mlsd&question=drustz-c5c2d47cc34774481f)

### E11. 检索质量如何影响 RL 训练的样本效率？

答题锚点：检索好 → rollout 里「结果直接含答案」比例↑ → 成功轨迹密度↑ → 有效梯度↑；
**GRPO 特有的超线性**：组内normalization优势，一组 rollout 全错则优势全 0、整组算力浪费 —— 检索质量把「零信号组」变成「有信号组」；
Exa 实测：达同等水平少 **69% token**、少 **62% search call**，答案命中 36.1% vs 32.6%；
**skill transfer** 要用 {训练引擎} × {评测引擎} 的**交叉矩阵**验证，只报对角线会藏住 overfit。→ [20 §5.3](?book=drustz-interview-2026&section=mlsd&question=drustz-c5c2d47cc34774481f)

### E12. search agent 的 reward 怎么设计？会怎么被 hack？

答题锚点：outcome（LLM grader，**不要精确子串匹配** —— 会被「啰嗦地列一堆候选答案」hack）+ cost（超上下文惩罚、每次 search call 小负项，否则无限搜）+ process（引用是否真支撑 claim，否则模型可能猜对/靠记忆答对）；
**RL 只在 verifier 可靠时才开**：multi-hop QA 有唯一答案可以训，开放式研究任务 verifier 本身是难题 → 先 rejection sampling + SFT；
防 hack 必做：人工看一批**高 reward** 的轨迹。→ [20 §5.2](?book=drustz-interview-2026&section=mlsd&question=drustz-c5c2d47cc34774481f)

### E13. 搜索管线越来越复杂（本地化、新鲜度、多索引、按客户定制），怎么组织？

答题锚点：**DAG 而不是命令式脚本**；pull-based（下游要了上游才跑）+ **级联取消**（父超时/客户端断开 → 不浪费算力）+ **memoize**（菱形依赖只算一次）+ 无依赖节点自动并行；
多索引**赛跑** = hedged request，用算力换 p99；
图是数据 → 可视化 / 校验 / 逐节点 trace（能回答"某 query 为什么没返回某 URL、哪个子系统丢的"）；
类型安全（typestate + totality）把正确性负担从 agent 的 context window 转到 schema 和 runtime；节点级重试。→ [20 §2/§6](?book=drustz-interview-2026&section=mlsd&question=drustz-c5c2d47cc34774481f)

### E14. 为什么 agentic search 必须盯 p99 而不是 p50？怎么在生产里量分位数？

答题锚点：agent 连搜 5–30 次，单次 p99=1% → 30 次里至少撞一次的概率 **1 − 0. $99^{30}$  ≈ 26%**；
分位数：全排序 → 分桶 → **相对误差**而非绝对误差（延迟跨数量级）→ **log 桶**，`i = ceil(log x / log γ)`，`γ=(1+α)/(1−α)`；
桶数 = `ln(max/min)/ln γ`，α=1%、1ms~100s → **约 576 个桶**；
**mergeable 是硬需求**（跨机聚合、滑动窗口、每线程一个 sketch 免锁）—— 分位数不能平均，sketch 可以；
t-digest 尾部更准但无严格保证、合并要重压缩。→ [drill E](?book=drustz-interview-2026&section=labs&question=drustz-eabd4d8ae3fd207e2b)、[20 §7](?book=drustz-interview-2026&section=mlsd&question=drustz-c5c2d47cc34774481f)

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/09_question_bank.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/09_question_bank.md)。作者整理资料；许可和第三方来源范围见阅读指南。
