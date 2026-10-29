---
id: sys-areal-vs-slime
section: systems
order: 275
level: S
title: AReaL 和 slime 对 rollout bottleneck 的理解差在哪？
quick: >-
  AReaL 主要用 fully async 消除同步长尾与训推互等，再用 staleness-aware PPO 处理混版本数据。slime 更侧重
  Megatron、SGLang 和 Data Buffer 的整条数据流，连同 sampling、回收和权重同步一起优化。
tags:
  - AReaL
  - slime
  - Async RL
  - VeRL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: AReaL — A Large-Scale Asynchronous Reinforcement Learning System
    url: 'https://arxiv.org/abs/2505.24298'
    type: primary
  - title: THUDM/slime
    url: 'https://github.com/THUDM/slime'
    type: primary
  - title: HybridFlow / verl
    url: 'https://arxiv.org/abs/2409.19256'
    type: primary
---

AReaL 重点解决同步训练里的等待：生成等最长样本，训练和推理阶段彼此空转。slime 则把 Megatron、SGLang 和 Buffer 之间的数据流一起优化，瓶颈可能出在 sampling、验证器、组对齐或权重同步。两者都能异步，但侧重点和实现路径不同；veRL / slime 的进程放置可以另外对照 `sys-verl-vs-slime`。

## AReaL：瓶颈是等待

同步 RL 交替做 generate 和 train。生成必须等 batch 内最长输出，推理卡空转；训练时推理卡再空，训练时生成卡也空。加卡并不能线性涨 逐 token 生成（decode） throughput，因为每卡 batch 变小，更容易掉进 memory-IO-bound。AReaL 的解法是解耦：

- sampling 轨迹（rollout） worker 流式生成，不等全局 batch 结束；
- trainer 凑够 batch 就更新；
- `update_weights` 可打断进行中的生成，丢掉旧 KV 再续写，见 `sys-partial-kv-policy`；
- 训练 batch 会混多个 policy 版本，所以改 PPO：按 staleness 过滤 / 加权，而不是假装 on-policy。

论文报告过相对同步系统数倍的实际耗时加速，任务分数保持住了。$2.77\times$ 这样的结果依赖长度方差和集群切分，解释时要连同等待长尾、训推互斥这两类开销一起讲。

## slime：瓶颈是整条栈的协同

slime 通过 `train_async.py`、队列水位和 TIS / mask 支持异步，公开方案把以下几段数据流放在一起：

- SGLang 把长尾 generate 做满；
- Megatron 吃训练；
- Data Buffer 承接 abort、partial、自定义 generate；
- 权重用 `update_weights` / delta 推回引擎。

rollout 慢，可能是 KV、调度、组不齐、验证器（verifier） 排队、Megatron 等数据，而不只是「同步等待」。对应卡：`slime-data-buffer`、`slime-async-train`、`slime-dynamic-partial`。

| | 更像 AReaL | 更像 slime |
| --- | --- | --- |
| 痛点 | 同步等长尾、生成/训练互斥 | 已有 Megatron / SGLang，要 scale 数据流 |
| 代价 | 混版本样本、打断续写、算法要改 | ckpt 切分、并行表、SGLang-only |
| 别和谁混 | 一步 overlap 仍是同 batch 同版本 | HybridEngine 同进程 reshard |

veRL 默认仍是可同步的 HybridFlow，fully-async 是一条可选路径。TRL / Unsloth 不进入这场比较：它们几乎没有这套 rollout 控制面。

衡量 staleness 时，版本差 $v_{\mathrm{train}}-v_{\mathrm{rollout}}$ 只是 proxy，还要看 $\rho$ 分布、KL 和 ESS。没有固定「安全 stale=3」。队列太长就丢最旧的，而不是把 LR 开大把过期梯度平均掉，见 `sys-staleness`、`fund-wis-ess`。

## 追问

**AReaL 的打断续写还是 on-policy 吗？**
整条轨迹不是单一 $\theta$ 采的。必须按段记版本，用 IS / clip / 过滤。这是算法税，换的是 GPU 不空。
**slime 异步是不是同一件事？**
优化目标同类，slime 的实现围绕 Buffer 和 TIS/mask；AReaL 论文则采用 interruptible worker + staleness-enhanced PPO。
**能 veRL 训练 + AReaL 生成吗？**
可以集成，但版本管理、KV 清理和组对齐都需要自行实现。通常不如在一个栈里把 async 走完。
