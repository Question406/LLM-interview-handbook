---
id: dt-c4-side-effect
section: good-data
order: 13
level: A
title: C4 那种块名单过滤，质量上去了，谁被切掉了？
quick: "常被切掉的是正常的身份讨论、方言、非英语页面和对话。块名单按词匹配、不看上下文，清理有害内容时会把这些一起删掉。所以过滤后除了看平均分和困惑度，还要按语言、主题统计通过率，抽查被丢弃的样本，看清哪些人和话题被排除了。"
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

被切掉的常是正常的身份讨论、方言、非英语页面和对话。块名单过滤可能让平均指标变好，同时也改了哪些语言、群体和话题还能留在训练集里，所以过滤后要把下游表现和各类内容的通过率一起报。只看平均困惑度（ppl），往往要等多语或安全评测出了问题，才发现某类内容早就被大量删掉了。

举个例子，`sex` 这个词既出现在医学页面，也出现在攻击性页面。块名单只按词匹配，两种页面会被一样处理。块名单本身缺上下文，词表也会过时，直接在 10B 文档上套一份英文脏话表，很容易重演 C4 的问题。

C4 是早期清理网页数据的公开例子。T5 那篇里，Raffel 等用块名单和启发式规则去掉脏话和坏页面。Dodge 等 2021 年回头分析，发现这种清理并不中立：身份相关的正常讨论、方言和非英语页面，也可能被判成有毒或低质量。WIMBD 后来在更多数据集里看到了类似问题。

误删还会传到后训练。预训练时把整个话题删掉，后训练可能只剩下「遇到这个话题就拒绝」的信号，见 `dt-safety-refuse`。这类错误一路传到下游才暴露，就是 `dt-data-cascade` 讲的情况。

## 怎么检查误删

过滤完我会看两类结果：下游平均分有没有改善，各语言、各主题的内容还剩多少。具体就是按语言和来源域名统计通过率，再抽 200 条被丢弃的样本看一看，分清哪些是正常内容被误删、哪些确实该丢。某个主题的通过率明显掉下来，就回头查是哪条规则触发的。块名单版本写进 dataset card，过滤器的 git 版本也记下来，方便以后复盘。

多语言要单独看。过滤器按语言校准，多语评测用母语者写的题；英语清理得再干净，也说明不了其他语言的质量。

检查本身也分层。个人信息（PII）、密钥和明确违法内容（包括 CSAM）用硬性检查在预训练阶段拦掉；主观毒性和要看语境的安全问题，交给抽查和可审计的后训练来处理。这两个阶段的数据效用 $u(x)$ 不一样，见 `dt-utility-select`。

## 追问

**那还检查毒性吗？**
要检查。明确违法内容和 CSAM 照样拦，其余内容按用途、语境和可审计的后训练规则来处理。

**开源块名单能直接拿来用吗？**
可以当候选。先在自己的各语言分组里验证误删率，再决定怎么用。

**这和 Diversity 指标有什么关系？**
各语言、各主题的通过率能直接看出谁被排除了，比一个全局 diversity 分数好解释。语义去重还会进一步改变覆盖，见 `dt-semdedup-code`。

**怎么判断一条被丢的样本是误删？**
抽查时把被丢弃的样本分成「正常内容被误删」和「确实应该丢弃」两堆，再看误删集中在哪条规则、哪个语言或主题上。
