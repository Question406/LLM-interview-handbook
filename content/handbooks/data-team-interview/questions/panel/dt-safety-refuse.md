---
id: dt-safety-refuse
section: panel
order: 21
level: A
title: Panel：安全 / 拒答数据怎么配，才不会变成一律拒绝？
quick: "应该拒绝和应该回答的题要成对出现，明确有害的请求配简短拒答，看起来敏感、实际无害的请求配正常回答。只喂有害请求和拒答示范，模型会把拒绝当成通用答案，连正常问题也不回答。评测分开报攻击成功率、过度拒绝和任务有用性。"
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

安全数据要同时覆盖该拒绝和该回答的请求。SFT 里只有拒答示范，模型会把拒绝学成通用答案，连本来该回答的问题也拒绝。

举个例子，「怎么杀进程」「怎么剪电线」听起来有点危险，其实是正常问题。只堆「有害请求 - 拒答」对，或者把安全当成后训练最后一道工序、不管有用性，模型学到的拒答边界会不断外扩，最后连这种问题也拒绝。它没见过「看起来敏感但应该回答」的例子，就分不清边界在哪。

所以我会成对配题。明确有害、越狱、索要私人数据的请求，标签是简短的拒绝，不写说教长文。看起来敏感、实际无害的请求，XSTest 一类的题就是这种，标签是正常回答，少了这一类，拒答边界就会外扩。偏好数据用「同一个问题，有害回答 vs 安全且有用的回答」来对比；如果只有「有害 vs 拒绝」，模型学到的是拒绝万能。强化学习（RL）阶段把 helpful 和 harmless 分开报，当作约束来处理，InstructGPT 就写过，对齐会改变模型的能力剖面。

评测时攻击成功率、过度拒绝、任务有用性三条曲线分开画。不同 locale 还要考虑当地法规和用语，由母语者标注，见 `dt-locale-data`。

## 追问

**证据不足导致的拒答，和安全拒答是一回事吗？**
不是一回事。图片或邮件里没有的信息不能编造（`dt-grounding-data`），这和政策安全是两套题，标签要分开，别混成同一个 `refuse`。

**小模型的安全怎么做？**
底座负责拒答，再加系统层过滤。开放世界的长篇政策别往小模型里灌。

**安全带来 2 个点的 MMLU 损失，能不能发？**
看发布要求。开放知识掉一点、过度拒绝却升了很多，通常不发。

**合成的越狱题有用吗？**
有，可以当开发集。门禁要用独立红队的题，防止和生成器同族。
