---
id: slime-sglang-native
section: systems
order: 254
level: A
title: slime 为什么死磕 SGLang？`--sglang-` 前缀和 BF16 训 + FP8 rollout 怎么讲？
quick: >-
  slime 专用 SGLang 后端，让 cache-aware router、PD 分离、原生 weight-sync 和 FP8 KV
  都能直接配置。SGLang 的 flag 加 `--sglang-` 前缀透传；大 MoE 常用 Megatron BF16 训练、SGLang FP8
  sampling，长上下文再考虑 `--sglang-kv-cache-dtype fp8_e4m3`。
tags:
  - slime
  - SGLang
  - FP8
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: slime 文档
    url: 'https://thudm.github.io/slime/zh/index.html'
    type: primary
---

slime 绑定 SGLang，是为了直接配置它的 router、PD、delta 同步和 engine 内 DP attention。veRL 为了兼容 FSDP+vLLM、Megatron+SGLang，需要公共层；slime 省去这层后，可以更直接地使用后端特有能力。

公共抽象只能保留公约数：连续 batch、基本 prefix cache。SGLang 的 cache-aware router、PD 角色、原生 weight-sync、FP8 KV 往往被抹平。slime 绑死 SGLang，这些能力有了专门配置开关，而不是插件。选型时可以对照 `sys-verl-vllm-vs-sglang`、`sys-verl-vs-slime`，看 serving 拓扑需要哪些能力。

代价是迁移成本：已经绑 vLLM 的栈要换引擎，或走 external engine 自己对齐协议。

SGLang 的 flag 加 `--sglang-` 前缀，例如 `--mem-fraction-static` 写成 `--sglang-mem-fraction-static`。`--rollout-num-gpus-per-engine` 单独存在，是一个 engine 的世界卡数，不要再发明 `--sglang-tp-size` 当世界大小。填错则 router 和 engine 对不上，见 `slime-colocate-vs-split`。

没文档的 SGLang 开关，先确认 slime 是否透传；不要假设「能传给 SGLang 的都能当 slime CLI」。

大规模 MoE 常见：Megatron BF16 训练态稳，SGLang FP8 sampling 抬 throughput 和 KV 容量；长上下文再 `--sglang-kv-cache-dtype fp8_e4m3`。代价是 rollout 分布与训练图不一致，必须 Megatron 侧重算 logp，并监控量化前后 奖励分数（reward） / KL。这和 Infra「rollout 量化」是同一句话，slime 做成默认 MoE recipe。FP8 KV 改变的是存储精度，公式仍是 exact attention，只是 $K/V$ 的表示更粗。

## 追问

**为什么不用 vLLM？**
不是 vLLM 慢，是公共层吃不到 router / PD / 原生 sync。已有 vLLM 集群用 veRL 或 slime external 更合适。
**BF16+FP8 要不要重算 logp？**
要。sampling 分布和训练图数值不同，ratio 必须基于训练图的 $\log\pi$。
**`--sglang-tp-size` 能当世界大小吗？**
不能。世界卡数用 `--rollout-num-gpus-per-engine`。
**FP8 KV 会改生成分布吗？**
会有数值差，尤其长上下文。要对照 BF16 KV 的 reward / KL，不能只看 throughput。
