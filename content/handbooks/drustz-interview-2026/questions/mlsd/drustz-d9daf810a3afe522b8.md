---
id: drustz-d9daf810a3afe522b8
section: mlsd
order: 125
level: A
title: 17 · Case：设计合成数据生成系统 · 边界：这篇讲什么、不讲什么
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 边界：这篇讲什么、不讲什么
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md
    type: primary
---
## 边界：这篇讲什么、不讲什么

| 主题 | 在哪 |
|---|---|
| 通用答题框架（Problem → Metrics → Data → Model → Eval → Serving → Feedback） | [01](?book=drustz-interview-2026&section=mlsd&question=drustz-5aa0ed2f208256af4b) |
| 数据来源、标签合同、数据短缺阶梯（synthetic 是第 9 级） | [02 §5](?book=drustz-interview-2026&section=mlsd&question=drustz-7702fad4618814bbd3) |
| SFT / DPO / RL 的选择、reward 设计与防 hacking | [03](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2) |
| MinHash/LSH、语义去重、benchmark 污染、mixture 配比 | [07 §六 / §八 / §九](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) |
| 通用 offline→online 评测、阈值、灰度 | [08](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) |
| 客服域的数据轴（resolution 标签、多租户冷启动） | [14](?book=drustz-interview-2026&section=mlsd&question=drustz-1979efc83c83eeddca) |

**本篇只回答合成数据特有的部分**：为什么生成、用哪种范式生成、生成完怎么筛、多样性怎么量、代际自噬怎么防、分布差多远怎么测、什么时候根本不该生成、钱花在哪。

去重与质量分类器的**通用机制**在 07 里；这里只讲"合成数据的去重和真实数据的去重有什么不同"（§6.3）。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
