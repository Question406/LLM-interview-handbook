---
id: sys-verl-hybridengine
section: systems
order: 235
level: S
title: veRL 的 HybridEngine 解决什么？和 OpenRLHF 把 vLLM 单独拉一套有何不同？
quick: >-
  HybridEngine 让同一批 GPU 在训练分片布局和推理 TP 布局之间原地 reshard，少存一份完整权重，通信也比全 rank
  all-gather 小。OpenRLHF 把 vLLM 放成独立 Ray actor，可异构扩容，但要多占卡、同步权重。70B+
  同构集群偏 veRL；要隔离生成节点偏 OpenRLHF。
tags:
  - VeRL
  - OpenRLHF
  - HybridEngine
  - vLLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: HybridFlow
    url: https://arxiv.org/abs/2409.19256
    type: primary
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
  - title: OpenRLHF
    url: https://github.com/OpenRLHF/OpenRLHF
    type: primary
---

要说清的是同卡换布局 vs 分卡扩容：RL 一步里 Actor 既要 backward，又要高吞吐 decode，两套并行布局本来就不同。选错放置，显存和通信会先爆，而不是算法不收敛。生成为什么必须用推理引擎，见 `sys-rl-why-vllm-rollout`。HybridEngine 做的是同一份权重在两种并行方案之间 reshard，一步内仍然串行，不是「训练和推理融合成一个更快的算子」。开口把「少存一份整模」和「一步能否重叠」分开，再比较 OpenRLHF / slime。

## HybridEngine 在省什么

训练侧常见 FSDP 或 Megatron TP/PP，权重按训练并行切开；生成侧 vLLM / SGLang 要的是推理 TP 布局和 PagedAttention。DeepSpeed-Chat 一类朴素做法会先把参数 gather 成整模再切开给推理，峰值显存多一份完整权重，跨机 all-gather 也大。70B 以上时，多一份整模往往直接 OOM，这才是 HybridEngine 出现的压力，而不是微基准上几个百分点的 MFU。reshard 要正确，训练 shard 和推理 TP 的切分必须能对齐；对不齐就会退回几乎全量 gather，省显存的故事立刻破产。

HybridFlow / veRL 的 3D-HybridEngine 把生成并行组排成和训练分片 **重叠**：本卡已有的 shard 能直接复用，all-gather 缩到 micro-DP 组内，而不是全集群拉一份整模。目的是 **少存一份权重、少一次全局收集**，让同构大模型（尤其 70B 级以上）在同一批 GPU 上既能训又能采。

代价要主动讲：一步之内训练与生成默认串行。同一张卡不能边 backward 边 decode；采样完卸 KV、reshard 回训练布局，再做更新。Fully async 是后加的另一条路径，会引入 policy staleness，和 `sys-rl-infra` 里的 freshness 是同一笔账。串行气泡在长 rollout 时尤其明显：生成占满墙钟，训练 GPU 空转。这时同卡省显存的收益还在，但利用率故事要改口；若业务要叠采样与更新，就该评估分卡或 async。

Reshard 解决的是权重布局；采样 logp 仍要在训练图上重算，见 `meituan-verl-recompute-logprob`。不要把「省显存的换布局」说成「省掉 recompute」。HybridEngine、weight sync、recompute 是三步：布局、版本、训练图 logp。缺一都会在 ratio 上出无声的偏。

## 和 OpenRLHF 分卡怎么选

OpenRLHF 把 vLLM 放成独立 Ray actor：训练走 DeepSpeed ZeRO，生成走另一组 GPU。好处是生成节点规格可以和训练不同（更吃显存带宽的卡专做 decode、训练卡专做 ZeRO），生成池可以按 rollout 瓶颈单独扩。坏处是 **多一份模型驻留**，每步要做跨进程 / 跨机权重同步，并 flush KV、记版本，见 `infra-rl-weight-sync`。

我会这样选：

