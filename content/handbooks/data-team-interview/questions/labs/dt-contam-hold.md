---
id: dt-contam-hold
section: labs
order: 16
level: A
title: Anthropic 风格：安全门禁被训练数据看见了，你先停什么？
quick: "先停所有依赖这份评测的模型比较和发布，因为它的分数已经不可信。然后按类别估计污染影响，保留旧结论但降低其可信度，再换训练截止后的新题或私有题重新检查。只从训练集删掉命中内容，不能证明已训练模型的评测重新可靠。"
companies:
  - apple
tags:
  - Anthropic
  - Contamination
  - Safety
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: "LiveCodeBench: Holistic and Contamination Free Evaluation"
    url: https://arxiv.org/abs/2403.07974
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先停所有依赖这份评测的决定：checkpoint 排序、发布和供应商比较。模型已经见过门禁题，门禁分数就说明不了它在没见过的题上会不会拒答。

## 为什么删训练数据不够

常见的第一反应是从 mix 里删掉命中的 n-gram，再在原评测上复测。这证明不了修好了：已训练的模型仍然见过这些题型和内容，删除训练文件也不会撤回已经学到的东西。Lee et al. 2021 说明复制内容有害；删掉命中 n-gram 之后，评测本身仍然要换。

## 处理顺序

1. **按类别估计影响。** 按危害类别、locale 和工具路径，分别统计精确、n-gram 与 embedding 命中率。总污染率 0.4% 可能掩盖某一类 30% 的污染。检测方法见 `dt-contamination`。
2. **降级旧结论。** 保留过去的记录，但把「拒绝率达标」这类结论改为带不确定性的说明。污染后的旧集只能降为开发集，人评集和各语言的检查集也一样。
3. **换题。** 换训练截止后的新题、内部私有题，以及改数字或翻译后仍应拒答的题。LiveCodeBench 的时间划分思路也适用于安全题。私有题可以先少而可靠，按危害分层，再谨慎扩题；用教师扩题前要检查与旧评测的重叠，避免再次把测试内容生成进训练（合成集涨分的风险见 `dt-synth-bench-trap`）。
4. **重新验证。** 在未污染的评测上重新测拒绝率、误拦，以及回答是否有证据支持，见 `dt-safety-refuse`。对照用研究集和固定评测。
5. **堵住来源。** 生成器禁止接触评测集，评测登记表记入数据血缘，见 `dt-repro-lineage`。

## 追问

- **只有英语被污染怎么办？** 英语检查集失效，其他 locale 仍按各自情况评测；不能拿受污染的英语分数给多语模型排序。
- **要公开承认吗？** 面试中说明内部治理流程即可，只报告能量化的命中率。
