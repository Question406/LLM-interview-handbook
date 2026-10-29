---
id: drustz-9dfc17e0ba17e18556
section: mlsd
order: 38
level: A
title: >-
  06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 十三、面试题与答题
  walkthrough
quick: >-
  作者文档章节 · 06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 十三、面试题与答题
  walkthrough
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md
    type: primary
---
## 十三、面试题与答题 walkthrough

### Q1：没有 query–document labels，怎么 cold start？

**回答结构**：

1. BM25 + strong off-the-shelf dense model 建 baseline。
2. 从高质量文档反向生成 diverse queries，做 teacher verification。
3. 用公共 retrieval/QA 数据 warm-start，但单独报告 domain gap。
4. 小规模 human pool 对真实 query 标 graded relevance。
5. 上线 shadow；用受控 exploration 获取 unbiased-ish implicit feedback。
6. Active learning 优先标模型分歧和高业务价值。

不要答“直接用点击数据”：cold start 根本没有足够 exposure，而且 bias 最大。

### Q2：为什么不直接让大 LLM 对所有网页打分？

Web scale 候选量太大、成本和延迟不可接受；LLM 只能在高-recall candidate pool 上做 teacher/reranker。还要考虑 index coverage——LLM 看不到没被召回的页面。用 cascade 把 expensive model 放在 top K，并通过 distillation/early exit 降低 serving cost。

### Q3：如何选 hard negatives？

先按阶段混合 random/in-batch、BM25、dense-mined、same-entity temporal negatives；unjudged candidates 不直接当负例，top pool 人工/teacher 分级；每轮 mining 冻结 snapshot，保留固定 test；监控 false-negative rate 和 negative hardness 分布。

### Q4：点击率上涨是否说明 search 更好？

不一定。可能是 position、标题诱导或新 UI。需要 impression propensity、random swap/interleaving、IPS/SNIPS；同时看 long-term satisfaction、reformulation、return、downstream completion。用人工 relevance holdout 验证构念。

### Q5：Retriever 该用 bi-encoder、ColBERT 还是 cross-encoder？

不是三选一：bi-encoder/learned sparse 做 web-scale candidate recall；late interaction 可在更高成本下增强 fine-grained retrieval；cross-encoder 放 top K 精排。最终按 recall–latency–index memory–cost Pareto 和 query slices 选择。

### Q6：怎么训练 query rewriting？

- 数据：真实 reformulation session、专家拆解、teacher-generated multi-hop subqueries。
- SFT：预测 normalized query/filters/subqueries。
- Pair preference：能提高 evidence recall 且少重复的 rewrite 胜。
- RL：最终 task success + evidence gain，惩罚 duplicate/empty query。
- Eval：rewrite 本身 BLEU 没意义；看 downstream Recall@k、complete-chain recall、cost。

### Q7：怎么让 agent 知道何时停止搜索？

维护显式 evidence ledger：每个 required claim/subgoal 的状态。训练中加入证据完整、缺失、冲突和 no-answer trajectories；stop reward 只在 outcome verifier 确认 acceptance criteria 时给。测 premature-stop rate 与 over-search rate，画 quality/cost frontier。

### Q8：Outcome reward 与 process reward 怎么选？

可验证任务优先 outcome，避免规定唯一思路；process 只约束必要且可观测的行为，如 citation entailment、policy violation、budget。若 outcome 稀疏，可用 potential-based/step evidence gain shaping，但要做 ablation，确保没有把 shortcut 变成目标。

### Q9：如何评价 citation？

先把答案拆成 atomic claims；每个 claim 映射 source span。分别测 citation precision（span 是否支持）、claim coverage（有多少 claim 被支持）、source correctness/freshness。Deterministic span/version 检查 + NLI/LLM judge + human calibration，不用 citation 数量代替正确性。

### Q10：训练 search agent 时为什么 mask retrieved tokens？

检索结果是 environment observation，不是 policy 选择生成的 action。若把 observation token 纳入 policy gradient，会把 credit 错分给不可控网页文本，训练不稳定甚至鼓励选择更容易“预测”的页面，而非更有用的搜索动作。

### Q11：如何处理网页不断变化导致 RL environment 非平稳？

训练/回归先用 versioned frozen index snapshot；每个 observation 记录 content hash。模型通过 gate 后再在 live shadow 测 freshness/generalization。生产 trace 保存 query、URL、snapshot/version，不能只存当前页面链接。

### Q12：如果 offline Recall@k 很好但 answer accuracy 差？

逐层检查：gold page 是否有 gold passage；excerpt 是否包含答案；answer model是否忽略/误读；evidence是否冲突；citation/answer rubric 是否正确。补 passage-level labels和 complete-chain recall，而不是继续扩大 top-k 导致 token/cost 上升。

### Q13：如果 answer accuracy 上升但 Recall@k 下降，是否可以上线？

不能仅凭平均 answer accuracy。可能 generator 用参数记忆或 benchmark leakage 猜对。对 fresh/OOD/no-answer、citation-required slice 检查，要求 evidence coverage guardrail；下游若依赖列表完整性，recall 下降会产生隐藏损害。

### Q14：如何防止 search engine 被 SEO spam 训练污染？

采集层做 canonical/domain/spam/malware signals；标注 adversarial negative；ranker 分离 relevance 与 source quality；上线监控 domain concentration、新域异常、clickbait high-click-low-satisfaction；保留人工 red-team 和快速 block/rollback 通道。

### Q15：怎样证明 synthetic queries 有价值？

做 compute/data-matched ablation：真实-only、synthetic-only、mixed；同一个 base model/hyperparameter，按 real held-out/temporal/OOD slices 比较。检查 lexical overlap、query diversity、teacher-human agreement；只有在真实 held-out task improvement 上才算有效。

### Q16：如何把 production feedback 用进训练而不形成 feedback loop？

完整记录 serving policy/propensity；保留 exploration traffic；对 exposure 做 correction；train/eval 时间切分；监控 source/query distribution；旧 ranker 未展示的候选用 independent crawl/pool 补齐。新模型先 shadow，不直接全量反哺自身日志。

### Q17：Search quality 和 agent quality 谁负责？

接口 contract 要可归因：search 服务报告 retrieval labels/coverage、ranker/index versions；agent 报 query plan、selected results、outcome。用 oracle retrieval 测 agent upper bound、oracle agent/query 测 search upper bound，避免团队互相归咎。

### Q18：Exa 类系统最重要的 cost metric？

不是单次 API 平均成本，而是 **cost per successful downstream task**，并拆 search、fetch/extract、rerank、LLM tokens。还要看 p95/p99，因为 agent 并行搜索会放大 tail latency。

### Q19：如何测试 fresh search？

建立滚动 temporal benchmark：每天/每周从 cutoff 后新事件生成问题，gold 保留发布/抓取/index 时间。测 discovery/fetch/index 各段 lag、fresh answer accuracy、stale citation rate；cache key 带 snapshot/TTL。

### Q20：v1 最小可行方案是什么？

BM25 + off-the-shelf dense hybrid → RRF → small cross-encoder → structured excerpts；1000–5000 条真实 graded queries + synthetic tail；component/offline temporal eval；agent 用 SFT demonstrations，暂不 RL。上线 shadow 后确认 outcome 信号和日志质量，再做 preference/RL。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/06_search_post_training.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md)。作者整理资料；许可和第三方来源范围见阅读指南。
