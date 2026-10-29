---
id: drustz-be6f5787d1132f1ae7
section: mlsd
order: 206
level: A
title: 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 9. 完整 pipeline 与真实产出率
quick: 作者文档章节 · 21 · 怎么给 SWE agent 造训练数据（从 GitHub 到可训练实例） · 9. 完整 pipeline 与真实产出率
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
## 9. 完整 pipeline 与真实产出率

```text
GH Archive / API
   ↓  仓库筛选（star / issue / license / 非 fork / 排 benchmark）
21,000 个仓库                                    ← 保留 20% 的仓库覆盖 80% 的任务
   ↓  挖 PR + issue 链接 + 劈 patch
580,000 个候选实例
   ↓  便宜的启发式过滤（无测试 / 过大 / 只改文档）
   ↓  【最贵】环境搭建（agent 闭环，每仓一次）
   ↓  执行验证（三步 + 跑 3 次去 flaky）
   ↓  issue 清晰度过滤（3 个 LLM judge 全票才留）
32,000 个可执行任务 / 3,617 个仓库 / 20 种语言     ← SWE-rebench V2 的最终产出
```



**从 58 万到 3.2 万，产出率约 5.5%。** 这个数字值得记住 ——
**SWE 数据 pipeline 的产出率就是这个量级**，别按 math 的直觉去估算。

### 一个容易忽略的质量闸门

> SWE-rebench V2 用 **3 个独立 LLM judge**（gpt-oss-120b、GLM-4.7、DeepSeek-V3.2）
> 给 issue 的「规格是否足够实现」打分，**三个都说够才留**。
> 这个 rubric 是从 **SWE-bench Verified 的人工标注规范**改写来的，
> 并且**用人工标注calibration过**。

这条直接对应你在 Anthropic take-home 里做的事：**judge 要拿人工标注calibration**。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/21_swe_agent_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/21_swe_agent_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
