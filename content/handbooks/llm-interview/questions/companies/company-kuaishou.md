---
id: company-kuaishou
section: companies
order: 13
level: A
title: 快手：大模型算法 / 应用开发应重点准备什么？
quick: "快手应用岗会追问意图识别、工具超时与空返回、用户反馈；算法岗会追问 RAG 的错误来自检索还是生成、SFT 的多源数据配比和 LoRA A/B 初始化。多模态岗还要准备动态分辨率和直播带货的时延问题。"
tags:
  - Kuaishou
  - 真题导航
  - "2026"
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 快手大模型应用开发算法岗三面面经
    url: https://www.nowcoder.com/feed/main/detail/4ff132d0d0fb450398341f4ec9828def
    type: candidate-first-hand
  - title: 快手实习 大模型算法面经
    url: https://www.nowcoder.com/feed/main/detail/93a72d1bd0a2418281414f288dcb3629
    type: candidate-first-hand
  - title: 快手26校招大模型算法一面
    url: https://www.nowcoder.com/feed/main/detail/b1da5731c34e4a3d99becef4f0a0c169
    type: candidate-first-hand
  - title: 快手大模型算法二面-实习面经
    url: https://www.nowcoder.com/feed/main/detail/ca3fe5949e0b4ddbb7807e43380ab7a6
    type: candidate-first-hand
---

快手的题一半是「能上线的 Agent」，一半是「能讲清后训练」。背一串模型名没用，面试官会问短视频、直播场景里时延、空结果和错误归因怎么做对照实验。

举个例子，工具调用超时返回了空结果，模型要是把它当成「没找到」接着往下写，就会编出事实。应用岗要说清怎么处理这种空工具结果；算法岗要能区分检索增强生成（RAG）里的检索错误和生成错误，并说明监督微调（SFT）的数据配比依据，随手定成 1:1:1 不行。

## 准备主线

1. Agent 生产这块，要会用意图分类体系拆分请求（`kuaishou-agent-intent-recovery`），用不同错误码区分超时和空返回（`kuaishou-tool-timeout-empty-result`），处理注入和工具权限（`kuaishou-prompt-injection`），做多步规划（`kuaishou-modular-planning`）。
2. RAG 归因和评估，先用替换实验区分检索和生成的影响（`kuaishou-rag-retrieve-vs-generate`），再评估系统是不是真的有效（`kuaishou-rag-eval-build`）。规划和幻觉率怎么量化见 `kuaishou-agent-eval-dims`。
3. 后训练看多源配比（`kuaishou-sft-source-mix`）、SFT 之后还有什么（`kuaishou-posttrain-after-sft`）、直接偏好优化（DPO）和奖励模型（RM）训练的对比（`kuaishou-dpo-vs-rm-train`），以及 DPO 的注意点（`kuaishou-dpo-cautions`）。
4. 系统和多模态看 LoRA A/B 初始化（`kuaishou-lora-ab-init`）、GQA/MQA/MLA（`kuaishou-gqa-mqa-mla`）、三工具高 QPS（`kuaishou-tool-chain-latency`）、动态分辨率（`kuaishou-dynamic-res`）、直播带货时延（`kuaishou-live-commerce-latency`）和 V3 vs R1（`kuaishou-v3-vs-r1`）。

## 本手册真题卡

下面每条点进去就能跳到对应题。

- `kuaishou-agent-intent-recovery` / `kuaishou-tool-timeout-empty-result` / `kuaishou-prompt-injection`
- `kuaishou-rag-retrieve-vs-generate` / `kuaishou-rag-eval-build` / `kuaishou-agent-eval-dims`
- `kuaishou-sft-source-mix` / `kuaishou-posttrain-after-sft` / `kuaishou-dpo-vs-rm-train` / `kuaishou-dpo-cautions`
- `kuaishou-lora-ab-init` / `kuaishou-gqa-mqa-mla` / `kuaishou-v3-vs-r1`
- `kuaishou-tool-chain-latency` / `kuaishou-dynamic-res` / `kuaishou-live-commerce-latency` / `kuaishou-modular-planning`

## 追问

**工具返回空结果，为什么不能当「没找到」直接生成？**
超时和空库是两种语义，当成没找到往下写，编出来的就是幻觉。先看错误码，再决定重试、澄清还是拒答。

**SFT 配比怎么定？**
根据任务覆盖和留出集（holdout）的难度来定。每次只改一类数据的比例，看固定评测集有没有下降，别直接拍成 1:1:1。

**直播带货时延先砍哪？**
先测商品检索和多图分辨率，再谈模型。按 id 准备替换实验。
