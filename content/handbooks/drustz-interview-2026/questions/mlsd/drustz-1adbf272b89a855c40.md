---
id: drustz-1adbf272b89a855c40
section: mlsd
order: 33
level: A
title: >-
  06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 八、Search Agent
  Post-training：SFT → Preference → RL ⭐⭐⭐
quick: >-
  作者文档章节 · 06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 八、Search
  Agent Post-training：SFT → Preference → RL ⭐⭐⭐
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
## 八、Search Agent Post-training：SFT → Preference → RL ⭐⭐⭐

### 8.1 把 trajectory 定义成可训练 episode

```text
state_t:
  user task, current subquestions, visited URLs,
  evidence table, remaining budget, timestamps

action_t:
  search(query, filters)
  open(url)
  find(pattern)
  extract(span)
  cite(claim, source)
  revise_plan(...)
  stop(answer)

observation_t:
  ranked results / page excerpt / fetch error / policy result
```



每一步必须记录 search engine/index snapshot；否则同一 action 未来返回不同网页，trajectory 不可复现。

### 8.2 Demonstrations 从哪里来

1. **Human expert traces**：人在受限 browser/tool 环境中完成真实任务。
2. **Best-of-N teacher rollouts**：强模型生成多条 trajectory，用独立 outcome/evidence verifier 选优。
3. **Production successes + corrections**：只在明确 consent、redaction、versioning 后使用。
4. **Programmatic task generation**：从结构化知识/网页变更生成可验证问题。
5. **Failure repair pairs**：把缺证据、重复搜索、错误引用轨迹修成 better trajectory。

数据要同时包含：

- search-required 与 search-free questions；否则模型会学会每题都搜。
- single-hop 与 multi-hop。
- 有答案、无答案、冲突证据、时效性强的问题。
- budget 紧与宽松场景。
- tool failure / 429 / dead link / parser failure。

### 8.3 阶段一：SFT / behavior cloning

目标是先学会协议和基本策略：

- query reformulation：从用户问题拆成可检索子问题；
- action schema：正确调用 search/open/cite；
- evidence ledger：不重复访问、记录每个 claim 缺什么；
- stop/abstain：证据完整才停止；
- citation：引用真正支持 claim 的 span。

SFT 的局限：模仿 demonstration 的冗余；对未见工具结果 exposure 不足；不会自动优化 cost。

### 8.4 阶段二：DPO / preference learning

构造相同 task 下的 `(chosen trajectory, rejected trajectory)`：

- 正确完整证据 > 只答对但引用错误；
- 少量有效搜索 > 重复十次相似 query；
- 官方/原始来源 > SEO 聚合转载（在同等证据下）；
- 识别冲突并说明 > 偷选一个来源；
- 合理 abstain > 无证据猜测。

Preference label 可以来自 human，也可以由 rubric grader 产生，但需对 judge 做 human calibration，避免 verbosity/style bias。

DPO 适合稳定、离线 pair 数据；它不会真正探索搜索环境，容易受 behavior policy support 限制。

### 8.5 阶段三：RL / outcome-verifiable training

让 policy 在线与冻结的 search snapshot/environment 交互。一个可解释 reward：

\[
r(\tau)=
w_1 r_{answer}
+w_2 r_{citation\_entail}
+w_3 r_{evidence\_coverage}
+w_4 r_{source\_quality}
-\lambda_1 n_{search}
-\lambda_2 tokens_{fetched}
-\lambda_3 latency
-\lambda_4 r_{unsafe}
\]

设计原则：

- **Outcome reward 为主**：可验证 QA、实体集合或 downstream task completion。
- **Process reward 只奖可观察行为**：引用 span 支持 claim、满足 freshness filter；不要奖漂亮思维过程。
- **检索文本不是 policy 生成 token**：计算 policy loss 时 mask observation/retrieved tokens，避免把环境输出当模型 action。
- Reward model/grader 在该训练阶段冻结；训练的是 policy，不要一边改 grader 一边声称 reward 上升。
- 对 search calls 加 penalty，但必须先满足 correctness constraint；否则模型学会“不搜最便宜”。
- 先在固定 index snapshot 训练以降低 non-stationarity，再评估 live web。

### 8.6 Reward hacking 清单

| Reward | 可能 hack | 防线 |
|---|---|---|
| Answer exact match | 猜答案、不搜 | freshness/OOD/no-answer set；evidence gate |
| Citation count | 堆很多无关引用 | claim-level entailment precision + coverage |
| Search penalty | 永不搜索 | search-required tasks；correctness constraint |
| Source authority | 只用大站、漏长尾 | evidence utility + diversity slice |
| LLM judge score | 冗长、迎合 judge style | deterministic checks + human calibration + judge ensemble/holdout |
| Dwell/click | clickbait 排名上升 | long-term satisfaction、return-to-SERP、task completion |

> 高分句：reward 应该奖励“环境中可验证的结果”，不是模型自己宣称已完成；citation correctness 不能只靠同一个 answer model 自评。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/06_search_post_training.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md)。作者整理资料；许可和第三方来源范围见阅读指南。
