---
id: drustz-1306b1b6affb8c9bf1
section: mlsd
order: 126
level: A
title: 17 · Case：设计合成数据生成系统 · 0. 90 秒开场（建议背下来）⭐⭐⭐
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 0. 90 秒开场（建议背下来）⭐⭐⭐
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
## 0. 90 秒开场（建议背下来）⭐⭐⭐

> 合成数据不是一个任务，是五个不同的任务共用一个名字。我先问要解决的是哪一个：总量不足、长尾覆盖、隐私替代、标注成本、还是难度控制。这五个目的的验收标准完全不同——补长尾的合成数据**故意不匹配真实分布**，隐私替代的合成数据**必须匹配**，两者的设计几乎相反。
>
> 无论哪一种，成功的定义只有一个：**在固定算力、固定其他变量的条件下，加了这批数据的模型在纯真实的 held-out 集上更好**。生成端的自评分、judge 平均分、"看起来很像真的"，都不是证据——它们只说明 generator 和 judge 有共同的偏好。
>
> 系统上我会做四段：**seed 采集 → 多阶段生成 → 三级质量漏斗（规则 / 程序或模型校验 / 人工抽检）→ 混合比例与代际治理**。真正决定成败的是后两段：漏斗决定单位有效样本的成本，代际治理决定这套系统能不能连续跑三个季度而不退化。
>
> 最后我会明确一条红线：**真实的 held-out eval 集里绝不能有合成数据**，以及**每条样本必须带 provenance**（generator、checkpoint、prompt 版本、seed 来源、通过了哪几级闸门）。没有 provenance，出了问题无法回滚，也无法回答"这次涨点是数据带来的还是配比带来的"。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
