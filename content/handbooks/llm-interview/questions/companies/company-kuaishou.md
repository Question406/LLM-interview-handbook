---
id: company-kuaishou
section: companies
order: 13
level: A
title: 快手：大模型算法 / 应用开发应重点准备什么？
quick: >-
  应用侧追意图识别、工具超时空返回与用户反馈；算法侧追 RAG 检索 vs 生成归因、SFT 多源配比、LoRA A/B
  初始化。多模态岗还会问动态分辨率与直播带货时延。
tags:
  - Kuaishou
  - 真题导航
  - "2026"
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
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

快手题覆盖「能上线的 Agent」和「能讲清后训练」。陷阱是背一串模型名，却说不清短视频 / 直播里**时延、空结果、错误归因**怎么做对照实验。应用岗把空工具结果编成事实会直接挂；算法岗把 RAG 错全推给生成、SFT 配比拍成 1:1:1，同样过不了追问。

## 准备主线

1. **Agent 生产**：意图按 taxonomy 拆（`kuaishou-agent-intent-recovery`）；超时 / 空返回分类错误码（`kuaishou-tool-timeout-empty-result`）；注入与工具权限（`kuaishou-prompt-injection`）；多步规划（`kuaishou-modular-planning`）。
2. **RAG 归因与评估**：先替换实验区分检索 vs 生成（`kuaishou-rag-retrieve-vs-generate`），再证明系统真 work（`kuaishou-rag-eval-build`）。规划与幻觉率量化见 `kuaishou-agent-eval-dims`。
3. **后训练**：多源配比（`kuaishou-sft-source-mix`）；SFT 之后还有什么（`kuaishou-posttrain-after-sft`）；DPO vs RM 训练（`kuaishou-dpo-vs-rm-train`）、DPO 注意点（`kuaishou-dpo-cautions`）。
4. **系统与多模态**：LoRA A/B 初始化（`kuaishou-lora-ab-init`）；GQA/MQA/MLA（`kuaishou-gqa-mqa-mla`）；三工具高 QPS（`kuaishou-tool-chain-latency`）；动态分辨率（`kuaishou-dynamic-res`）；直播带货时延（`kuaishou-live-commerce-latency`）；V3 vs R1（`kuaishou-v3-vs-r1`）。

## 本手册真题卡

点击下面每条即可跳到对应题。

- `kuaishou-agent-intent-recovery` / `kuaishou-tool-timeout-empty-result` / `kuaishou-prompt-injection`
- `kuaishou-rag-retrieve-vs-generate` / `kuaishou-rag-eval-build` / `kuaishou-agent-eval-dims`
- `kuaishou-sft-source-mix` / `kuaishou-posttrain-after-sft` / `kuaishou-dpo-vs-rm-train` / `kuaishou-dpo-cautions`
- `kuaishou-lora-ab-init` / `kuaishou-gqa-mqa-mla` / `kuaishou-v3-vs-r1`
- `kuaishou-tool-chain-latency` / `kuaishou-dynamic-res` / `kuaishou-live-commerce-latency` / `kuaishou-modular-planning`

## 追问

- **空结果为什么不能当「没找到」直接生成？** 超时与空库语义不同；编造是幻觉。先错误码，再决定重试 / 澄清 / 拒答。
- **SFT 配比怎么定？** 按覆盖与 holdout 难度，做只改一类比例的对照，看锚点是否掉。不是 1:1:1。
- **直播带货时延先砍哪？** 先测商品检索与多图分辨率，再谈模型。按 id 准备替换实验。
