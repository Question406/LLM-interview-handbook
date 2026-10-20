---
id: dt-llm-clf-logprob
section: labs
order: 46
level: A
title: Anthropic：只用 token logprob，怎么做成质量 / 安全二分类器？
quick: "让模型只输出 Yes/No，再用两者的 logprob 计算分类分数。阈值应在各语言、数据域的开发集上校准。不要先生成长解释再正则找词，也不要默认所有分组都适合 0.5 阈值；独立人标和评测仍用于检查误差。"
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

系统提示要求只回答 Yes 或 No，不生成解释。helper 返回各输入的 token logprob 后，分类分数可取 $\mathrm{softmax}(\ell_{\mathrm{Yes}},\ell_{\mathrm{No}})$ 的 Yes 概率，或差值 $\ell_{\mathrm{Yes}}-\ell_{\mathrm{No}}$。再按语言和数据域，在开发集尝试阈值、校准后用于过滤。

先生成「这段高质量因为……」再正则找词，输出形式不稳定，也难以校准。统一使用 0.5 阈值，可能对低资源语言与代码产生很不同的误差。

## 怎么验证分类器

质量和安全分类都可以从这种方法起步。用少量人标样本校准、检查误差，不把模型输出当成百万级金标。代码和工具轨迹不要复用网页教育价值分类头。

logprob 分类器可作为开发过滤器，发布仍依赖固定评测与人工抽查，见 `dt-quality-clf-synth`、`dt-oai-classifier`。它与 FineWeb-Edu 的合成标签分类器思路相近。

AceOffer 记录过 Anthropic MLE 题型：提供 batch 文本到 token logprob 的 helper，要求设计二分类器，报道到 2025 年 7 月。

## 追问

- Yes/No 表面形式变了怎么办？提示中固定输出形式，解码只看对应的两个 id。若模型输出 `yes.`，先规范化查表，或把带句点的 id 合并到 Yes 类。
- 没有 logprob API 怎么办？改用小编码器，或用独立 oracle 做拒绝采样，别强行套这个实现。
- 能作为奖励模型（RM）吗？可以提供弱奖励特征。与隐藏测试或人工标签冲突时，以独立验证为准，见 `dt-agent-reward-spec`。
