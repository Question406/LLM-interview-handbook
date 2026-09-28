---
id: sys-verl-vllm-vs-sglang
section: systems
order: 240
level: A
title: veRL 里 rollout 用 vLLM 还是 SGLang？多轮 Agent 怎么选？
quick: >-
  单轮数学/代码两者都能跑，改 `rollout.name`。多轮工具、结构化输出、和 serving 对齐时 SGLang
  更常被点名；纯吞吐 + PagedAttention 熟路用 vLLM。无论哪个，采样 logp 都要在训练图重算，同步后都要 flush
  KV。
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

Infra 面经会问「vLLM / SGLang 的 continuous batching」：请求结束立刻插入新序列，避免短序列空等。这是引擎层，见 `sys-cont-batch`，和「异步 RL」不是一层。这块容易答「SGLang 一定更快」或「vLLM logp 更准所以拿去更新」。选引擎是因为生成是墙钟大头；数值上 ratio 仍要回训练图。两者都做 paging 和连续 batch，选型差在生态、多轮工具、以及你 serving 已经绑了谁，不在「谁的 kernel 赢了 5%」。我先报负载（单轮数学还是多轮 Agent）和现有 serving 栈，再报 `rollout.name`。快来自引擎，对齐来自训练图；承诺「又快又数值对齐」会在下一问重算 logp 时穿帮。进程组冲突看起来像 NCCL hang，先隔离 communicator 再换引擎。

## 怎么切

veRL 切换：`actor_rollout_ref.rollout.name=sglang` 或 `vllm`。单轮数学 / 代码 GRPO，两者都能跑，先看团队镜像和熟悉程度。SGLang worker 文档强调和 vLLM 功能对齐（省显存、多节点），并单独做了 multi-turn / 工具。TP 初始化会 `init_process_group`，多模块共存时进程组冲突是常见翻车，hang 看起来像 NCCL，其实是 communicator 混用，见 `sys-distributed-hang`。

我会这样选：

- 团队 serving 已是 SGLang → RL 用同一引擎，少两套数值、少两套权重同步协议。
- 只要 GRPO 数学题、现成 vLLM 镜像、PagedAttention 熟路 → 不必换。
- 多轮工具、结构化输出、constrained decoding、cache-aware router、PD 分离 → SGLang 更常被点名。
- 已经走 slime 的人默认就是 SGLang，这不是「veRL 不能 SGLang」，是栈收窄了，见 `sys-verl-vs-slime`。

别用微基准上几个百分点的 tokens/s 决定。RL 负载是组内 $n$ 条、变长 CoT、还要周期性 `update_weights`。引擎快，同步慢，一步仍然慢，见 `infra-rl-weight-sync`。FP8 / 量化 rollout 时，两边的数值漂移都可能进 $\rho$，更不能用「引擎 logp」当训练信号。多节点 TP 下，SGLang 的 router 和 PD 是加分项；纯单机 8 卡数学 GRPO，vLLM 的成熟镜像往往更少踩坑。进程组冲突出现时不要先换引擎：先隔离 communicator。换引擎解决不了 WORLD 被占。报选型时带一句「我们 serving 是 X，所以 RL 用 X，少两套权同步」，这比报跑分更像生产决策。

## 多轮 Agent 为什么偏 SGLang

多轮不是多次单轮拼接。要在同一条 session 里保留 KV、插入 tool observation、按 schema 约束解码。SGLang 的程序化生成 / router 对这类状态机更顺；vLLM 也能接工具，但和 serving 侧若已经是 SGLang 协议，RL 再自研一套 multi-turn worker 是重复税。Agent 的墙钟还含环境延迟，引擎差距可能小于 sandbox，先 profile 再换引擎。

无论哪个引擎：采样 logp 都要在训练图重算；同步后都要 flush KV、记 `policy_version`。量化（尤其 FP8 rollout）会让引擎 logp 和 FSDP/Megatron 差出能进 $\rho$ 的误差。正确拆法是采样用快引擎，ratio / KL 用训练图，见 `meituan-verl-recompute-logprob`。

## 和放置的关系

同卡 HybridEngine：两种引擎都是「采完卸 KV、reshard 回训练」。分卡：引擎常驻，训练另一套，按步推权。OpenRLHF 更常绑独立 vLLM actor；slime colocate 绑 SGLang server + offload。引擎选择和放置选择正交：可以 vLLM + HybridEngine，也可以 SGLang + 分卡。我先报负载（单轮 vs 多轮），再报放置，最后才报名字。多轮 Agent 的状态机（session、tool、schema）才是 SGLang 常被点名的原因；把这一点说成「SGLang 更快」会被追问 benchmark 拆穿。结构化输出、constrained decoding 同样偏 SGLang 的程序化生成；纯补全、无工具，vLLM 完全够。选完之后仍要：同步 flush KV、训练图重算 logp、profile generate vs sync vs backward。

单轮数学/代码：团队镜像是谁就用谁，改 `actor_rollout_ref.rollout.name`。多轮工具、结构化输出、serving 已是 SGLang：偏 SGLang。纯吞吐熟路、现成 vLLM：不必换。slime 默认 SGLang 是栈收窄，不是 veRL 不能接 SGLang。microbenchmark 快 5% 不能当理由。

## 追问

- **Continuous batching 谁有？** 两者都有。这不是选型差异，是为什么不用训练图 `generate`。把这一点说成「所以选 SGLang」会被追问 vLLM 为什么也能连续 batch。
- **SGLang 能不能跳过重算 logp？** 不能。数值图仍是推理引擎的，量化尤其 FP8 会让 $\rho$ 漂移。slime 默认 SGLang 同样要在 Megatron 上重算，见 `meituan-verl-recompute-logprob`。
- **进程组冲突怎么发现？** 训练 hang 在 init 或第一次 collective，而单跑 trainer / 单跑引擎都正常。隔离默认组，给引擎单独的 communicator，见 `sys-distributed-hang`。换引擎解决不了 WORLD 被占。
- **一定要为 Agent 换 SGLang 吗？** 不是。已有稳定的 vLLM 多轮栈、工具协议已经对齐，换引擎的迁移成本可能大于收益。Agent 墙钟还常在 sandbox，先 profile。
- **和放置怎么组合？** 正交。可以 vLLM + HybridEngine，也可以 SGLang + 分卡。OpenRLHF 更常绑独立 vLLM；slime colocate 绑 SGLang + offload。先报负载和 serving 现状，再报名字。
- **微基准快 5% 能当理由吗？** 不能。RL 一步还含 `update_weights` 和重算 logp。引擎快、同步慢，一步仍然慢。用分段计时，不要用纯 serving tokens/s。
- **FP8 rollout 怎么选引擎？** 两边都能量化，数值漂移都会进 $\rho$，更不能跳过训练图重算。选你 serving 已经在用、权同步协议更熟的那个，量化是附加约束不是选型主因。
- **多轮 session 的 KV 要不要跨步保留？** 要，否则每轮重 prefill。SGLang 对 session / 工具插入更顺；若 vLLM 侧已经有稳定的多轮 worker，不必为了「更现代」而换。先报现有协议。
- **面试怎么选？** 单轮数学/代码跟团队镜像走；多轮工具、结构化输出、serving 已是 SGLang 则偏 SGLang。无论哪个：采样用快引擎，ratio 用训练图，同步后 flush KV。continuous batching 两者都有，那不是选型差异。进程组冲突先隔离 communicator。
