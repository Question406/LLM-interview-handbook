---
id: slime-colocate-vs-split
section: systems
order: 251
level: S
title: slime 训推一体和训推分离怎么配？和 veRL HybridEngine 是一回事吗？
quick: >-
  默认分离：Ray 按 `--actor-num-nodes × --actor-num-gpus-per-node` 给 Megatron，按
  `--rollout-num-gpus` 给 SGLang。`--colocate` 让两边共享卡，可用 `--offload-train` /
  `--offload-rollout` 互斥占显存。这不是 HybridEngine：slime 仍是两套进程（Megatron trainer +
  SGLang server），一体只是放置和 offload，不是同进程换并行组。
tags:
  - slime
  - VeRL
  - Placement
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
---

这块容易说「slime 也有 HybridEngine」。HybridEngine 追求 **同卡、同进程、换布局、少一份整模**。slime `--colocate` 追求 **同卡、两进程、offload 轮流上班**。分离时 slime 更像 OpenRLHF 的分池，再用 NCCL / 磁盘 / delta 同步。说成一回事会被拆穿，见 `sys-verl-hybridengine`、`sys-verl-vs-slime`。面试官若追问「那为什么还叫训推一体」，我会答：一体指的是 **放置**（同一批 GPU 时分复用），不是 **运行时融合**。进程边界、CUDA context、通信组都还是两套。资源账本先写启动参数：分离是加法，一体是时分复用加 offload 税。profile 拷贝气泡，若已经接近 generate，省卡是假省。

## 分离怎么配

资源账本先写在启动参数上，不要事后在 Ray 里猜。默认训推分离：

- Megatron actor：`--actor-num-nodes × --actor-num-gpus-per-node`
- SGLang rollout：`--rollout-num-gpus`
- `--rollout-num-gpus-per-engine` 是 **一个 SGLang engine 的世界卡数**。多机 serving 填总卡，不是「单机 tp 再乘节点」。填错会让 router 和 engine 的世界大小对不上。

分离的好处是生成池可以按 decode 瓶颈单独扩、训练卡不用卸 KV。坏处是 **两份权驻留**，每步 `update_weights`，见 `infra-rl-weight-sync`、`slime-weight-sync`。`--rollout-num-gpus 0` 只起 router，接外部 engine，适合已经有独立 SGLang 集群。

## `--colocate` 在做什么

`--colocate` 让两边共享卡：默认训推卡数相等，并且会打开 `--offload`（等价 `--offload-train` + `--offload-rollout`）。也可让 rollout 卡多于 actor，多出来的是 rollout-only。显存互斥：

- 训练阶段 offload SGLang（含 KV / CUDA graph）
- 采样阶段 offload Megatron（含优化器状态）

`--sglang-mem-fraction-static` 常降到 0.8 左右，给两边各留一点，否则两套权在切换瞬间叠爆。Offload 的代价是 PCIe / NVLink 上把优化器状态和 KV 来回搬，一步里会出现两段拷贝气泡。卡内带宽够时可以接受；跨 NUMA 或 PCIe 代差大时，colocate 可能比分卡还慢。选放置要 profile 拷贝，不要只比「省不省卡」。

一体时训推仍 **串行**：同一张卡不能边 backward 边 decode。别把 `--colocate` 说成异步 RL，见 `slime-async-train`。Offload 没配对是最常见的 OOM：只开 `--offload-rollout` 却在训练阶段忘了把 SGLang 的 KV / CUDA graph 卸掉，两套权叠在同一张卡上。反过来，采样阶段 Megatron 优化器状态还在 HBM，SGLang 的 `mem-fraction-static` 再按 0.9 预留，切换瞬间爆。官方 `--colocate` 默认打开双边 offload，就是为了避免这种「以为一体、其实双驻留」。手动拆开关时必须按阶段互斥。拷贝气泡要单独 profile：H100 上 NVLink 搬 70B 分片和 PCIe 搬优化器状态完全不是一个数量级，跨 NUMA 再降一档。选 colocate 之前用一次空跑看 offload 占比，若已经接近 generate 时间，分卡可能更便宜。

## 和 HybridEngine 差在哪

| | veRL HybridEngine | slime `--colocate` |
| --- | --- | --- |
| 进程 | 同进程换并行组 | Megatron trainer + SGLang server 两套进程 |
| 权重 | 原地 reshard，少一份整模 | 两套权，靠 offload 互斥显存 |
| 切换 | 改 layout / 通信组 | 把对方整段 offload 再 load |
| 失败模式 | shard 与推理 TP 对不齐 | offload 没配对、`mem-fraction` 太大 |

