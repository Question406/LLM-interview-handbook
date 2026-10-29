---
id: byte-verl-structure
section: systems
order: 230
level: S
title: 字节 Agent 算法一面：讲讲 veRL 的结构、关键组件，怎么魔改？
quick: >-
  按数据流讲：Ray Trainer 负责编排，Actor/Rollout/Ref 在同一组 GPU 上切换布局来训练和
  sampling，Reward/Env 打分，只有 PPO 才有 Critic。魔改先动 Reward 和 Env，再动 loss，最后才碰内核。
tags:
  - ByteDance
  - VeRL
  - HybridFlow
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 字节大模型agent算法一面分享
    url: 'https://www.nowcoder.com/feed/main/detail/f6e62eddaae1460fa80c0a0052f3267a'
    type: candidate-first-hand
  - title: HybridFlow
    url: 'https://arxiv.org/abs/2409.19256'
    type: primary
  - title: verl
    url: 'https://github.com/verl-project/verl'
    type: primary
---

## 真题记录

- 公司：字节跳动
- 岗位：大模型 Agent 算法；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“讲讲 verl 的结构，关键组件，如何魔改,遇到的问题”**

我会按数据流讲 veRL：Trainer 编排 → Actor/Rollout/Ref 在同一组 GPU 上换布局 sampling → Reward/Env 打分 →（只有 PPO 才有）Critic。魔改的优先级是先 Reward 和工具协议，再 损失（loss）和异步，最后才动内核。照着目录名报 `workers/`，或者一上来讲 Megatron kernel，面试官听不出你用过。

沿着一条样本走一遍就清楚了。Trainer 是单控的，读 parquet 里的 prompt，切成 `rollout_batch`，用 Ray 调度各个 worker。接着是 Actor、Rollout 和 Ref：HybridEngine 把 FSDP 或 Megatron 分片的权重原地换成 vLLM / SGLang 的布局去 sampling，Ref 是冻结的，负责算 KL 或参考 logp。采出来的轨迹交给 Reward、Verifier 或 Tool Env 打分，可以是规则、代码沙箱或搜索 API，Agent 多轮场景走 SGLang multi-turn。Critic 只在 PPO/GAE 里出现，GRPO 没有。权重同步和 logp 重算是这条链路上必须交的税，不是可选的日志。蚂蚁那张账本卡管样本数怎么对齐，这题管改哪里。

魔改的顺序是：先写自定义的 reward manager，处理工具超时、定义 schema；再动 `loss_agg_mode` 和 KL 估计器；然后才是异步 sampling 轨迹（rollout）和 staleness。不要一上来就改 Megatron kernel。Agent 场景里，最优先把 Env 的超时、重试和 observation 截断做对，不然后面所有 loss 的改动都是在放大脏轨迹。

遇到的问题通常是这几类：vLLM 和训练图算出的 logp 不一致，必须重算；权重同步卡死；`rollout.n` 和 micro-batch 对不齐，导致空卡或 OOM。

用过 slime 的话，可以对照一句：Trainer 同样是 Ray 单控，但 Actor 和 Rollout 拆成了 Megatron 加 SGLang，中间靠 Data Buffer 和 `update_weights` 粘起来，没有 HybridEngine 那种换布局；魔改先换 `--custom-rm-path` / `--rollout-function-path`。

## 追问

**GRPO 为什么没有 Critic？**
组内相对优势替代了 value，组件图里这条边直接就没有。

**为什么一定要重算 logp？**
sampling 引擎和训练的精度、并行切分都不一样，直接用旧 logp，ratio 会失真。见 `meituan-verl-recompute-logprob`。

**HybridEngine 换布局失败，常见原因是什么？**
训练 TP 和推理 TP 不一致、dtype 不齐、更新权重时还有 in-flight 请求。

**最小可行的魔改是什么？**
一个可测的 rule reward 加固定的 `rollout.n`，先把 group 优势和指标跑通，再加工具。

相关：`sys-verl-hybridengine`、`sys-verl-vs-slime`、`didi-verl-metrics`
