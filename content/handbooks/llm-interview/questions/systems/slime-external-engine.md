---
id: slime-external-engine
section: systems
order: 262
level: A
title: slime 怎么接已经拉起来的 SGLang？和 `--sglang-config` 为什么互斥？
quick: "已有 SGLang 服务就用 `--rollout-external-engine-addrs host:port ...` 连接，slime 不负责拉起 engine；`--rollout-num-gpus 0` 时本地只起 router。`--sglang-config` 由 slime 管生命周期，所以两者互斥；权重同步按能否建立 NCCL 选择默认 transport 或 disk，大模型再考虑 delta。"
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

已经拉起 SGLang 时，用 `--rollout-external-engine-addrs` 让 slime 连接现有服务。`--sglang-config` 则让 slime 用 YAML 管理 PD / 多模型的生命周期，两条路径互斥，否则 router 和 worker 的归属会冲突。external 用的是另一套推理卡；`--colocate` 是同卡的两套进程，通过 offload 交替运行。

| 你要的 | 用 |
| --- | --- |
| slime 起常规 engine | CLI `--rollout-num-gpus` |
| slime 起 PD / 多模型 / 异构组 | `--sglang-config` |
| serving 已起好、环境甚至 GPU 型号不同 | `--rollout-external-engine-addrs` |

`--rollout-num-gpus 0` 时本地只起 router，再 `/add_worker`。没给 router 地址时 slime 仍会起一个，推理进程则运行在外部集群。slime 调用 `/server_info` 获取卡数和 PD 角色，填错 addr 会表现为半边空转。

同集群能建 NCCL comm group 时，用默认 `full` transport，每步传整份权重。跨集群、异构卡或无法建立 comm 时，改用 `--update-weight-transport disk`；大 MoE 可以再开 `--update-weight-mode delta`，只传变更。晚加入的 replica 必须先加载一份全量权重，不能只回放 delta，否则缺基线。版本和 KV flush 要你自己保证，一体/分离开关管不到那套卡，见 `slime-weight-sync`、`slime-colocate-vs-split`。

veRL 少见「推理集群完全外置」这条一等路径；slime 把它当成 GLM 规模的生产接口。colocate 是同卡两进程 + offload；external 是另一套卡、另一套运维。版本号、KV flush、PD 角色都要在 serving 侧对齐，slime 负责连接已有引擎并推送权重。

## 追问

**为什么和 `--sglang-config` 互斥？**
一个是 slime 管生命周期（起停、PD 角色、卡账），一个是只连已有进程。两边都写，router 和 worker 所有权冲突。
**异构卡为什么走 disk？**
NCCL 组建不起来，或拓扑跨集群。disk / 共享存储换的是正确性，吞吐会掉，大 MoE 用 delta 降流量。
**新 replica 只收 delta 会怎样？**
缺 full 基线，部分专家或层是随机/旧权，采样分布会产生不易察觉的偏差。先 full 再 delta。
**`--rollout-num-gpus 0` 还算 colocate 吗？**
不算。本地无 engine，是分池。同步和 KV flush 要单独设计。
