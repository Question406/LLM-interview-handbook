---
id: slime-external-engine
section: systems
order: 262
level: A
title: slime 怎么接已经拉起来的 SGLang？和 `--sglang-config` 为什么互斥？
quick: >-
  `--rollout-external-engine-addrs host:port ...` 只连、不拉起；`--rollout-num-gpus 0`
  时本地只起 router。`--sglang-config` 是 slime 自己管生命周期，两者互斥。跨集群 / 异构卡走 disk（大模型再
  delta）；能建 NCCL 再用默认 transport。slime 会打 `/server_info` 反推卡数和 PD 角色。
tags:
  - slime
  - SGLang
  - Weight Sync
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime External Rollout Engines
    url: https://thudm.github.io/slime/advanced/external-rollout-engines.html
    type: primary
  - title: slime SGLang Config
    url: https://thudm.github.io/slime/advanced/sglang-config.html
    type: primary
---

错法：把 `--rollout-external-engine-addrs` 和 `--sglang-config` 叠在一起，或把 external 说成 `--colocate`。三件事互斥：slime 自己起 engine、slime 用 YAML 管 PD / 多模型、serving 团队已经起好只让 slime 连。叠开关会让生命周期和卡账对不上。external 是分池的极端，不是一体。

## 三选一，别叠

| 你要的 | 用 |
| --- | --- |
| slime 起常规 engine | CLI `--rollout-num-gpus` |
| slime 起 PD / 多模型 / 异构组 | `--sglang-config` |
| serving 已起好、环境甚至 GPU 型号不同 | `--rollout-external-engine-addrs` |

`--rollout-num-gpus 0` 时本地只起 router，再 `/add_worker`。没给 router 地址时 slime 仍会起一个。面试别把「只起 router」说成「没推理进程」，推理在别人的集群里。slime 打 `/server_info` 反推卡数和 PD 角色，填错 addr 会表现为半边空转。

## 权重怎么同步

同集群能建 NCCL comm group：默认 `full` transport，一步推整份权。跨集群、异构卡、建不了 comm：`--update-weight-transport disk`。大 MoE 再 `--update-weight-mode delta`，只推变更。晚加入的 replica 必须先吃一份 full，不能只回放 delta，否则缺基线。版本和 KV flush 要你自己保证，一体/分离开关管不到那套卡，见 `slime-weight-sync`、`slime-colocate-vs-split`。

## 和 veRL、colocate 怎么划界

veRL 少见「推理集群完全外置」这条一等路径；slime 把它当成 GLM 规模的生产接口。colocate 是同卡两进程 + offload；external 是另一套卡、另一套运维。版本号、KV flush、PD 角色都要在 serving 侧对齐，slime 只保证能连上并推权。

## 追问

- **为什么和 `--sglang-config` 互斥？** 一个是 slime 管生命周期（起停、PD 角色、卡账），一个是只连已有进程。两边都写，router 和 worker 所有权冲突。
- **异构卡为什么走 disk？** NCCL 组建不起来，或拓扑跨集群。disk / 共享存储换的是正确性，吞吐会掉，大 MoE 用 delta 降流量。
- **新 replica 只收 delta 会怎样？** 缺 full 基线，部分专家或层是随机/旧权，采样分布 silently 偏。先 full 再 delta。
- **`--rollout-num-gpus 0` 还算 colocate 吗？** 不算。本地无 engine，是分池。同步和 KV flush 要单独设计。
