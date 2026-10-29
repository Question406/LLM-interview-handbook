---
id: drustz-931ecb9366bcc102d3
section: mlsd
order: 163
level: A
title: 19 · Case：设计 agent 能力 benchmark · 1. 先问清楚：七个澄清问题 ⭐⭐⭐
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 1. 先问清楚：七个澄清问题 ⭐⭐⭐
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
## 1. 先问清楚：七个澄清问题 ⭐⭐⭐

每个问题后面标注的是**这个答案会改掉哪个设计决策**——面试时要把这句说出来，否则会被当成拖时间。

| # | 问题 | 答案改变什么 |
|---|---|---|
| 1 | **这个 benchmark 服务谁的决策？** 是"选一个基座模型"、"决定这次训练要不要上线"、还是"对外发榜"？ | 决定**噪声预算**。上线 gate 要能分辨 2–3pt（→ 配对设计 + 大 k + 大题量）；选型只要分辨 10pt（→ 300 题跑一次就够）；对外发榜则**私有 held-out 集变成必需品**（§8）。 |
| 2 | **被测对象是模型还是系统？** 换 scaffold 算不算换了被测对象？ | 决定 harness 是自变量还是常量。Terminal-Bench 上同一模型换 scaffold 差 15–20pt——如果没锁死这一层，所有对比都不成立。 |
| 3 | **agent 有写权限吗？会花钱/发消息/改真实数据吗？** | 决定沙箱等级和"是否需要 undo"。只读 agent 可以打真实 API；有写操作必须全部快照 + 回滚，而且要专门测"该拒绝时拒不拒绝"。 |
| 4 | **任务的正确性谁说了算？** 有没有可程序化的终态？还是必须人判？ | 这是**最硬的约束**（§6）。没有程序化 verifier 的领域，benchmark 规模上限直接从 1000 题掉到 100 题，成本高一个数量级。 |
| 5 | **产品允许重试吗？有没有廉价 verifier 可以 rerank？** | 决定报 pass@k 还是  $\mathrm{pass}^k$ （§7）。coding agent 有测试可以重试 → pass@k 有意义；退款 agent 一次做错就是真赔钱 → 只能看  $\mathrm{pass}^k$ 。 |
| 6 | **一次完整评测的预算是多少（&#36; 和 wall-clock）？** | 决定 $N_{task} \times k \times steps$ 的三方分配（§10）。"每次 commit 都跑"和"每个 release 跑一次"是两个完全不同的设计。 |
| 7 | **这个 benchmark 要活多久？谁维护？** | 决定要不要程序化生成任务。一次性评估可以手写 200 题；要活两年就必须有滚动换题机制和 verifier CI，否则 12 个月后它会静默失效（§9）。 |

补充第 8 问（如果时间允许）：**现在用什么在做决策？** 如果已有一个内部 eval，先问它的 test-retest 噪声是多少——很多团队从没测过，这个问题本身就能拿分。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