最后我会补一句：HybridEngine 卖「少一份整模」；colocate 卖「少一套卡、进程边界仍在」。70B 同构卡紧、能接受 reshard 复杂度，偏 veRL；已经绑定 Megatron + SGLang、要 router / PD / 自定义 generate，偏 slime。分离部署时 `--actor-num-gpus-per-node` 和 `--rollout-num-gpus` 是加法，账本上要能说出「训练 64 卡 + 推理 32 卡」而不是含糊的「用了 96 卡」。`--rollout-num-gpus-per-engine` 填错成单机 tp，多机 router 会把请求打到错误的世界大小，表现为部分 engine 空转、部分 OOM。外部 engine（`--rollout-num-gpus 0`）把同步协议彻底外置，版本和 KV flush 仍要你自己保证，一体/分离开关管不到那套卡。把放置、offload、同步画成三列，比把 `--colocate` 当成布尔更快让面试官信你跑过。

## 选型时怎么讲资源账

先画卡：分离是加法，一体是时分复用。再画显存：分离两份权常驻；一体靠 `--offload-train` / `--offload-rollout` 互斥，切换走 PCIe。最后画时间：一体默认串行，分卡才叠得开 `train_async.py`。70B 同构、卡不够再买一份：colocate 或 HybridEngine。已经有 SGLang 推理池：分离 + `--rollout-num-gpus 0` 接外部 engine。中等规模、想少运维：`--colocate` 加双边 offload，把 `--sglang-mem-fraction-static` 降到 0.8。千万不要说「slime 的一体就是 HybridEngine」，进程数、是否原地 reshard、失败模式都不同。`--rollout-num-gpus-per-engine` 填的是 engine 世界卡数，多机 serving 填总卡。账本讲顺之后，flag 只是把这张图写进命令行。profile 时单独计 offload 拷贝，若拷贝已经接近 generate，一体比分卡更慢，这时省卡是假省。

一体卖的是少一套卡，税是 offload 拷贝和一步串行；分离卖的是生成池可独立扩，税是第二份权和 `update_weights`。`--colocate` 默认打开双边 offload，手动拆开关必须按阶段互斥，否则切换瞬间两套权叠爆。`--rollout-num-gpus-per-engine` 填世界卡数，`--rollout-num-gpus 0` 接外部 engine 已不是一体。和 HybridEngine 的差别用「进程数、是否原地 reshard」两句话就能拆穿冒充。profile 拷贝，气泡接近 generate 时一体比分卡更慢。

## 追问

- **一体能不能重叠 generate 和 train？** 默认不能。`--offload-train` / `--offload-rollout` 把对方赶出显存，物理上串行。要重叠先分卡，再谈挪 `ray.get` 或 `train_async.py`。把 `--colocate` 说成异步会被拆穿。
- **rollout 卡多于 actor 时多的卡干什么？** rollout-only，不参与 Megatron。适合 decode 比 backward 更吃卡的长 CoT。少报「多出来的卡也在训练」，账本会错。
- **为什么要降 `mem-fraction-static`？** 静态预留太大，offload 回来的训练状态没地方放，OOM 发生在切换瞬间而不是稳态。常降到 0.8，给两边各留一点。
- **外部 engine 还算 colocate 吗？** 不算。`--rollout-num-gpus 0` 只起 router，接外部 SGLang，是分池的极端。同步协议和 KV flush 要单独设计，一体开关管不到那套卡。
- **`--rollout-num-gpus-per-engine` 填错会怎样？** 它是一个 engine 的世界卡数，多机 serving 填总卡不是单机 tp。填错则 router 和 engine 世界大小对不上，部分空转、部分 OOM。
- **和 HybridEngine 一句话差在哪？** HybridEngine：同进程、换布局、少一份整模。slime colocate：两进程、offload 轮转、两份权互斥显存。说「slime 也有 HybridEngine」当场穿帮。
- **offload 没配对的典型 OOM 在哪？** 切换瞬间：训练阶段 SGLang 的 KV / CUDA graph 还在，或采样阶段 Megatron 优化器还在。稳态显存看起来够，峰值不够。双边 offload 必须互斥。
- **一体时 `--sglang-mem-fraction-static` 为什么常 0.8？** 给 offload 回来的训练状态留空。按 0.9 预留给 serving 独占没问题，一体切换会叠爆。这是放置参数，不是「SGLang 更省显存」。
- **怎么向面试官画这张图？** 先画卡是加法还是时分，再画显存是两份常驻还是 offload 互斥，最后画时间是否串行。HybridEngine 少一份整模；colocate 少一套卡、进程仍是两套。拷贝气泡接近 generate 就改分卡。`--rollout-num-gpus-per-engine` 填世界卡数，不要填成单机 tp。
