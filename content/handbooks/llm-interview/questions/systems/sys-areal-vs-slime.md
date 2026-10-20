---
id: sys-areal-vs-slime
section: systems
order: 275
level: S
title: AReaL 和 slime 对 rollout bottleneck 的理解差在哪？
quick: "AReaL 认为瓶颈是同步等待：生成等最长样本、训推互相空转，所以 fully async 解耦并用 staleness-aware PPO。slime 把瓶颈看成 SGLang、Megatron、Buffer 整条数据流的协同。"
tags:
  - AReaL
  - slime
  - Async RL
  - VeRL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: AReaL — A Large-Scale Asynchronous Reinforcement Learning System
    url: https://arxiv.org/abs/2505.24298
    type: primary
  - title: THUDM/slime
    url: https://github.com/THUDM/slime
    type: primary
  - title: HybridFlow / verl
    url: https://arxiv.org/abs/2409.19256
    type: primary
---

常见误区是：把 AReaL 和 slime 说成同一套 async 实现。veRL / slime 放置对照见 `sys-verl-vs-slime`，那张卡几乎不谈 AReaL。面试若问「同步 RL 慢在哪、异步怎么解」，AReaL 把系统病写得很干净；slime 则假设你已经接受 Megatron + SGLang 这条生产路径。

## AReaL：瓶颈是等待

同步 强化学习（RL） 交替做 generate 和 train。生成必须等 batch 内最长输出，推理卡空转；训练时推理卡再空，训练时生成卡也空。加卡并不能线性涨 逐 token 生成（decode） 吞吐，因为每卡 batch 变小，更容易掉进 memory-IO-bound。AReaL 的解法是解耦：

- 采样轨迹（rollout） worker 流式生成，不等全局 batch 结束；
- trainer 凑够 batch 就更新；
- `update_weights` 可打断进行中的生成，丢掉旧 KV 再续写，见 `sys-partial-kv-policy`；
- 训练 batch 会混多个 policy 版本，所以改 PPO：按 staleness 过滤 / 加权，而不是假装 on-policy。

论文报过相对同步系统数倍的实际耗时加速，且任务分数不掉。数字依赖长度方差和集群切分，面试不要背 $2.77\times$，要讲清等待长尾和训推互斥带来的两类开销。

## slime：瓶颈是整条栈的协同

slime 也做异步（`train_async.py`、队列水位、TIS / mask），但它公开叙事的中心不是「发明一种 staleness-aware 目标」，而是：

- SGLang 把长尾 generate 做满；
- Megatron 吃训练；
- Data Buffer 承接 abort、partial、自定义 generate；
- 权重用 `update_weights` / delta 推回引擎。

rollout 慢，可能是 KV、调度、组不齐、验证器（verifier） 排队、Megatron 等数据，而不只是「同步等待」。对应卡：`slime-data-buffer`、`slime-async-train`、`slime-dynamic-partial`。

## 怎么选型

| | 更像 AReaL | 更像 slime |
| --- | --- | --- |
| 痛点 | 同步等长尾、生成/训练互斥 | 已有 Megatron / SGLang，要 scale 数据流 |
| 代价 | 混版本样本、打断续写、算法要改 | ckpt 切分、并行表、SGLang-only |
| 别和谁混 | 一步 overlap 仍是同 batch 同版本 | HybridEngine 同进程 reshard |

veRL 默认仍是可同步的 HybridFlow，fully-async 是一条可选路径。TRL / Unsloth 不进入这场比较：它们几乎没有这套 rollout 控制面。

Staleness 怎么读：版本差 $v_{\mathrm{train}}-v_{\mathrm{rollout}}$ 只是 proxy；更有用的是 $\rho$ 分布、KL、ESS。没有固定「安全 stale=3」。队列太长就丢最旧的，而不是把 LR 开大把过期梯度平均掉，见 `sys-staleness`、`fund-wis-ess`。

## 追问

- **AReaL 的打断续写还是 on-policy 吗？** 整条轨迹不是单一 $\theta$ 采的。必须按段记版本，用 IS / clip / 过滤。这是算法税，换的是 GPU 不空。
- **slime 异步是不是同一件事？** 目标同类，实现绑在 Buffer 和 TIS/mask 上，而不是论文里那套 interruptible worker + staleness-enhanced PPO 商标。
- **能 veRL 训练 + AReaL 生成吗？** 可以集成，但版本管理、KV 清理和组对齐都需要自行实现。通常不如在一个栈里把 async 走完。
