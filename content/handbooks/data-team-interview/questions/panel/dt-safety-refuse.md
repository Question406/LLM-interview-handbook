---
id: dt-safety-refuse
section: panel
order: 21
level: A
title: Panel：安全 / 拒答数据怎么配，才不会变成一律拒绝？
quick: "训练中同时提供应该拒绝和应该回答的题，并分别评测攻击成功率、过度拒绝和任务有用性。只喂有害请求与拒答示范，会让模型把拒绝当成通用答案，连正常问题也不回答。"
companies:
  - apple
tags:
  - Apple
  - Safety
  - Refusal
  - Preference
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: "XSTest: A Test Suite for Identifying Exaggerated Safety"
    url: https://arxiv.org/abs/2308.01263
    type: primary
---

安全训练要同时覆盖应该拒绝和应该回答的请求。如果 SFT 只有拒答示范，模型可能把拒绝学成通用答案，连端侧助手本来该回答的问题也拒绝。

不这么选的理由：AFM 把 Responsible AI、内容过滤、locale 评测写进报告。堆有害-拒答对，或把安全当成后训练最后一道、不管有用性，边界会扩到「怎么杀进程」「怎么剪电线」。

## 应拒和应答要成对出现

应拒：明确有害、越狱、要私人数据。标签是拒，不是说教长文。

应答：看起来敏感、实际无害（XSTest 一类）。没有这类，拒答边界会扩。

另一种拒答来自证据不足：图片或邮件里没有的信息，不能编造，见 `dt-grounding-data`。这是产品安全，政策安全是另一套题。两套不要混成一个 `refuse` 标签。

对比学习用「同一问，有害答 vs 安全且有用答」。只有「有害 vs 拒绝」，模型学到拒绝万能。强化学习（RL） 把 helpful / harmless 分开报，像约束。InstructGPT 已经写过对齐会改能力剖面。

评测分开画：攻击成功率、过度拒绝、任务有用性。locale 还要看当地法规和用语，母语者标，见 `dt-locale-data`。

用户日志里的越狱默认不进全球 FM。红队用内部和许可集。

## 追问

- **端侧 3B 安全怎么做？** 底座拒答 + 系统过滤。不要把开放世界政策长文灌进 3B。
- **安全税 2 个点 MMLU 能不能发？** 看产品契约。开放知识掉一点、过度拒绝升很多，通常不发。
- **合成越狱有用吗？** 有，当开发集。门禁用独立红队，防和生成器同族。
