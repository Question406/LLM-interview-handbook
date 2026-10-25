---
id: sys-verl-vllm-vs-sglang
section: systems
order: 240
level: A
title: veRL 里 rollout 用 vLLM 还是 SGLang？多轮 Agent 怎么选？
quick: "单轮数学 / 代码 GRPO，两种引擎都能用，可以跟团队现有镜像走。多轮工具、结构化输出，或 serving 已采用 SGLang 时，更值得沿用 SGLang；无论选谁，都要在训练图重算 logp，同步权重后 flush KV 并记版本。"
tags:
  - VeRL
  - vLLM
  - SGLang
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: AI infra实习面经（小厂）
    url: https://www.nowcoder.com/feed/main/detail/166e576d5afa4a298cf9492ed51bed04
    type: candidate-first-hand
  - title: SGLang Worker — verl
    url: https://verl.readthedocs.io/en/latest/workers/sglang_worker.html
    type: primary
---

单轮数学 / 代码 GRPO，我会先沿用团队现有的 vLLM 或 SGLang 镜像；多轮工具、结构化输出，或者 serving 已经是 SGLang 时，再优先考虑 SGLang。两者都有 paging 和 continuous batching，选型主要取决于负载与现有 serving 协议。

veRL 用 `actor_rollout_ref.rollout.name=sglang` 或 `vllm` 切换，也就是调整 `actor_rollout_ref.rollout.name`，简称 `rollout.name`。SGLang worker 文档强调与 vLLM 对齐省显存、多节点等功能，并单独提供 multi-turn / 工具支持。纯单机 8 卡数学 GRPO，团队熟悉 PagedAttention、已有成熟 vLLM 镜像时，迁移未必有收益。slime 默认 SGLang 是它主动收窄了栈，veRL 本身也能接。

Continuous batching 指请求结束后立即补入新序列，避免短序列结束后整批等待。两种引擎都有，这解释了为什么 rollout 用推理引擎，避免用训练图 `generate` 承担生成；异步 RL 则讨论采样与更新如何重叠，是另一层问题。RL 负载包含组内 $n$ 条、变长思维链（CoT）、周期性 `update_weights` 和重算 logp，纯 serving microbenchmark 快 5%，不能推出整步更快。应把 generate、sync、backward 分开计时。

多轮 Agent 需要在同一 session 中保留 KV、插入工具观测结果（observation），并按 schema 约束解码。SGLang 的程序化生成和 router 更便于表达这类状态机，也常与 constrained decoding、cache-aware router、PD 分离一起使用。若 serving 已是 SGLang，RL 沿用它能减少两套数值与权重同步协议。vLLM 也能做工具调用；已有稳定多轮 worker 和协议时，换引擎可能得不偿失。Agent 时间也可能主要花在 sandbox / 环境延迟上，要先 profile。

无论哪个引擎，采样用快速推理图，ratio / KL 用训练图：采样 logp 都要回 FSDP/Megatron 重算，尤其 FP8 / 量化 rollout 可能产生足以影响 $\rho$ 的差异。同步后 flush KV，记录 `policy_version`，避免旧缓存对应旧权重。多轮 session 内 KV 要保留，否则每轮都要重新处理输入并建立 KV 缓存。

引擎和放置可以独立选择。vLLM + HybridEngine、SGLang + 分卡都成立。同卡 HybridEngine 采样后卸 KV、reshard 回训练；分卡则让引擎常驻，训练侧按步推权。OpenRLHF 常用独立 vLLM actor，slime colocate 常用 SGLang server + offload。回答时先交代单轮还是多轮、现有 serving，再说放置和引擎名。

## 追问

**SGLang 能跳过重算 logp 吗？**
不能。推理图与训练图仍有数值差异，FP8 尤其可能让 $\rho$ 漂移，slime 也要回 Megatron 重算。

**初始化或第一次 collective 挂住，要换引擎吗？**
先查 communicator。如果 trainer 和引擎单跑都正常，合在一起却在 `init_process_group` 或 collective hang，常见原因是默认组混用、WORLD 被占。给引擎隔离 communicator，比换引擎更有针对性。

**FP8 rollout 会改变选型结论吗？**
它增加了数值校验要求，两边的量化漂移都可能进入 $\rho$。仍应选 serving 已用、同步协议更熟的引擎，并重算 logp。

相关：`sys-cont-batch`、`sys-distributed-hang`、`sys-verl-vs-slime`、`infra-rl-weight-sync`、`meituan-verl-recompute-logprob`
