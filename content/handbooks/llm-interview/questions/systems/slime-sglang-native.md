---
id: slime-sglang-native
section: systems
order: 254
level: A
title: slime 为什么死磕 SGLang？`--sglang-` 前缀和 BF16 训 + FP8 rollout 怎么讲？
quick: >-
  单一推理后端才能把 router 的 cache-aware 调度、PD 分离、FP8 KV、原生 weight-sync 用满，避免接口只保留
  vLLM/SGLang 共有的能力。SGLang 的 flag 加 `--sglang-` 前缀透传。大规模 MoE 常见 Megatron BF16
  训练态 + SGLang FP8 采样；长上下文再 `--sglang-kv-cache-dtype fp8_e4m3`。
tags:
  - slime
  - SGLang
  - FP8
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime 文档
    url: https://thudm.github.io/slime/zh/index.html
    type: primary
---

常见误区是：把「slime 更轻」说成少写了几行抽象，却落不到具体能力。veRL 为了 FSDP+vLLM 和 Megatron+SGLang 都能跑，必须做公共层；slime 拿掉这层，换的是 SGLang 特有能力：router 按前缀切流、PD、delta 同步、engine 内 DP attention。说「更轻」要落到这些，否则下一问「那为什么不用 vLLM」答不上。

## 单一后端换来什么

公共抽象只能保留公约数：连续 batch、基本 prefix cache。SGLang 的 cache-aware router、PD 角色、原生 weight-sync、FP8 KV 往往被抹平。slime 绑死 SGLang，这些能力有了专门配置开关，而不是插件。面试对照 `sys-verl-vllm-vs-sglang`、`sys-verl-vs-slime`：选 slime 是因为 serving 拓扑，不是因为「不想写 HybridEngine」。

代价是迁移成本：已经绑 vLLM 的栈要换引擎，或走 external engine 自己对齐协议。

## `--sglang-` 怎么透传

SGLang 的 flag 加 `--sglang-` 前缀，例如 `--mem-fraction-static` 写成 `--sglang-mem-fraction-static`。`--rollout-num-gpus-per-engine` 单独存在，是一个 engine 的世界卡数，不要再发明 `--sglang-tp-size` 当世界大小。填错则 router 和 engine 对不上，见 `slime-colocate-vs-split`。

没文档的 SGLang 开关，先确认 slime 是否透传；不要假设「能传给 SGLang 的都能当 slime CLI」。

## BF16 训 + FP8 采样轨迹（rollout）

大规模 MoE 常见：Megatron BF16 训练态稳，SGLang FP8 采样抬吞吐和 KV 容量；长上下文再 `--sglang-kv-cache-dtype fp8_e4m3`。代价是 rollout 分布与训练图不一致，必须 Megatron 侧重算 logp，并监控量化前后 奖励分数（reward） / KL。这和 Infra「rollout 量化」是同一句话，slime 做成默认 MoE recipe。别把 FP8 KV 说成改了 attention 数学，它改的是存储精度；公式仍是 exact attention，只是 $K/V$ 更粗。

## 追问

- **为什么不用 vLLM？** 不是 vLLM 慢，是公共层吃不到 router / PD / 原生 sync。已有 vLLM 集群用 veRL 或 slime external 更合适。
- **BF16+FP8 要不要重算 logp？** 要。采样分布和训练图数值不同，ratio 必须基于训练图的 $\log\pi$。
- **`--sglang-tp-size` 能当世界大小吗？** 不能。世界卡数用 `--rollout-num-gpus-per-engine`。
- **FP8 KV 会改生成分布吗？** 会有数值差，尤其长上下文。要对照 BF16 KV 的 reward / KL，不能只看吞吐。
