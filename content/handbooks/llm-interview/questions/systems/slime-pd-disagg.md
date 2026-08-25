---
id: slime-pd-disagg
section: systems
order: 261
level: A
title: slime 什么时候上 PD 分离？`--prefill-num-servers` 和 `--sglang-config` 怎么选？
quick: >-
  长上下文、多轮、decode 占墙钟、prefill/decode 要不同 TP 时再拆。玩具路径
  `--prefill-num-servers`；生产用 `--sglang-config` 分别写 `worker_type: prefill|decode`。短单轮别拆。同一
  model 里不要混 `regular` 和 PD worker；`--rollout-num-gpus` 必须等于 YAML 里的总卡。
tags:
  - slime
  - SGLang
  - PD Disaggregation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime PD 分离
    url: https://thudm.github.io/slime/zh/advanced/pd-disaggregation.html
    type: primary
---

这块容易短 GSM8K、卡很少也上 PD，或把 PD 说成 Megatron 训练环的功能。PD 改的是 **SGLang rollout 池**：prefill 吃吞吐、decode 吃 KV / 低 TP。训练图不动。短单轮、colocate 已经在抢显存时，拆开会多一份 KV 传输和调度税，墙钟更差。见 `sys-chunk-pd`、`sys-prefill-decode`。

## 什么时候才拆

RL rollout 不像 SFT 一批短 completion：工具史把 prompt 拉得很长，decode 又有长尾。同一张卡上，一条 $8\mathrm{k}$ prefill 会饿死正在飞的 decode，TPOT 出尖刺。要拆的信号：

- 多轮 / 长上下文，prefill 占墙钟
- decode 要更低 TP、更高 `mem_fraction_static` 给 KV
- prefill / decode 想用不同并行度或不同机型

不要拆：短单轮、卡少、一体 offload 已经很紧。验收看 prefill QPS、decode tokens/s、prefix hit，不看「上了 PD」。

## 两条配置路径

- **玩具**：`--prefill-num-servers 1`，单 actor、只想把角色拆开。
- **生产**：`--sglang-config` 里分别写 `worker_type: prefill|decode`，各自 `num_gpus`、`num_gpus_per_engine`、`overrides`（decode 更高 `mem_fraction_static`）。

同一 model 不要混 `regular` 和 PD worker。`--rollout-num-gpus` 必须等于 YAML 总卡，否则 router 和卡账对不上。多轮必须开 session affinity，否则 PD 拆开会把前缀缓存和 KV 打散，见 `slime-router-session`。

## 和 veRL、chunked prefill 的关系

veRL 侧对应「rollout 用 SGLang 多轮 / PD」，不是 HybridEngine。Chunked prefill 是同卡把长 prompt 切块、与 decode 混排，**不传 KV**；PD 是跨池传 KV。短任务先 chunk，长多轮、角色不对称再 PD。KV 传输本身可能比算子贵，网络和 cache placement 要单独算；InfiniBand 上 8k 上下文的 KV 复制，有时已经接近一次 prefill 的墙钟。

## 追问

- **短 GSM8K 上 PD 会怎样？** 多一次 KV 传输和两套调度，几乎没有角色不对称，墙钟通常更差。
- **为什么不能混 regular 和 PD？** router 的路由假设和 KV 传递协议不同，混用会把请求打到没有对应 KV 的 worker。
- **`--rollout-num-gpus` 填错？** 必须等于 YAML 里所有 PD worker 的卡之和。少填则部分 engine 不起，多填则空占卡。
- **PD 和 colocate 能一起开吗？** 理论上分角色仍可同机，但 offload 税和 KV 传输叠在一起，先分卡再拆 PD 更常见。
