---
id: pt-test-time-search-topology
section: posttrain
order: 28
level: S
title: 固定推理预算时，并行采样、顺序反思、Verifier rerank、list-wise merge 应怎样公平比较和选型？
quick: 比较的对象是完整推理系统，而不是“采样次数”。固定总 token、模型调用、墙钟时间和 verifier 成本；再按候选覆盖率、选择器质量、合并器质量和尾延迟拆开，依据题目是否可验证决定拓扑。
tags:
  - Test-time Search
  - Verifier
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Scaling Test-time Compute for LLM Agents
    url: https://arxiv.org/abs/2506.12928
    type: primary
---

并行采样适合答案可独立生成、后验可投票或验证的任务；顺序反思适合后一步能利用前一步失败信息；prefix-level search 适合能在中间状态打分的任务。rerank 的收益取决于候选池中是否已经有正确解，merge 则额外依赖模型能否忠实整合证据而不引入新错。

实验应固定总预算，而不是固定 `N`：一次长轨迹、十条短轨迹、十次 verifier 调用的成本不同。报告 generator 的 oracle upper bound、真实 selector 的差距、候选间相关性、P50/P95 latency 和每成功任务成本。

不要把一个拓扑在数学题上的成绩外推到工具 Agent。工具环境里分支会产生外部副作用，搜索还要计入 reset、sandbox、状态快照和动作可回滚性。
