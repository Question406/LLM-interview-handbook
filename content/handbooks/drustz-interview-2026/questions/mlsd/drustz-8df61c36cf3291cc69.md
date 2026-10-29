---
id: drustz-8df61c36cf3291cc69
section: mlsd
order: 102
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 16 · Case：设计 RL（post-training）数据流水线
quick: >-
  作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 16 · Case：设计
  RL（post-training）数据流水线
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md
    type: primary
---
# 16 · Case：设计 RL（post-training）数据流水线

⏱ 精读约 45 分钟 ｜ 这是你**最对口**的一题，按「能当场展开 30 分钟」准备，不是按「能答上来」准备

> **三档阅读入口**
> - **面试前 3 分钟** → §1 一句话主张 + §7.1 组内优势为 0 的两个来源 + §16 一页速记
> - **只有 15 分钟** → §1 + §2（RL 数据 ≠ SFT 数据）+ §7（难度筛选，本篇最重）+ §10（reward hacking）
> - **完整** → 顺读；分量最重的四节是 §2 / §7 / §9 / §10
>
> **四个题眼**（答不出这四点，其余讲得再多都是外围）：
> 1. **RL 数据的产出物不是「好答案」，是「有梯度信号的 prompt」**（§2）
> 2. **组内优势为 0 有两个来源：题目退化（数据侧）和熵坍缩（优化侧）**，筛数据只能解决第一个（§7.1）
> 3. **verifier 的假阳性会被策略主动搜索，假阴性只是噪声**——两类错误的代价差好几个数量级（§9.4）
> 4. **难度不是题目的属性，是 (题目, 策略, sampling参数) 三元组的属性**，所以它会随训练漂移（§7.4）

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
