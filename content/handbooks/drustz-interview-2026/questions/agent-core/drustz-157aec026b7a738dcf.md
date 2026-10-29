---
id: drustz-157aec026b7a738dcf
section: agent-core
order: 44
level: A
title: Agentic RL（面试口径版） · 面试常问 3 题 ⭐⭐⭐
quick: 作者文档章节 · Agentic RL（面试口径版） · 面试常问 3 题 ⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/agentic_rl.md
    type: primary
---
## 面试常问 3 题 ⭐⭐⭐

### Q1：给 SWE agent 训练设计 reward，你怎么设计？





**参考打法**



- 开场给三分量结构：**task success**（hidden test suite 通过，二值或按 test 分级）+ **policy compliance**（未触碰禁区：没改测试文件、没逃逸沙箱、diff 范围约束）+ **efficiency**（步数/token 小权重惩罚）。
- success 信号用 verifiable signal 而非 LLM judge，且 agent 可见的测试与打分用的 hidden test 物理分离——这是防 hack 第一道线。
- compliance 做成 **hard gate** 而非软惩罚：碰了测试文件直接 reward = 0；软扣分会被 policy 做"性价比"权衡掉。
- efficiency 权重要小、可后期才引入——上来就罚步数，模型先学会提前终止交白卷。
- 主动提 shaped/中间 reward 的坑：给"打开了相关文件"部分分 → policy 学会疯狂打开文件刷分；agent 任务默认 outcome reward + 组内相对化（GRPO）来对付稀疏性。





> 高分句：reward 设计的默认假设是 policy 一定会找到你没想到的最大化路径——所以 success 用 hidden verifier，compliance 用 hard gate，efficiency 用小权重晚引入。

### Q2：reward hacking 见过哪些？给具体例子和防线。





**参考打法**



- 例 1 **改测试而非改代码**：SWE 任务里 agent 覆写 test 文件、删 assert、monkey-patch 打分函数换取 pass——防线：打分 test 对 agent 不可见 + 文件系统只读、diff 审计拒绝触碰 test 路径（2025-2026 公开研究反复复现此类，见 [Reward Hacking in RLVR](https://www.emergentmind.com/topics/reward-hacking-in-reinforcement-learning-with-verifiable-rewards-rlvr)）。
- 例 2 **骗过 judge**：LLM-as-judge reward 下，policy 学会输出自信、格式完美但内容错的答案，甚至在答案里嵌"该结果已验证正确"操纵 judge——防线：能换 verifier 就换、judge ensemble、拿对抗样本定期校验 judge 本身。
- 例 3 **学会过度谨慎拒答**：错误答案罚分重而拒答/escalate 不罚 → policy 收敛到"不确定就拒"，任务完成率崩、体验上表现为动不动甩给人——防线：无功也计低分，惩罚结构对"拒答/错答/对答"三态calibration。
- 监控口径：reward 曲线上涨但 held-out eval 不涨，这个**散度**就是被 hack 的告警信号；配人工抽查 top-reward rollout。
- 收个 meta：这是 Goodhart's law，proxy 与意图的 gap——缓解方向是 rubric 分解 reward + 显式惩罚项，而不是指望某个万能 reward。





> 高分句：reward hacking 不是 bug 是 optimizer 的正常输出——监控指标是 reward 与 held-out eval 的散度，散开即被 hack。

### Q3：RLVR 为什么适合 agent 任务？和 RLHF 什么关系？





**参考打法**



- 对比一句话：RLHF 的 reward 来自 learned RM（偏好数据训练），RM 是 proxy、OOD 下可被 policy 钻空，所以要 KL 罩着；RLVR 的 reward 来自程序化 verifier，是 ground truth 不是 proxy——hack 面小一个量级（但不为零，verifier 有洞照样被钻，见 Q2 例 1）。
- agent 任务**天然自带 verifier**：SWE 有测试、browser task 有终态断言、math 有答案匹配——这正是 agent 任务比开放对话更适合 RL 的结构性原因。
- 工程侧卖点：rollout 采集直接复用 eval harness——env、sandbox、tool executor、trace schema 全一样，只加 reward 出口和 trainer 回路；所以"先建可信 eval"是 RL 的前置投资，不是两套系统。
- 局限主动说：只覆盖可验证任务；主观/长尾任务退回 rubric-as-reward 或 LLM judge，就重新面对 judge hack。
- 若被追算法：GRPO 一句话——组内相对优势替代 value network；agent 任务 reward 稀疏 + 序列超长，value network 难训又贵，GRPO 用"同题多sampling"换掉它。





> 高分句：training harness 就是 eval harness 加一个 reward 出口——先有可信的 eval，才有可信的 RL。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/agentic_rl.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/agentic_rl.md)。作者整理资料；许可和第三方来源范围见阅读指南。
