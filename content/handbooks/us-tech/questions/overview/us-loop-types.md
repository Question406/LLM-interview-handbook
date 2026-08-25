---
id: us-loop-types
section: overview
order: 2
level: A
title: 美国 Tech LLM 岗常见几轮，每一轮到底在考什么？
quick: >-
  典型是 recruiter 筛背景、技术电面（debug 或 ML coding）、现场或虚拟 onsite 四到六轮：coding、ML
  基础 / 论文、系统设计或训练系统、行为面，研究岗再加 research deep dive。不要按国内「八股 + 两道
  LeetCode」去赌。
tags:
  - 备考
  - 流程
  - Onsite
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OpenAI Research Engineer Interview Guide (Exponent)
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
  - title: Anthropic interview questions (IGotAnOffer)
    url: https://igotanoffer.com/en/advice/anthropic-interview-questions
    type: secondary
---

各家包装不一样，骨架差不了太多。我按「这一轮失败会怎么被写进 feedback」来准备，不按公司名字背流程表。

## 电面：能不能独立改对东西

OpenAI / Apple 常见给一份能跑的小 Transformer 或 attention，里面有 bug，或者让你现场加 KV cache。Anthropic 常见 CodeSignal 分层实现。Google / Meta 电面更接近「中等算法 + 一点 ML」。这一轮不是展示阅读量，是展示你能在没人提示时定位 shape / 数值 / 并发。

准备法：闭卷写 attention 和一步 decode，再专门练「四类植入 bug」：因果 mask、softmax 轴、缩放、位置偏移。见 `openai-transformer-debug`、`apple-mha-code`。

## Onsite 技术轮怎么拆

1. **ML coding：** 实现采样、tokenizer、layernorm、一个小训练 step。评委看数值稳定和接口，不看你能不能背 PyTorch 文档。见 `coding-softmax-stable`、`coding-layernorm`。
2. **ML 基础 / 论文：** GQA 为什么省显存、PPO clip 在干什么、DPO 的 implicit reward。研究岗会深挖你简历上的工作。
3. **System / ML design：** 万亿训练怎么切并行、RAG 的 p95、推荐双塔。NVIDIA 更偏 GPU；Amazon / Apple 更偏产品约束。
4. **Behavioral：** Meta / Amazon 会认真打。STAR 要落到「你做的权衡」，不要背领导力原则原文。

xAI 有时把系统题收成「带事务的 KV + 找 race」，时间紧，正确性比完整引擎重要，见 `xai-kv-txn`。

## 研究岗多出来的那一轮

Research Engineer 和 Research Scientist 都可能有 paper deep dive，但 RE 更常被拽回「这段代码你怎么写进训练栈」。Scientist 会被问到「这个实验如果结果反了你信哪条假设」。准备时把论文的 negative result 和消融先想一遍。

## 追问

- **只有 45 分钟电面怎么取舍？** 先让代码跑对一个单测，再加 cache / TTL / 并发。半成品但接口干净，好过华丽但错。
- **会不会有纯 LeetCode？** 会，尤其 Meta / Amazon / Microsoft 的通用软件轮。LLM 岗不要因此放弃中等题，但主战场仍是 ML coding 和系统。
- **Take-home？** 少数 Applied 岗有。按招聘邮件来，不要在论坛找「标准答案包」。
