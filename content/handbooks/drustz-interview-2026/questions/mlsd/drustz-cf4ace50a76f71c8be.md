---
id: drustz-cf4ace50a76f71c8be
section: mlsd
order: 84
level: A
title: 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 0. 开场 60 秒 ⭐⭐⭐
quick: 作者文档章节 · 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 0. 开场 60 秒 ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md
    type: primary
---
## 0. 开场 60 秒 ⭐⭐⭐

> 我先确认这套评测服务于哪个决策——是发布 gate、训练中选 checkpoint、还是对外榜单，三者的延迟预算和可信度要求差三个数量级。然后我会明确一件事：通用助手没有单一 ground truth，所以评测的目标不是"给出一个分数"，而是"支撑一个可以复盘的 ship / no-ship 判断"。
>
> 结构上我用三层：**可验证自动指标**做门禁和回归（数学答案、单测、格式约束、grounding 的 claim 级校验），**LLM-as-judge** 做大规模相对比较，**人工**只做两件事——定义 truth 和calibration judge。三层的样本量大约 100 : 10 : 1。
>
> 这套系统最容易坏在两个地方。一是 judge 有**系统性偏差**：位置、长度、自我偏好、格式，这些不是噪声，加样本不会消失。我会做双向交换判决、长度控制回归、跨家族 judge 仲裁，并且用一套人工双标集持续测 judge 自己的 κ 和扰动检出率。二是**污染**：benchmark 分数上涨可能只是测试集被预训练吃掉了。所以 eval 分三级——public 可训练、internal frozen 进数据管道 blocklist、private holdout 限次查询。
>
> 报告一定分层，不给总分：能力域 × 语言 × 难度 × 安全类别，每个切片报 n 和confidence interval。回归用冻结集 + 配对显著性检验，guardrail 用非劣性而不是"不显著"。安全单独一条线，越狱率和over-refusal率必须成对报，否则任何一个都能被刷。
>
> 成本上人工全评不可行，我用分层配额保证切片可报、随机审计集做unbiased estimate、不确定性sampling喂人工预算，并用 prediction-powered inference 把 judge 的全量结果和人工小样本合成一个无偏且更窄的区间。

面试官此时打断也没关系——上面已经覆盖 framing、三层结构、judge 偏差、污染、切片、回归、安全、成本八个点。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/15_case_eval_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
