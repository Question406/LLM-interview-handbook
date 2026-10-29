---
id: xiaohongshu-rag-limits
section: agent
order: 169
level: A
title: 小红书秋招：RAG 有哪些短板？如何保证输出一致性？
quick: >-
  RAG
  把错误从参数挪到了检索链路上，切块丢信息、索引过期、检索错误、引用错挂、证据冲突都会让它答错。一致性要分两层保证：同一输入多次输出稳定，靠降低温度和约束输出结构；引用的块稳定，靠固定检索快照、记录模板版本。反复运行同一个
  prompt 取众数代替不了这些控制。
tags:
  - Xiaohongshu
  - RAG
  - Consistency
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 小红书大模型秋招算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/f41f88405bf844489452feeb26bf4a8b'
    type: candidate-first-hand
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：大模型秋招算法
- 届别 / 流程：秋招；一面
- 面试时间：原帖未披露；帖子发布于 2025-12-11
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“RAG 存在哪些缺陷？”**；**“如何确保大模型输出内容的一致性？”**

RAG 的缺陷，我会说它把错误从参数里挪到了检索链路上：切块丢失、索引过期、语义近但事实错、引用错挂、多份证据冲突时随机站队。社区笔记还多一层时效和立场冲突。所以装了检索也照样会编。一致性要从两层保证：同一输入多次输出要稳定，引用指向的块也要稳定，前者靠温度和结构化 decoding，后者靠快照和引用校验。

举个例子：一个活动已经下线了，索引还没更新，用户问「现在还有满减吗」，检索召回了旧活动页，模型据此很自信地回答「有」。这时在 prompt 里再加一句「请根据资料回答」也没用，资料本身就是错的。

RAG 的短板可以沿着链路一段段拆。表格、图注、价格条被切开，结构就断了，见 `xiaohongshu-mmkg-chunk`。同款的种草文语义很近，会被当成当前 SKU 的条款，可它买不了。活动下线后索引还在，是热更新滞后。生成时引用了一个没召回的块，是引用错挂。top-$k$ 被近重复占满、售后槽位缺失，是被噪声带偏，见 `pdd-pick-relevant-chunks`。表格和多模态本来就弱，OCR 会错，图文会不一致。冲突被最高分抹平最危险，它会把 hallucination 伪装成检索成功。这些都不是「再加一句根据资料回答」能修好的。

一致性的做法是固定快照，别连跑三次碰运气。同一个 query 固定索引版本、检索参数和 top-$k$ 集合；decoding 时降低随机性，或者约束成 JSON；冲突时输出「来源 A/B」，别随机站队。模板、工具 schema、检索版本组成一个不可变 release，见 `pdd-prompt-template-versioning-rollback`。「连抽三次取众数」不适合当线上方案，那是在掩盖方差。

评测用同一道题多次运行的一致率和引用稳定率，再加上无根据的原子事实、过期活动引用、冲突有没有被抹平，流畅度只当辅助。RAG 解决的是「缺知识」，解决不了「检索错了仍然自信」，所以评测要单列引用错误和冲突处理。能固定快照的评测，才能把模板改动和检索漂移切开；同一个 query 换了索引版本，要当成新实验，别和提示改动混在一个 A/B 里。多 Agent 或 Deep Research 会引入更多检索跳，停止和选块策略不当会进一步破坏一致性，见 `xiaohongshu-deep-research-stop`。同一面还问了生成评测、hallucination 和多智能体，hallucination 那部分可以接到 `xiaohongshu-hallucination-prompt`。

## 追问

**RAG 能消灭 hallucination 吗？**
不能。检索错、切块丢、冲突被抹平，模型照样会编，见 `xiaohongshu-hallucination-prompt`。

**温度设成 0 就一致了吗？**
不够。检索集合要是在漂，低温度只是稳定地复述错资料。

**冲突时怎么保持一致？**
并列给出来源，或者升级澄清，不允许出现静默赢家。

**线上怎么复现某次回答？**
记录索引版本、top-$k$ 的 ID 和模板 release，否则无法复现。
