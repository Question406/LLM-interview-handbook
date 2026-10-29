---
id: drustz-7d3db0a54f609af6d9
section: mlsd
order: 208
level: A
title: 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 11. 和 math/STEM 的对照：什么能迁移，什么不能
quick: >-
  作者文档章节 · 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 11. 和 math/STEM
  的对照：什么能迁移，什么不能
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md
    type: primary
---
## 11. 和 math/STEM 的对照：什么能迁移，什么不能

### ✅ 直接迁移

- **难度筛选**：pass@k ∈ {0,1} 的题没有梯度 —— 完全一样
- **去重 / 去污染**：MinHash + LSH，只是normalization函数换成 patch normalization
- **配比与课程**：按难度桶sampling
- **judge 要用人工标注calibration**
- **对照组纪律**：任何「数据改进」都要有 count-matched 的对照

### ❌ 不能迁移，要重新学

- **环境即数据**。math 的样本是一段文本，SWE 的样本是**一个可复现的容器**。
  你的存储、缓存、调度设计全都不一样。
- **验证是慢的、有状态的**。math 可以在数据生成时就验证完；
  SWE 的验证要排队、要隔离、要防 flaky，**它本身就是一个分布式系统问题**。
- **产出率低一个数量级**。58 万 → 3.2 万。
- **轨迹是多步的**。你造的不是 `(prompt, answer)`，是 `(环境, 工具协议, 终局判据)`。

### 一句可以在面试里说的话

> 「math 数据里验证器是廉价的后处理；SWE 数据里**验证器本身就是产品**。
> 我做 math curation 时最贵的是找题和去重，
> 做 SWE 数据时最贵的是**让测试能在正确的历史时点上跑起来** ——
> SWE-rebench V2 的漏斗是 58 万候选到 3.2 万可执行，产出率 5.5%，
> 几乎所有损耗都在环境和执行这两步。」

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/21_swe_agent_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
