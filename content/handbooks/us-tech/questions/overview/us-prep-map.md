---
id: us-prep-map
section: overview
order: 1
level: S
title: 美国 Tech / frontier lab：LLM 岗按哪几条线准备？
quick: "先把 Transformer / KV cache 改对，再补 GQA 与长上下文显存、并行和 serving，以及 RLHF / DPO / GRPO 的实现与评测。按公司加重点：OpenAI 偏 debug 和统计，Anthropic 偏实现与对齐，Google / Meta 偏架构和训练栈，NVIDIA 偏 kernel，Apple 偏端侧；六周计划见 `us-llm-re-prep`。"
tags:
  - US Tech
  - 备考地图
  - OpenAI
  - Anthropic
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OpenAI Research Engineer Interview Guide (Exponent)
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
  - title: OpenAI ML Coding 面经
    url: https://www.1point3acres.com/bbs/thread-1177444-1-1.html
    type: candidate-first-hand
  - title: Anthropic interview questions (IGotAnOffer)
    url: https://igotanoffer.com/en/advice/anthropic-interview-questions
    type: secondary
---

先按下表找到目标公司的问法，再沿 debug、架构与显存、训练 / serving、对齐和产品设计几条线准备。比如遇到带 bug 的 nanoGPT，要能修好并加 KV cache，也要解释 GQA、并行和对齐目标怎样影响实现与评测。

本手册按公司整理美国 frontier lab / Big Tech 的公开面经；GQA、量化、RLHF 等主题基础在「LLM 面试手册」里，这里用来对照各家公司怎么问。

## 按公司找到准备入口

| 公司 | 公开面经里反复出现的形态 | 本手册对应卡 |
| --- | --- | --- |
| OpenAI RE / MLE | Transformer debug、KV cache、noisy all_gather + 信息论、entropy / L1 | `openai-transformer-debug`、`openai-allgather-noise`、`openai-entropy-l1`、`openai-instructgpt-kl` |
| Anthropic | 内存库 + TTL、Tokenizer、Constitutional AI、computer-use 确认 | `anthropic-inmemory-db`、`anthropic-bpe-tokenizer`、`anthropic-constitutional-ai` |
| Google DeepMind | ML design（数据/模型/评测一体）、GQA/MQA | `gdm-ml-design`、`google-gqa-mqa` |
| Meta GenAI / FAIR | Llama GQA、onsite 的 AI-enabled coding | `meta-llama-gqa`、`meta-ai-coding` |
| NVIDIA | 万亿参数并行、INT8 / 推理 kernel | `nvidia-trillion-train`、`nvidia-int8-quant` |
| Apple Intelligence / Siri | 手写 MHA、voice grounded 检索增强生成（RAG） | `apple-mha-code`、`apple-siri-grounded` |
| Amazon AGI / Bedrock | 企业 RAG、p95、引用与过期文档 | `amazon-bedrock-rag` |
| Microsoft | DeepSpeed ZeRO、Copilot grounding、Phi / ORPO | `msft-deepspeed-zero`、`msft-copilot-ground` |
| xAI / SpaceXAI / Tesla | 15 分钟筛（项目深挖 + why xAI）、内存 KV/race、Grok 工具与缓存；先读现在在卖什么 | `xai-spacexai-now`、`xai-screen-15min`、`xai-kv-txn`、`tesla-data-engine` |

白板手撕走 ML Coding 章（`coding-softmax-stable`），训练/推理系统走 `sys-3d-parallel`，RAG / 推荐 / 评测平台走 `design-prod-rag`，RLHF / 直接偏好优化（DPO） / CAI 走 `align-rlhf-kl`。公司章只收「这家怎么问」。

## 常见题型怎样练

1. **Debug 大于默写。** OpenAI 会给 ~300 行 Transformer，四个标注区间各有一个 bug，改完再加 KV cache。国内更常见「从零手写 attention」。
2. **统计和信息论会单独成轮。** noisy all_gather 后面要推轮数 bound，还要想到 float 精度能改进 naive 界。这轮在 Exponent 候选人报告里被写成整个 loop 最难的一轮。
3. **工程实现题更长。** Anthropic CodeSignal 是分层解锁：内存库 TTL、银行账户、爬虫。不是一道 20 行 LeetCode。
4. **产品约束进算法题。** Apple Siri 要 grounded、voice 长度预算、引用可评测；Amazon 要 p95 和文档日更。答成「上个 RAG」会被追问。

先把 attention 和 KV cache 写到能闭卷改 shape。再做一次「给一份错的 attention，列出因果 mask / softmax 维 / 缩放 / 位置编码」的自检。OpenAI 统计轮补一点信息论：重复码、Chernoff、量化位数 $\log(\mathrm{range}/\varepsilon)$。NVIDIA 补 Megatron 三维并行和 Nsight 看利用率。Apple / Amazon 准备一个端到端 grounded 生成设计，指标不要只报 BLEU。

每张卡对应一条公开面经或官方流程描述；细节被论坛藏了的，我按能公开复述的题面写，不编造没出现过的 follow-up。

## 追问

**没美国身份也要看这本吗？**
国内大模型岗也在抄这些题型，尤其 Transformer debug 和 GQA 显存。当作压轴即可。
**和 LLM 面试手册什么关系？**
那本按主题和国内公司切；这本按美国公司切同一批基础，问法更偏 debug / 实现 / 产品约束。
**要不要刷 Meta 的 AI coding 平台？**
有面试再向 recruiter 要练习环境。没面试时用多文件仓库 + 弱助手做 60 分钟 debug/extend 模拟就够。
