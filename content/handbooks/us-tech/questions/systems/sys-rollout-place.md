---
id: sys-rollout-place
section: systems
order: 43
level: A
title: 系统：后训练的生成和训练，共置还是拆到两组卡？
quick: "卡充足时可以把 rollout 和训练拆到两组卡，按步同步权重；卡紧时让两者共置，生成前卸载训练状态，训练前释放 KV 池。生成主要受带宽和 KV 限制，训练还要容纳梯度与 Adam，因此要按阶段安排显存。"
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

卡充足时，我会把生成和训练拆到两组卡；卡紧时让它们共置，按阶段交换训练状态和 KV 池。vLLM 的 server 与 colocate 对应这两种方式，这道题按公开部署文档拟成，没有逐字现场面经。

两种作业吃的资源不同。生成每步读取权重和 KV，计算量较小，主要受带宽限制；训练对整段 token 做大 GEMM，主要受算力限制，还要存梯度和 Adam。如果直接在训练图里生成，KV 池小、缺少连续批处理，同一批回答的长度差也会拖长整步时间，所以 rollout 通常交给推理引擎，见 `sys-rl-why-vllm-rollout`。

拆卡时，一组只生成，一组只训练，每步传送权重。它们不用互相腾显存，也不用反复拆建 KV 池，但一组可能在等另一组，卡不一定始终忙着。

共置时，生成前把训练状态卸到 CPU，给 KV 池留空间；训练前释放 KV，再把训练状态搬回来。每卡参数和优化器经 PCIe 搬运可能花秒级时间，如果一步本来是分钟级，可以接受。vLLM sleep 可只释放 KV，也可连权重一起释放。恢复时先加载权重、写入新参数，最后恢复 KV，中间的空闲显存留给训练侧拼接分片。

参考模型只是一份冻结的 bf16 权重，没有优化器，不能按第二个训练副本估。KL 系数为 0 时可以不加载；规则或单测奖励也不占 GPU。

下面示意共置切换：

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

**一批 rollout 里可以更新多次吗？**
可以，但要接受后续 mini-batch 已经偏离采样策略，并用重要性采样比修正。权重同步发生在优化器真正 step 之后；也可以一批只更新一次，保持更接近 on-policy。verl issue 1524 讨论的就是这个区别。

**拆卡后生成挂了，训练继续吗？**
没有完整的一组样本就不更新。保留上一份权重等待，或丢掉整批；残缺组会把 GRPO 的均值与优势算错。
