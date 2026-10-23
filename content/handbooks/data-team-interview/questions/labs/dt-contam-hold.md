---
id: dt-contam-hold
section: labs
order: 16
level: A
title: Anthropic 风格：安全门禁被训练数据看见了，你先停什么？
quick: "先停所有依赖这份评测的模型比较和发布，它的分数已经不可信。然后按类别估计污染影响，旧结论保留但降低可信度，再换训练截止后的新题或私有题重测。只从训练集删掉命中内容，证明不了已训练模型的评测又可靠了。"
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

先停所有依赖这份评测的决定：checkpoint 排序、发布、供应商比较。模型已经见过门禁题，门禁分数就说明不了它在没见过的题上会不会拒答。

常见的第一反应是从 mix 里删掉命中的 n-gram，再在原评测上复测。这证明不了修好了。已经训好的模型见过这些题型和内容，删掉训练文件也撤不回它学到的东西。Lee et al. 2021 说明复制内容有害，可删完命中之后，评测本身还是得换。

接下来我会估计影响有多大，按危害类别、locale 和工具路径分别统计精确、n-gram 与 embedding 命中率。分开统计是因为总污染率 0.4% 可能盖住某一类 30% 的污染，检测方法见 `dt-contamination`。过去的记录保留，但「拒绝率达标」这类结论要改成带不确定性的说明，污染过的旧集降为开发集，人评集和各语言的检查集也一样。

然后换题，换成训练截止后的新题、内部私有题，以及改数字或翻译之后仍应拒答的题。换好之后，在未污染的评测上重测拒绝率、误拦，以及回答有没有证据支持，见 `dt-safety-refuse`，对照用研究集和固定评测。

最后把来源堵住：生成器不许接触评测集，评测登记表记入数据血缘，见 `dt-repro-lineage`。

## 追问

**新题怎么保证模型没见过？**
按训练截止时间切。LiveCodeBench 按时间划分的思路对安全题也适用，再加上改数字或翻译后仍应拒答的变体。

**私有题很少，怎么扩？**
先少而可靠，按危害分层，再慎重扩题。用教师扩题前要查和旧评测的重叠，免得又把测试内容生成进训练，合成集涨分的风险见 `dt-synth-bench-trap`。

**只有英语被污染了怎么办？**
英语检查集作废，其他 locale 按各自的情况继续评。受污染的英语分数不能拿来给多语模型排序。

**要不要对外公开承认？**
面试里讲清楚内部治理流程就行，只报能量化的命中率。
