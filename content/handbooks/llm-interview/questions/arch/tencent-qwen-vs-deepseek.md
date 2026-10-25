---
id: tencent-qwen-vs-deepseek
section: arch
order: 201
level: A
title: 腾讯混元一面：Qwen 和 DeepSeek 差在哪，什么时候你会换底座？
quick: "我会分架构、数据和后训练三块比。架构上 Qwen 系常用 GQA，有稠密也有常规 MoE；DeepSeek 用 MLA 压缩 KV，再加细粒度专家和共享专家。长上下文看缓存成本，中文指令和工具调用看后训练效果，最后用同一套评测决定换不换底座。"
tags:
  - Tencent
  - Hunyuan
  - Qwen
  - DeepSeek
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 日常实习 腾讯混元大模型一面 好难
    url: https://www.nowcoder.com/feed/main/detail/8066dff3170547c98738ed3b1ba1b496
    type: candidate-first-hand
---

Qwen 和 DeepSeek 我会分架构、数据和后训练三块来比，换不换底座最后拿同一套评测说话。架构上最好讲清的两点是注意力和 MoE：Qwen 系常用 GQA，有稠密模型也有常规 MoE；DeepSeek 用 MLA 压缩 KV，再配细粒度专家和共享专家。光背参数量、或者复述博客里「DeepSeek 更强」，面试官听不到你的判断。

## 架构：GQA 对 MLA，常规 MoE 对细粒度加共享专家

先说注意力。Qwen 系常用 GQA，减少 KV 头数，实现简单，也兼容标准 RoPE。DeepSeek-V2/V3 用 MLA，把 K/V 压成低维的潜在表示，RoPE 单独处理，推理时靠矩阵吸收，不用还原完整的 K/V。比如一个长上下文、大 batch 的服务，逐 token 生成（decode）每一步都要读缓存，缓存带宽的差别会很明显；短上下文的小模型上，GQA 往往就够用了。MLA 原理见 `arch-mla`。

再说 MoE。DeepSeek 是细粒度专家加共享专家，负载均衡有 aux 和无 aux 的变体，见 `arch-moe-noaux`。Qwen-MoE 更接近常规 top-$k$。选型时我会问三件事：有没有共享专家兜底，专家粒度多大，训练和推理的路由是否一致。

其他因素也会影响「能不能上线」：词表和 tokenizer、MTP 或推测解码、开源推理栈的成熟度（比如 vLLM 对 MLA 和 GQA 的支持）。一面先把注意力和 MoE 两条讲完就行。报参数时别把「总参数 671B」和「激活 37B」混在一起，DeepSeek 的卖点就是激活小、容量大，见 `minimax-param-breakdown`。

## 后训练，以及什么时候换底座

DeepSeek-R1 这类推理向的模型，用规则奖励和两阶段训练（监督微调（SFT）冷启动，再做强化学习（RL）），把长思维链训得很重。要长 CoT、竞赛数学、省 KV 的场景，我会先试它。Qwen 指令版在中文对齐、工具调用和开箱模板上往往更省事；要稳定的 function call、做中文产品、或者要用 Qwen-VL 多模态生态，先试它。数据和许可也要早看：商用和蒸馏条款、能不能继续训练，可能在比排行榜分数之前就把选择范围定死了。

真要换的时候，我会用同一组输入提示比较指令跟随、工具调用、长上下文和安全表现，测 decode 延迟和 KV 缓存开销，再看自己的后训练主要靠 SFT，还是靠基于可验证奖励的强化学习（RLVR）。这一步会影响结论：R1 风格的底座接短指令 SFT，可能把格式弄坏；Qwen 直接接纯推理 RL，可能不如从 R1 冷启动。最后靠对照实验定，别靠「听说换了就涨」。

## 追问

**MLA 是不是一定更好？**
它好在缓存。代价是实现和 kernel 的成熟度，以及短序列上的额外开销。小模型、短上下文用 GQA 更简单。

**共享专家是什么？**
每个 token 都会经过的专家，用来学公共能力，减少对路由结果的依赖。常规 top-$k$ 没有这层兜底。

**什么时候不换？**
现有底座在你们的评测上已经够用、工具协议已经对齐、换底座要重做全部后训练的时候。换底座的成本在数据和配方上，下载权重是最便宜的一步。

**和混元自研底座怎么比？**
还要算上内部数据和推理栈的差异。开源底座适合用来对齐公开结果，内部基线还是要保留。

**后训练的差距能不能靠 SFT 抹平？**
能抹平一部分，比如格式和中文。推理深度和 cache 结构抹不平。该换架构就换，该补数据就补。

## 真题记录

这题来自腾讯混元大模型日常实习一面的牛客候选人原帖，可信度 A，原话是 **“Qwen 和 DeepSeek 有什么区别？你会怎么选底座？”**。

相关：`tencent-moe-vs-dense`、`arch-mla`
