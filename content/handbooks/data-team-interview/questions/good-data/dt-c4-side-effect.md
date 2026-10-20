---
id: dt-c4-side-effect
section: good-data
order: 13
level: A
title: C4 那种块名单过滤，质量上去了，谁被切掉了？
quick: "块名单可能在清理有害内容的同时，误删正常的身份讨论、方言、非英语页面和对话。检查过滤效果时，除了平均分和困惑度，还要按语言、主题统计通过率，并抽查被丢弃的样本，确认哪些人和话题被排除。"
companies:
  - apple
tags:
  - Apple
  - Filtering
  - Data Quality
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus"
    url: https://arxiv.org/abs/2104.08758
    type: primary
  - title: Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer
    url: https://arxiv.org/abs/1910.10683
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

块名单过滤可能提高平均指标，但它也会改变哪些语言、群体和话题还能出现在训练集里。因此，要同时报告下游表现和各类内容的通过率。只看平均困惑度（ppl），可能到产品的地区语言（locale）或安全评测出问题时，才发现某类内容已被大量删掉，见 `dt-data-cascade`。

T5 的 C4 是早期清理网页数据的公开例子。Raffel 等用块名单和启发式规则去掉脏话和坏页面。Dodge 等在 2021 年回头分析，发现这种清理并不中立：身份相关的正常讨论、方言和非英语页面，也可能被判断为有毒或低质量。WIMBD 后来在更多数据集里发现了类似问题。直接在 10B 文档上使用一份英文脏话表，很容易重演这些问题。

## 过滤后要看两类结果

一类是下游平均分有没有改善。另一类是各语言、主题的内容还剩多少。

块名单往往缺少上下文，而且词表会过时。比如 `sex` 出现在医学页面和攻击性页面中，单纯按词匹配会把两者同样处理。个人信息（PII）、密钥和明确违法内容可以用硬性检查拦截；主观毒性应结合抽查和后训练处理。若预训练时直接删掉整个话题，后训练可能只剩下「遇到这个话题就拒绝」的信号，见 `dt-safety-refuse`。

## 怎么检查误删

按语言和来源域名统计通过率，再抽查被丢弃的 200 条样本，区分「正常内容被误删」和「确实应该丢弃」。某个主题的通过率明显下降，就回头检查触发了哪条规则。把块名单版本写进 dataset card，并记录过滤器的 git 版本，方便复盘。

苹果的公开方向是按语言校准过滤器，并用母语者写的题做多语评测。英语内容的干净程度，不能直接代表所有语言的质量。预训练仍要拦截明确违法内容和 CSAM；其他需要判断语境的安全问题，应交给可审计的后训练。两个阶段的数据效用 $u(x)$ 不同，见 `dt-utility-select`。

## 追问

- 是否完全不检查毒性？仍要拦截明确违法内容和 CSAM。其余内容根据用途、语境和可审计的后训练规则处理，不能一律放行。
- 开源块名单能直接用吗？可以作为候选，先在自己的语言分组中验证误删率，再决定如何使用。
- 这和 Diversity 指标有什么关系？各语言、主题的通过率更容易暴露谁被排除，比一个全局 diversity 分数更有解释力。语义去重还会进一步改变覆盖，见 `dt-semdedup-code`。
