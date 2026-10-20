---
id: dt-contam-hold
section: labs
order: 16
level: A
title: Anthropic 风格：安全门禁被训练数据看见了，你先停什么？
quick: "发现评测污染后，先暂停依赖它的模型比较和发布，按类别估计影响，保留并降低旧结论的可信度。再换训练截止后的新题或私有题重新检查。只从训练集删命中内容，不能证明已训练模型的评测重新可靠。"
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

评测集被污染后，依赖它的 checkpoint 排序、发布和供应商比较应先暂停。再按危害类别、locale 和工具路径，统计精确、n-gram 与 embedding 命中率。总污染率 0.4% 可能掩盖某类 30% 的污染，不能只看总体。

保留过去的记录，但把「拒绝率达标」等结论改为带不确定性的说明。换训练截止后的新题、内部私有题，以及改数字或翻译后仍应拒答的题。生成器禁止接触评测集，评测登记表记录进数据血缘，见 `dt-repro-lineage`。

只从 mix 删去命中 n-gram，再在原评测上复测，不能证明修好了。已训练模型仍见过题型或内容；删除训练文件也不会直接撤回已学知识。如何检测见 `dt-contamination`，合成集涨分风险见 `dt-synth-bench-trap`。

## 重新验证时看什么

在未污染的评测上重新测拒绝率、误拦，以及回答是否有证据支持，见 `dt-safety-refuse`。AFM 人评和 locale 检查也一样：污染后的旧集只能降为开发集。

私有题可以先少而可靠，按危害分层。用教师扩题前，检查与旧评测的重叠，避免再次把测试内容生成进训练。对照使用研究集和固定评测，不默认使用用户交互。面试只报告能量化的命中率，不编苹果内部事故。

LiveCodeBench 的时间划分思路也适用于安全题。Lee et al. 2021 说明复制内容有害，但删掉命中 n-gram 不能替代更换评测。

## 追问

- 只有英语被污染怎么办？英语检查集失效，其他 locale 仍按各自情况评测；不能拿受污染英语分数排序多语模型。
- 私有题太少怎么办？先保证题和判分可靠、按危害分层，再谨慎扩题。
- 要公开承认吗？面试说明内部治理流程即可，数字只用能量化的结果。
