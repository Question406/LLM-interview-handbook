---
id: byte-verl-structure
section: systems
order: 230
level: S
title: 字节 Agent 算法一面：讲讲 veRL 的结构、关键组件，怎么魔改？
quick: >-
  按 HybridFlow：Ray Trainer 编排数据流；`actor_rollout_ref` 同一组 GPU
  上训练/采样/算参考 logp；Reward / Env 打分或跑工具；PPO 才加 Critic。魔改我先动 Reward 与
  Env，再动 loss 与异步 rollout，不会一上来改 Megatron kernel。
tags:
  - ByteDance
  - VeRL
  - HybridFlow
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节大模型agent算法一面分享
    url: https://www.nowcoder.com/feed/main/detail/f6e62eddaae1460fa80c0a0052f3267a
    type: candidate-first-hand
  - title: HybridFlow
    url: https://arxiv.org/abs/2409.19256
    type: primary
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
---

## 真题记录

- 公司：字节跳动
- 岗位：大模型 Agent 算法；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“讲讲verl的结构，关键组件，如何魔改,遇到的问题”**

字节 Agent 算法一面这题，这块容易按目录名报 `workers/`，或一上来讲 Megatron kernel。我会按数据流讲：Trainer 编排 → Actor/Rollout/Ref 在同一组 GPU 上换布局采样 → Reward/Env 打分 →（PPO 才有）Critic。魔改优先级是 Reward 与工具协议，再是 loss 与异步，最后才动内核。相关卡：`sys-verl-hybridengine`、`sys-verl-vs-slime`、`didi-verl-metrics`。

## 按数据流说组件

1. **Trainer（单控）**：读 parquet / prompt，切 `rollout_batch`，用 Ray 调度 worker。
2. **Actor + Rollout + Ref**：HybridEngine 把 FSDP/Megatron 分片权重原地换成 vLLM/SGLang 布局再采样；Ref 冻结算 KL 或参考 logp。
3. **Reward / Verifier / Tool Env**：规则、代码沙箱、搜索 API；Agent 多轮走 SGLang multi-turn。
4. **Critic**：只在 PPO/GAE；GRPO 没有。

蚂蚁账本卡管样本数怎么对齐；本题管「改哪里」。权重同步和 logp 重算是这条链路的税，不是可选日志。

## 魔改顺序与典型坑

先自定义 reward manager 和工具超时 / schema；再动 `loss_agg_mode`、KL 估计器；然后才异步 rollout 与 staleness。不要一上来改 Megatron kernel。踩坑通常是：vLLM 与训练图 logp 不一致必须重算；权重同步卡死；`rollout.n` 与 micro-batch 对不齐导致空卡或 OOM。Agent 场景优先把 Env 的超时、重试和 observation 截断做对，否则后面的 loss 改动都在放大脏轨迹。用过 slime 时对照一句：Trainer 仍是 Ray 单控；Actor/Rollout 拆成 Megatron + SGLang，粘合是 Data Buffer 和 `update_weights`，不是 HybridEngine 换布局；魔改先换 `--custom-rm-path` / `--rollout-function-path`。

## 追问

- **GRPO 为什么没有 Critic？** 组内相对优势替代 value；组件图里这条边直接不存在。
- **为何必须重算 logp？** 采样引擎与训练精度 / 并行切分不同，旧 logp 会让 ratio 失真。见 `meituan-verl-recompute-logprob`。
- **HybridEngine 换布局失败常见原因？** TP 与推理 TP 不一致、dtype 不齐、更新权重时仍有 in-flight 请求。
- **最小可行魔改是什么？** 一个可测的 rule reward + 固定 `rollout.n`，先把 group 优势和指标跑通，再加工具。
