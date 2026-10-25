---
id: slime-pd-disagg
section: systems
order: 261
level: A
title: slime 什么时候上 PD 分离？`--prefill-num-servers` 和 `--sglang-config` 怎么选？
quick: "长上下文多轮任务里，prefill 拖慢 decode，或两边需要不同 TP、机型时，再考虑 PD 分离。简单实验用 `--prefill-num-servers`，生产用 `--sglang-config` 分别配置 worker；短单轮通常承担不起额外 KV 传输和调度开销。"
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

当长上下文的 prefill 挡住 decode，或者两者需要不同并行度和机型时，才值得拆 PD。它调整的是 SGLang 采样轨迹（rollout）池，Megatron 训练图保持原样：输入预填充（prefill，即处理输入并建立缓存）重吞吐，逐 token 生成（decode）更需要 KV 空间和较低 TP。短 GSM8K、卡少或 colocate 显存已很紧的任务，额外的 KV 传输和调度反而可能增加耗时。相关机制见 `sys-chunk-pd`、`sys-prefill-decode`。

强化学习（RL）rollout 的工具历史会把输入提示（prompt）拉得很长，decode 还会有长尾，负载形态和监督微调（SFT）的一批短 completion 不同。同一张卡上，一条 $8\mathrm{k}$ prefill 会长时间占用计算资源，让正在生成的请求等待，每个 token 的生成间隔突然变长。要拆的信号：

- 多轮 / 长上下文，prefill 占实际耗时
- decode 要更低 TP、更高 `mem_fraction_static` 给 KV
- prefill / decode 想用不同并行度或不同机型

不要拆：短单轮、卡少、一体 offload 已经很紧。验收看 prefill QPS、decode tokens/s、prefix hit，不看「上了 PD」。

简单的单 actor 实验可以先设 `--prefill-num-servers 1`，把角色拆开。生产配置用 `--sglang-config`，分别写 `worker_type: prefill|decode`，为两边设置 `num_gpus`、`num_gpus_per_engine` 和 `overrides`，例如给 decode 更高的 `mem_fraction_static`。

同一 model 不要混 `regular` 和 PD worker。`--rollout-num-gpus` 必须等于 YAML 总卡，否则 router 配置与实际 GPU 数量不一致。多轮必须开 session affinity，否则 PD 拆开会把前缀缓存和 KV 打散，见 `slime-router-session`。

veRL 侧对应「rollout 用 SGLang 多轮 / PD」，不是 HybridEngine。Chunked prefill 是同卡把长 prompt 切块、与 decode 混排，不传 KV；PD 是跨池传 KV。短任务先 chunk，长多轮、角色不对称再 PD。KV 传输本身可能比算子贵，网络和 cache placement 要单独算；InfiniBand 上 8k 上下文的 KV 复制，有时已经接近一次 prefill 的实际耗时。

## 追问

**短 GSM8K 上 PD 会怎样？**
多一次 KV 传输和两套调度，几乎没有角色不对称，实际耗时通常更差。
**为什么不能混 regular 和 PD？**
router 的路由假设和 KV 传递协议不同，混用会把请求打到没有对应 KV 的 worker。
**`--rollout-num-gpus` 填错？**
必须等于 YAML 里所有 PD worker 的卡之和。少填则部分 engine 不起，多填则空占卡。
**PD 和 colocate 能一起开吗？**
理论上分角色仍可同机，但 offload 开销和 KV 传输开销会叠加，先分卡再拆 PD 更常见。
