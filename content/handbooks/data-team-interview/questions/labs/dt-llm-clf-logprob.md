---
id: dt-llm-clf-logprob
section: labs
order: 46
level: A
title: Anthropic：只用 token logprob，怎么做成质量 / 安全二分类器？
quick: "让模型只输出 Yes 或 No，用这两个 token 的 logprob 算一个连续分数，再按语言和数据域在开发集上分别校准阈值。连续分数能画校准曲线、按需挪阈值；先写长解释再用正则找词，输出不稳，也没法校准。模型分只当开发过滤器，误差靠独立人标和固定评测来查。"
companies:
  - apple
tags:
  - Anthropic
  - Classifier
  - Logprob
  - Apple
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: LLM-Based Binary Classifier Design (AceOffer, Anthropic reports)
    url: https://aceoffer.app/interviews/llm_based_binary_classifier_design_technical_deep_dive
    type: secondary
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

系统提示要求模型只回答 Yes 或 No，不写解释；拿到这两个 token 的 logprob 后算一个连续分数，再按语言和数据域在开发集上定阈值、做校准，然后才拿去过滤。质量分类和安全分类都可以从这个方法起步。

比如问「这段网页有没有教育价值？只回答 Yes 或 No」，模型在 Yes 上的 logprob 是 −0.3，在 No 上是 −1.5。差值是 1.2，换成 Yes 的概率大约 0.77。这个数可以和阈值比，也可以拿去画校准曲线。

分数可以取两者 softmax 之后 Yes 的概率 $\mathrm{softmax}(\ell_{\mathrm{Yes}},\ell_{\mathrm{No}})$，也可以直接用差值 $\ell_{\mathrm{Yes}}-\ell_{\mathrm{No}}$。两者单调等价，区别只在阈值的刻度。

只看这两个 token，是因为 logprob 给的是连续分数，能画校准曲线、按需要移动阈值。要是让模型先写「这段高质量，因为……」再用正则找关键词，长解释的输出形式不稳定，得到的也只是离散判断，很难校准。

阈值要按语言和数据域分别在开发集上试，同一个 0.5 在低资源语言和代码上的误差可能差很多。验证时用少量人标样本做校准和误差检查，模型输出本身只是弱标签，当不了百万级金标。代码和工具轨迹要单独训分类头，网页教育价值的分类头放到这些数据上会失准。这个思路和 FineWeb-Edu 用合成标签训分类器相近。logprob 分类器可以当开发阶段的过滤器，发布还是要靠固定评测和人工抽查，见 `dt-quality-clf-synth`、`dt-oai-classifier`。

## 追问

**这题是从哪来的？**
AceOffer 记录过这道 Anthropic MLE 题：给一个把一批文本映射成 token logprob 的 helper，要求设计二分类器，报道到 2025 年 7 月。

**Yes/No 的表面形式变了怎么办？**
在提示里固定输出形式，解码时只看对应的两个 token id。模型输出 `yes.` 的话，先规范化再查表，或者把带句点的 id 合并到 Yes 类。

**没有 logprob API 怎么办？**
改用小编码器，或者用独立 oracle 做拒绝采样。

**能当奖励模型（RM）吗？**
可以当弱奖励特征。它和隐藏测试或人工标签冲突时，以独立验证为准，见 `dt-agent-reward-spec`。
