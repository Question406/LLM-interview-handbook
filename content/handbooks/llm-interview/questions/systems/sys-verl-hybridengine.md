---
id: sys-verl-hybridengine
section: systems
order: 235
level: S
title: veRL 的 HybridEngine 解决什么？和 OpenRLHF 把 vLLM 单独拉一套有何不同？
quick: >-
  HybridEngine 在同一批 GPU 上把训练分片重新排成推理 TP 布局，减少完整权重副本和全局 all-gather。OpenRLHF 用独立
  Ray actor 部署 vLLM，生成池可异构扩容，但需要额外驻留模型并同步权重。选哪种，要看显存、拓扑和能否接受训练与生成串行。
tags:
  - VeRL
  - OpenRLHF
  - HybridEngine
  - vLLM
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: HybridFlow
    url: 'https://arxiv.org/abs/2409.19256'
    type: primary
  - title: verl
    url: 'https://github.com/verl-project/verl'
    type: primary
  - title: OpenRLHF
    url: 'https://github.com/OpenRLHF/OpenRLHF'
    type: primary
---

## 可以这样回答

HybridEngine 解决的是同一批 GPU 怎样既训练又生成，并尽量少存一份完整模型。比如在同构 8 卡上训练 70B，如果再给 rollout 留一份整模，显存可能就不够了；它通过对齐训练分片和推理 TP 布局，在两种布局之间重新分片（reshard）。

省权重副本和重叠计算要分别看。默认一步内训练与生成串行：sampling 完卸 KV，reshard 回训练布局，再 backward 更新，同卡不能同时做两件事。长 rollout 时生成可能占据大部分耗时，训练算子要等待。Fully async 是另外增加的路径，能重叠 sampling 和更新，却引入 policy staleness，需要单独核对 freshness。

## 技术备查

HybridEngine 解决的是同一批 GPU 怎样既训练又生成，并尽量少存一份完整模型。比如在同构 8 卡上训练 70B，如果再给 rollout 留一份整模，显存可能就不够了；它通过对齐训练分片和推理 TP 布局，在两种布局之间重新分片（reshard）。

训练时常用 FSDP 或 Megatron TP/PP，生成时 vLLM / SGLang 需要推理 TP 和 PagedAttention。DeepSpeed-Chat 一类朴素路径先 gather 成整模，再切给推理，峰值会多出一份完整权重，跨机 all-gather 也很大。HybridFlow / veRL 的 3D-HybridEngine 让生成并行组与训练分片重叠，本卡已有 shard 直接复用，只在重叠的 micro-DP 组内补齐需要的切片。这样减少完整副本和全局收集，尤其适合同构的 70B 级以上模型。若切分对不齐，仍会退回近乎全量 gather，这个收益也就消失了。

省权重副本和重叠计算要分别看。默认一步内训练与生成串行：sampling 完卸 KV，reshard 回训练布局，再 backward 更新，同卡不能同时做两件事。长 rollout 时生成可能占据大部分耗时，训练算子要等待。Fully async 是另外增加的路径，能重叠 sampling 和更新，却引入 policy staleness，需要单独核对 freshness。

Reshard 只解决布局，weight sync 解决权重版本，recompute 解决训练图上的 logp。sampling logp 仍需在训练图重算，少了任何一步，都可能让 ratio 产生不易察觉的偏差。

## 和分卡部署怎么选

OpenRLHF 让训练走 DeepSpeed ZeRO，把 vLLM 放在独立 Ray actor 和另一组 GPU 上。生成节点可以使用不同规格的卡，比如更重视显存带宽的卡负责 decode，生成池也能按 rollout 瓶颈单独扩容。代价是另一份模型驻留，以及每步跨进程 / 跨机同步权重、flush KV 和记录版本。

所以同构、卡紧、大模型时，我会优先评估 HybridEngine；已经有独立推理池，或生成与训练需要异构扩容且能接受同步延迟时，会考虑 OpenRLHF 式分池。两者都能用 vLLM，差别是权重有几份、卡怎么分和一步是否串行。现有 SGLang router / PD / delta 同步若是硬需求，分卡或 slime 也可能更合适，要先画资源拓扑。

slime 的 `--colocate` 则是同卡上的两个进程：Megatron trainer 与 SGLang server，用 `--offload-train` / `--offload-rollout` 轮流释放显存。它是时分复用与 offload，process boundary 仍在；HybridEngine 是同进程换并行组、原地 reshard。Offload 会在 PCIe / NVLink 上搬优化器状态和 KV，一步可能出现两段拷贝等待。卡内带宽充足时可以接受，跨 NUMA 或 PCIe 代差大时，colocate 可能比分卡慢，必须 profile 拷贝。

同卡也仍需容纳训练分片及优化器、生成 KV 和 reshard 临时缓冲。权重少一份，不代表 `rollout.n` 能无限增大；长 chain of thought（CoT）的 KV 会成为下一个瓶颈，需要动态 batch 和 inflight 序列限制。分卡则把 KV 留在生成池、优化器留在训练池，用网络同步换取显存隔离。

验收时把一步拆成 generate / reshard / backward，单独记录切换等待；峰值显存分开看训练分片、KV 和 reshard 缓冲。加速比取决于模型宽度、TP 对齐和是否 async，要从实际 profile 得到。

## 追问

**FSDP 和 Megatron 都能走 HybridEngine 吗？**
可以。推理仍是 vLLM/SGLang 的 TP，改变的是训练 shard。Megatron 带 PP 时，还要对齐流水线阶段与推理 TP，因此配置更复杂。

**70B 就一定选 veRL 吗？**
不一定。已有独立推理集群，或者 router / PD / delta 同步是硬需求时，分卡或 slime 可能更合适。模型规模、卡数、同构程度和能否接受串行要一起看。

相关：`sys-rl-why-vllm-rollout`、`sys-rl-infra`、`meituan-verl-recompute-logprob`、`infra-rl-weight-sync`、`slime-colocate-vs-split`、`sys-verl-vs-slime`、`sys-verl-dynamic-bsz`
