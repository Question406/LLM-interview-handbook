---
id: drustz-c5653befaf775fbe17
section: mlsd
order: 172
level: A
title: 19 · Case：设计 agent 能力 benchmark · 10. 成本：agent 评测的钱是怎么烧掉的
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 10. 成本：agent 评测的钱是怎么烧掉的
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md
    type: primary
---
## 10. 成本：agent 评测的钱是怎么烧掉的

### 10.1 量级估算（面试要能当场算）

```text
总成本 ≈ N_task × k × E[steps] × tokens/step × price
       + N_task × k × (env 启动 + reset) × 机时
```



代入一组典型值：$N=500$、$k=8$、平均 30 步、每步 8k input（含累积上下文）+ 500 output。

- 单次 rollout ≈ 30 × 8k = **240k input tokens**（未计 prefix cache）
- 总计 4000 次 rollout ≈ **10 亿 input tokens**

结论：**这不是可以每次 commit 都跑的东西。** sampling策略必须是设计的一部分，而不是事后优化。

### 10.2 sampling与早停策略

| 策略 | 做法 | 省多少 | 风险 |
|---|---|---|---|
| **分层 CI** | commit 级跑 smoke(5%) + core 的 10% 固定子样；nightly 跑全 core；release 跑全集含 frontier | 10–50× | 子样本必须**分层抽样且固定**，否则不同 commit 之间不可比 |
| **自适应 $k$** | 先每题跑 2–3 次，只对 $\hat p \in [0.2, 0.8]$ 的题追加 rollout | 2–3× | 需要两阶段调度 |
| **序贯早停** | 每题跑到能判定 stable_pass / stable_fail 就停 | 30–50% 的 $k$ | 会**低估 flaky**；早停后报出的 $\hat p$ 有偏 → 只用在 CI 快筛，正式报告用固定 $k$ |
| **不可恢复态剪枝** | 检测到死循环、关键文件已删、预算耗尽即终止 | 20–40% steps | 剪枝规则会误杀"能救回来"的情况，要抽样人工验 |
| **prefix cache** | 系统提示 + 工具 schema 是固定长前缀 | 输入成本 30–70% | 无（应当默认开） |
| **便宜的先跑** | 小模型/短预算先筛掉明显不可解的题 | — | 引入selection bias，只用于建题阶段不用于评分阶段 |

"自适应 $k$"就是我在 Reflection 做的 **16 条探测 → 128 条正式**这套两阶段调度的直接对应物，可以明说这个迁移。

### 10.3 基础设施：agent eval 的负载形态和 RL rollout 几乎一样

大量并行、任务长尾（有的 5 步结束、有的跑满 100 步）、可被更高优先级作业抢占。我在 Reflection 为 RL 数据生成自建过一套batch inference框架来对付这个问题，直接可复用：

- **pause / resume**：作业能在被抢占时保存进度并在资源回来时续跑，而不是从头再来。对 agent eval 尤其重要——一次 rollout 可能已经烧了 20 分钟。
- **动态申领 / 让出资源**：共享 GPU 池里被其他团队抢占是常态，与其等独占配额不如做成弹性。
- **TCP 式自适应并发调节**：成功就加并发，失败窗口内就退。对付的是外部推理服务的限流和尾延迟。

**诚实边界**：这是离线批量作业的调度，不是在线 serving 的容量规划——我没有大规模在线服务的 oncall 经验，这点要说清楚。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
