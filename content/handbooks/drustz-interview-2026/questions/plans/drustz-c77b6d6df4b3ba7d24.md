---
id: drustz-c77b6d6df4b3ba7d24
section: plans
order: 36
level: A
title: >-
  3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 1：Deep Learning / PyTorch /
  Transformer 前置基础
quick: >-
  作者文档章节 · 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 1：Deep Learning / PyTorch /
  Transformer 前置基础
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 作者复习计划与报告
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md
    type: primary
---
> 下文的个人经历、时间安排与复习状态属于原作者 DrustZ；可用作组织自己材料的参考。

## Week 1：Deep Learning / PyTorch / Transformer 前置基础

### 本周目标

把 LLM 需要的 DL/PyTorch 基础重新压实。你不是重新学 ML，而是把和 LLM 面试最相关的部分补到“能解释 + 能写 toy code”的程度。

### 必学概念

- Tensor shape / broadcasting
- Matrix multiplication
- Autograd
- Forward / backward
- Cross entropy
- Optimizer state
- Mixed precision：fp32 / fp16 / bf16
- Parameter / gradient / activation memory
- Train loop / eval loop
- gradient accumulation
- checkpointing 的直觉

### 你必须能回答的问题

1. 一个简单 MLP 的 forward 会保存哪些中间 activation？
2. 为什么 training 比 inference 更耗显存？
3. optimizer state 为什么可能比 parameter 本身还占内存？
4. fp16 和 bf16 的差别是什么？为什么大模型训练偏爱 bf16？
5. batch size、sequence length、hidden size 分别影响什么？
6. gradient accumulation 解决什么问题？它和真正增大 batch size 是否完全等价？

### 小实现

- [ ] 手写一个 MLP training loop
- [ ] 手写 cross entropy，不直接调用 PyTorch loss
- [ ] 打印每层 tensor shape
- [ ] 估算 parameter / activation / optimizer memory
- [ ] 加入 gradient accumulation

### 本周输出物

`week1_dl_pytorch_notes.md`

内容包括：

- 一张 train loop 数据流图
- parameter / gradient / activation / optimizer state 的区别
- 5 个常见 PyTorch bug
- 一个最小 MLP training loop

### 判断是否过关

闭卷解释：

```text
input → forward → loss → backward → optimizer.step → zero_grad
```



并且能解释每一步在显存里主要存了什么。

---

---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