- **同构、卡紧、大模型：偏 HybridEngine。** 不想为 rollout 再备一套 70B。
- **生成与训练异构、要独立扩容、能接受同步延迟：偏 OpenRLHF 式分池。**

两者都能接 vLLM；差别不在「用不用 vLLM」，在权重有几份、卡怎么切、一步是否串行。同构集群上为了「看起来像 OpenRLHF」强行分卡，会多交一份 70B 显存税；反过来在已经隔离的推理池上硬套 HybridEngine，会把 serving 弹性丢掉。先画资源拓扑，再选引擎粘合方式。

## 不要和 slime `--colocate` 混为一谈

slime 的 `--colocate` 是同卡、两套进程（Megatron trainer + SGLang server），用 `--offload-train` / `--offload-rollout` 轮流把对方挤出显存。这是放置和 offload，不是同进程换并行组。HybridEngine 追求原地 reshard、少一份整模；colocate 追求同卡时分复用、进程边界仍在。对答见 `slime-colocate-vs-split`、`sys-verl-vs-slime`。说「slime 也是 HybridEngine」会被拆穿。Offload 的代价是 PCIe / NVLink 上把优化器状态和 KV 来回搬，一步里会出现两段明显的拷贝气泡。卡内带宽够时可以接受；跨 NUMA 或 PCIe 代差大时，colocate 可能比分卡还慢。选放置要 profile 拷贝，不要只比「省不省卡」。

## 显存账本怎么讲

同卡方案要同时装：训练分片（含优化器状态）、生成所需的 KV、以及 reshard 时的短暂缓冲。HybridEngine 的卖点是权重不双份；KV 和优化器仍然在。所以「省了一份整模」不等于「可以随便开很大的 `rollout.n`」。长 CoT 的 KV 才是下一步瓶颈，要用动态 batch、限制 inflight 序列，见 `sys-verl-dynamic-bsz`。

OpenRLHF 分卡把 KV 放到生成池、优化器放到训练池，账本隔离，同步成本换成网络。被问「你当时为什么选」时，我先报模型规模、是否同构、一步能否接受串行，再报框架名。同构 8 卡训 70B，优先讲 HybridEngine 如何少一份整模；已经有独立推理池，优先讲同步协议和 stale。两种答案都对，取决于拓扑，不存在永远更快的那个框架。被追问 benchmark 数字时，诚实说取决于模型宽度、TP 对齐和是否 async，不要编造加速比。选完之后把一步墙钟拆成 generate / reshard / backward。追问「峰值显存」时，分别报训练分片、KV、reshard 缓冲。HybridEngine 省的是权重副本，KV 仍随 `rollout.n` 和长度走。

## 追问

- **为什么通信能比全 rank all-gather 小？** 生成组与训练 shard 对齐后，只需在重叠的 micro-DP 内补齐推理 TP 需要的切片，不必把整模广播到每个 rank。对不齐时这个优势消失，会退回接近朴素 gather 的成本，所以并行配置是一等公民。
- **串行会不会把 GPU 空闲打满？** 会。采样阶段训练算子停，更新阶段推理引擎停。这是用显存换利用率；异步路径才重叠，但要管 stale trajectory。profile 时要把「切换气泡」单独标出来，不要全部算进 decode。
- **FSDP 和 Megatron 都能走这套吗？** 都能作为训练后端，推理仍是 vLLM/SGLang 的 TP。换后端改的是 shard 形状，不是「要不要 HybridEngine」这个动机。Megatron 还带 PP，reshard 要考虑流水线阶段和推理 TP 怎么对齐，比纯 FSDP 更绕。
- **70B 一定选 veRL？** 不是。若组织上已经有独立推理集群、或 SGLang router / PD / delta 同步是硬需求，分卡或 slime 可能更合适。先报你的卡数、是否同构、能否接受一步串行。框架是放置策略的实现，不是放置策略本身。
