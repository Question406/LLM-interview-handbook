---
id: drustz-a4fd9b621c97e86d1c
section: mlsd
order: 75
level: A
title: 09 · ML System Design 题库 · J. Frontier-lab 五题（2026-07-29 新增）
quick: 作者文档章节 · 09 · ML System Design 题库 · J. Frontier-lab 五题（2026-07-29 新增）
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
## J. Frontier-lab 五题（2026-07-29 新增）

这五题对应 §15–19 五个新 case study。**它们是 OpenAI / Anthropic / Reflection
这类实验室的常考题型，和推荐/搜索类 MLSD 是两个体系。**
每题给「30 秒必须先说的那句话」+「最容易被追死的一问」。

### J1. Design an evaluation pipeline for ChatGPT.
→ 详见 [15](?book=drustz-interview-2026&section=mlsd&question=drustz-07520390a6b2c475a2)

**先说**：「开放式对话没有单一 ground truth，所以我不会先讲指标，
先讲**分层**——按能力域/语言/安全类别切开，一个总分是没有信息量的。」

**最容易被追死**：「你的 LLM judge 怎么保证是对的？」
→ 人工双标集报一致率 + κ + **人类间一致性的天花板**；按扰动类型分层的检出率；
判决翻转率（位置交换）；gold anchor 夹带监控 judge 静默升级。

### J2. Design a data pipeline for RL post-training.
→ 详见 [16](?book=drustz-interview-2026&section=mlsd&question=drustz-8df61c36cf3291cc69) ⭐ **最对口你的经历**

**先说**：「RL 数据和 SFT 数据要的东西不一样。SFT 要好答案，
**RL 要的是有梯度信号的 prompt** —— 全对和全错的题，组内优势恒等于 0，
是纯粹的算力浪费。」

**最容易被追死**：「你怎么保证 batch 里有梯度？」
→ 只答难度筛选是**不完整的**。组内优势为 0 有两个来源：题目退化（数据侧，筛数据能修）
和**熵坍缩**（优化侧，筛数据完全没用）。要同时监控策略熵和组内回答多样性。

### J3. Design a synthetic data generation system.
→ 详见 [17](?book=drustz-interview-2026&section=mlsd&question=drustz-296c269c87350db28f)

**先说**：「先问合成要解决什么——数据不足 / 长尾覆盖 / 隐私 / 标注成本 / 难度控制。
这五个目的会导出完全不同的系统。」

**最容易被追死**：「怎么知道合成数据是有用的而不是有害的？」
→ 只能用**下游任务提升**衡量，不能用生成质量自评。
并且要监控 replace vs accumulate 的代际比例，防模型坍塌。

### J4. Design a distributed inference system.
→ 详见 [18](?book=drustz-interview-2026&section=mlsd&question=drustz-ed4eb9e01c767c533b)

**先说**：「先分叉——在线低延迟 serving 和离线batch inference的**目标函数不同**
（p99 延迟 vs throughput/成本），架构选择也不同。你要的是哪个？」

**最容易被追死**：「prefill 和 decode 为什么要分开？」
→ prefill 是 compute-bound、decode 是 memory-bound，混在一起会互相拖累。
⚠️ **在线 serving 的 oncall 你没做过，要诚实标注**；离线批量是你的主场。

### J5. Design a benchmark for evaluating agents.
→ 详见 [19](?book=drustz-interview-2026&section=mlsd&question=drustz-f2abdd7ba423c258b9)

**先说**：「agent 评测最大的陷阱是**只看最终成功率**——它分不出
『走对了路』和『绕过约束蒙对了』。过程和结果必须分开报。」

**最容易被追死**：「 $\mathrm{pass}^k$  和 pass@k 有什么区别，为什么你选前者？」
→ pass@k 是「k 次里至少一次成功」（乐观）， $\mathrm{pass}^k$  是「k 次**全部**成功」（可靠性）。
信息在 per-task 通过率的**分布**而非均值：同为 p=0.7，双峰系统  $\mathrm{pass}^8$ =0.70 可上线，
均匀系统  $\mathrm{pass}^8$ =0.057 不可上线。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/09_question_bank.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/09_question_bank.md)。作者整理资料；许可和第三方来源范围见阅读指南。
