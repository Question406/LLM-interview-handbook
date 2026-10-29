---
id: drustz-ed4eb9e01c767c533b
section: mlsd
order: 144
level: A
title: 18 · Case：设计大规模分布式推理系统 · 18 · Case：设计大规模分布式推理系统
quick: 作者文档章节 · 18 · Case：设计大规模分布式推理系统 · 18 · Case：设计大规模分布式推理系统
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md
    type: primary
---
# 18 · Case：设计大规模分布式推理系统

⏱ 精读约 30 分钟 ｜ 题面：**"Design a distributed inference system."**

> **三档阅读入口**
> - **面试前 3 分钟** → §0 两个场景的分叉 + §11 面试前一页速记
> - **只有 15 分钟** → §0 + §2 指标 + §4 离线批量（你的主场）+ §10 10 分钟口述稿
> - **完整** → 顺读，重点 §0 / §4 / §6 / §10
>
> 三个题眼：**§0 在线 vs 离线是两道题不是一道题**、**§4 离线的目标函数是 &#36;/M token 不是 p99**、**§6 抢占恢复的检查点粒度**。这三点答不出，背再多 PagedAttention 名词也没用。

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/18_case_distributed_inference.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/18_case_distributed_inference.md)。作者整理资料；许可和第三方来源范围见阅读指南。
