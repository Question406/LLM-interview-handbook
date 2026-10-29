---
id: sys-rl-dataplane-controlplane
section: systems
order: 267
level: S
title: RL 训练为何要把数据平面与控制平面分开？responsibilities 如何划分？
quick: >-
  数据面负责 rollout generate、logprob、env /
  verifier、轨迹张量和梯度等高频操作，控制面负责作业规格、实验配置、权重版本发布和同步协议。两者通过带版本的接口交接，便于独立扩缩和故障恢复；控制面重启时，已在执行的
  batch 应能完成当前 step 或恢复。
tags:
  - RL Infra
  - Architecture
  - Control Plane
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: HybridFlow / veRL
    url: 'https://arxiv.org/abs/2409.19256'
    type: primary
---

我会把高频的张量和环境交互放在数据面，把作业配置、版本发布和成员管理放在控制面。这样控制面重启时，已经准入的 batch 还能完成当前 step 或恢复；某个 worker OOM 也不会破坏实验配置。On-policy RL 比读取磁盘 dataset 的 SFT 多了生成、环境交互和版本管理，把这些调度逻辑分散在每个 worker 里，很容易出现配置漂移，见 `sys-rl-infra`。

HybridEngine 的「训练布局 $\leftrightarrow$ 推理布局」属于同一批 GPU 上的放置与 reshard，具体见 `sys-verl-hybridengine`。这里划分的是每秒百万 token 的热路径和秒级、可人工审查的配置路径。

## 按接口划分职责

**数据面**扛一步里的张量与环境：

- Rollout generate / 逐 token 生成（decode）、PagedAttention KV
- 训练图重算 $\log\pi_\theta$、ref logprob
- Env / sandbox / 验证器（verifier） 的观测与标量 $r$
- Trajectory buffer、advantage、backward 与 DP all-reduce

**控制面**扛作业生命周期，不进 token 循环：

- Job spec、Hydra / 实验配置、特征开关
- 权重 **版本发布**：何时 sync、哪一版 $\theta$ 对哪一版 sampling 轨迹（rollout） 合法
- Worker 成员、配额、镜像、审计
- Checkpoint 调度（触发，而不是写 shard 本身）

HybridFlow 的 multi-controller 就是这个意思：generation、奖励分数（reward）、update 可换引擎，但「谁占哪张卡、跑哪一版配置」由控制面编排。角色本身按时间轴拆，见 `sys-rl-grpo-loop-roles`；本题问的是这些角色 **通过什么接口对话**，而不是 Actor 和 Ref 谁更新。

接口要版本化：`TrajectoryBatch` 带 `policy_version`、prompt id、token 张量、reward、mask；任务租约要幂等，避免控制面重试把同一条轨迹训两遍。数据面热点不得每个 token 去问 etcd；控制面挂了，已准入的 batch 应能把当前 step 做完或可恢复，而不是整群 SIGKILL。反过来，数据面 OOM 不该把实验配置写坏。

## 扩缩容和故障时怎样保持一致

Rollout 池和 trainer 池的瓶颈不同：前者吃 decode 与 sandbox 延迟，后者吃优化器显存。分平面之后生成节点可以按 KV 扩、训练节点按 ZeRO 扩，权重同步仍走控制面协议（NCCL / 共享存储 / 分片广播），见 `sys-rl-infra`、`sys-verl-hybridengine`。同卡 HybridEngine 只是把两份布局叠在同一批 GPU 上，**版本号和 job spec 仍然是控制面**；不要因为 colocate 就把配置写死在 worker 常量里。

故障隔离：verifier 超时是数据面局部失败，应按 `sys-rl-rollout-admission` drop / retry，而不是让作业控制器把整个 trial 标成 failed。控制面升级（改 clip $\varepsilon$、改 $n$）必须打版本，旧轨迹要么丢要么按旧契约消费，否则 advantage 和 损失（loss） 对不上。Freshness 也是控制面的契约：允许的最大 `policy_version` gap 写在 spec 里，数据面只执行过滤。

验收时，我会重启控制面，检查数据面 inflight batch 能否恢复；修改实验配置，检查是否等到版本栅栏再统一生效；最后按版本号验证 weight sync，避免 NCCL 没报错却仍有 worker 使用旧权重。画架构图时，把编排接口和张量传输分开，就能清楚表达这些 responsibilities。

## 追问

**HybridEngine 算哪一面？**
数据面放置：同卡 reshard、少一份整模。控制面仍是 job spec 和版本发布。换布局不是换实验。
**Weight sync 为什么算控制面？**
同步的 **时机、版本、失败重试** 是协议；拷贝 bytes 的 kernel 在数据面。没有版本号的 memcpy 会让 stale 轨迹混进 on-policy batch。
**控制面能不能直接改 learning rate？**
可以，但要打新 version，让本步剩余轨迹要么用旧超参做完，要么丢弃。中途改一半 rank 等于训练了两个作业。
**Trajectory store 算哪边？**
存张量是数据面；retention、权限、按实验查询是控制面。两边通过带版本的 字段和类型规范（schema） 交接。
**分了会不会多一跳延迟？**
会。热路径只在 step boundaries 问控制面一次（拉版本、拉租约），token 循环禁止 RPC。延迟换的是故障域清晰。
---
