---
id: sys-rollout-place
section: systems
order: 43
level: A
title: 系统：后训练的生成和训练，共置还是拆到两组卡？
quick: "生成时逐个输出 token，需要较大的 KV 缓存；训练是整段矩阵乘，要参数、梯度和 Adam。 卡多就拆开，卡紧就共置，每步把训练状态和 KV 池对调。参考模型只有一份冻结的 bf16，没有优化器。"
tags:
  - Post-train
  - Rollout
  - Memory
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: vLLM with TRL, server 与 colocate
    url: https://docs.vllm.ai/en/latest/training/trl/
    type: primary
  - title: verl issue 1524, 一批里更新几次
    url: https://github.com/verl-project/verl/issues/1524
    type: primary
---

## 题怎么来的

后训练 infra 的第一问通常是「生成和训练怎么放」。vLLM 文档写了两种：server 模式占单独的卡，colocate 模式和训练进程共享显存。没有一份公开的逐字面经，这道按这两种部署来答。

## 为什么不能当成同一种作业

生成每步读一遍权重和 KV，算得少，卡在带宽。训练对整段 token 做大 GEMM，卡在算力，还要放下梯度和 Adam。把生成硬跑在训练图里，KV 池小、没有连续批处理，同一批回答的长度差会大幅拖长每步耗时。所以 采样轨迹（rollout） 用推理引擎，见 `sys-rl-why-vllm-rollout`。

## 两种放法

卡够：一组卡只生成，一组卡只训练。权重按步送过去。生成不用等训练把显存腾出来，训练也不用拆掉 KV 池。代价是一部分卡在等另一部分。

卡紧：同一组卡轮流当主。生成前把训练状态卸到 CPU，把 KV 池建满；训练前反过来。搬的是每卡上的参数和优化器，PCIe 上是秒级，步时间是分钟级时可以接受。vLLM 的 sleep 可以只丢掉 KV、或连权重一起丢。先加载权重、写入新参数，再加载 KV，中间那段空着的显存留给训练侧把分片拼起来。

参考模型不要按第二个训练副本估。它是冻结的 bf16。KL 系数为 0 时可以不加载。奖励若是规则或单测，也不占 GPU。

## 代码

```python
def colocate_step(actor, rollout, batch):
    actor.to("cpu")
    rollout.wake(tags=["weights", "kv_cache"])
    trajectories = rollout.generate(batch)
    rollout.sleep()  # drop KV, then weights
    actor.to("cuda")
    actor.update(trajectories)
```

## 追问

**共置时一步里更新几次？** 权重同步发生在优化器真正 step 之后。一个 rollout batch 里若切成多个 mini-batch、更新多次，后面的 mini-batch 已经不是采样时的那份权重。要么一步只更新一次，要么接受 off-policy，并用重要性采样比修正。verl 的 issue 1524 写的就是这个账。

**拆卡之后生成挂了，训练要不要停？** 这一步没有完整的一组样本，就不要更新。用上一份权重继续等，或者丢掉这批。用残缺的组算 GRPO 均值，优势是错的。
