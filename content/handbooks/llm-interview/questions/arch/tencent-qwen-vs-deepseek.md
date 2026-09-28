---
id: tencent-qwen-vs-deepseek
section: arch
order: 201
level: A
title: 腾讯混元一面：Qwen 和 DeepSeek 差在哪，什么时候你会换底座？
quick: >-
  先拆架构、数据与后训练三条线：Qwen 系多是 GQA + 稠密/常规 MoE；DeepSeek 用 MLA
  压 KV、细粒度 MoE 加共享专家。换底座看任务：长上下文推理看 cache 与 MLA，中文指令与工具调用看后训练配方，不要只背参数量。
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

## 真题记录

- 公司：腾讯 · 混元
- 岗位：大模型日常实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“Qwen 和 DeepSeek 有什么区别？你会怎么选底座？”**

错法：只背参数量或复读博客「DeepSeek 更强」。对照只讲你能辩护的点：注意力、MoE、后训练。换底座用同一套评测集，不要用社交媒体结论替实验。同面 MoE 题见 `tencent-moe-vs-dense`；MLA 原理见 `arch-mla`。

## 架构：GQA vs MLA，常规 MoE vs 细粒度 + 共享专家

- 注意力：Qwen 系常用 GQA，少 KV 头、实现简单、和标准 RoPE 兼容。DeepSeek-V2/V3 用 MLA：把 K/V 压进低维 latent，RoPE 拆开，推理靠矩阵吸收不必物化全长 K/V。长上下文、大 batch decode 时 cache 带宽差一档；短上下文小模型上 GQA 往往够用。
- MoE：DeepSeek 细粒度专家 + 共享专家 + 负载均衡（aux / 无 aux 变体，见 `arch-moe-noaux`）。Qwen-MoE 更接近常规 top-$k$。选型时问：有没有共享专家兜底、专家粒度、训推路由是否一致。
- 其它：词表与 tokenizer、MTP / 推测解码、是否开源推理栈（vLLM 对 MLA/GQA 的成熟度）也会左右「能不能上线」，但一面先把注意力和 MoE 两条讲完。

不要把「总参数 671B」和「激活 37B」混报；DeepSeek 的卖点是激活小、容量大，见 `minimax-param-breakdown`。

## 后训练与何时换底座

- DeepSeek-R1 / 推理向：规则奖励、两阶段（SFT 冷启动 → RL）把长思维链训得很重。要长 CoT、竞赛数学、省 KV 时优先试。
- Qwen 指令版：中文对齐、工具调用、开箱模板往往更省事。要稳定 function call、中文产品、多模态 Qwen-VL 生态时优先试。
- 数据与许可：商用、蒸馏条款、是否能继续训，比 leaderboard 分更早卡死选型。

换底座清单：同一 prompt 集看 instruction / tool / long-context / 安全；看 decode 延迟与 KV；看你们后训练配方是 SFT 为主还是 RLVR。R1 风格底座接短指令 SFT 可能把格式弄坏；Qwen 接纯推理 RL 可能不如从 R1 冷启动。最终对照实验，不要靠「听说换了就涨」。

## 追问

- **MLA 是不是一定更好？** 更好的是 cache；实现与 kernel 成熟度、短序列开销是代价。小模型短上下文 GQA 更简单。
- **共享专家是什么？** 每 token 必走的专家，减轻路由全责，稳定公共能力。常规 top-$k$ 没有这层兜底。
- **什么时候不换？** 现有底座在你们评测上已够、工具协议已对齐、换底座要重做全部后训练。换的成本是数据与配方，不是下载权重。
- **和混元自研底座怎么比？** 承认内部数据与推理栈是第三轴；开源底座用来对齐公开结果，不是替代内部基线。
- **后训练差能否用 SFT 抹平？** 部分可以（格式、中文），推理深度和 cache 结构抹不平。该换架构时换，该补数据时补。
