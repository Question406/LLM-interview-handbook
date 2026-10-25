---
id: xai-colossus
section: xai
order: 4
level: S
title: xAI：超大集群训练，故障、checkpoint、重同步面试怎么讲
quick: "超大集群先按故障域处理，再从完整 checkpoint 恢复，让所有 rank 对齐 step、RNG 和数据位置并重建通信。Series C 公开过 10 万 Hopper、122 天就绪、首批服务器后 19 天跑负载，以及 Spectrum-X 扩至 20 万卡的计划，内部切分和故障率未公开。"
tags:
  - xAI
  - Colossus
  - Distributed Training
  - Checkpoint
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: xAI Series C (6 billion USD)
    url: https://x.ai/blog/series-c
    type: primary
  - title: Grok 3 Beta — The Age of Reasoning Agents
    url: https://x.ai/blog/grok-3
    type: primary
  - title: MegaScale — Scaling Large Language Model Training to More Than 10,000 GPUs
    url: https://arxiv.org/abs/2402.15627
    type: primary
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

超大集群训练要把故障恢复当成正常路径：按故障域隔离问题，只加载完整提交的 checkpoint，再让所有 rank 回到同一步和同一数据位置。下面用公开的 Megatron / MegaScale 机制说明设计，不能把它当成 xAI 内部 runbook。

Series C 对 Colossus 的公开描述是 NVIDIA 全栈参考设计、10 万 Hopper、122 天就绪、第一批服务器到位后 19 天跑负载，并规划用 Spectrum-X 以太网扩到 20 万 Hopper。Grok-3 博文将训练算力归于这座集群，但未公布并行切分、checkpoint 间隔和故障率。后续若有新公开规模，应按对应时间引用；机柜布局、NCCL 超时、功耗和内部调度器都不能补写。

讨论万卡以上的重同步时，引用的机制来自 Megatron / MegaScale 等公开论文。

卡数到 $10^5$ 量级，要为 GPU Xid、网卡和主机故障、集合通信卡死、存储打满等问题准备恢复路径。可以按故障域处理：

| 域 | 典型现象 | 训练侧动作 |
| --- | --- | --- |
| 单卡 / 单机 | kernel 失败、ECC、进程退出 | 踢 rank，从最近一致 ckpt 拉起 |
| 集合通信 | all-reduce / all-to-all 挂起 | 毁 communicator，对齐 step 再重建 |
| 存储 | ckpt 写一半、读到短文件 | 版本目录加提交标记，不见标记当不存在 |
| 数据 | worker 落后、重复喂 | 按全局 token / sample 偏移重定位 |

以太网训练把延迟抖动放进故障模型：straggler 看起来像挂。先看是算得慢还是集合通信在等；不要一上来重跑整天。并行轴仍是张量 / 流水线 / 数据 / 专家并行。xAI 用哪一档，公开材料没写。我只说以太网比 NVLink 域更怕小消息延迟，流水线和 MoE 的同步点会放大 straggler。MoE 通信见 `xai-grok-moe`。

优化器状态按参数量是数倍于权重的。步与步之间的可见性必须是完整一份或完全不可见，半份权重比没存更糟。这和 `xai-kv-txn` 同一契约。

checkpoint 可以按下面的顺序发布：

1. 写到 `step=N/` 临时目录（模型、优化器、RNG、dataloader 偏移、并行拓扑）。
2. 校验 size / checksum，再写 `COMMIT` 标记或原子 rename 成当前最新。
3. 保留最近 $k$ 份。读只认有标记的。
4. 异步流水：拷贝重叠在前向，但提交点仍是一步边界。不要「拷到一半就算成功」。

保存间隔要在 I/O 开销和故障后的重做窗口之间取舍。平均无故障时间随规模变差时，保存太稀会降低有效 MFU；太密又会占满存储和 CPU 拷贝。这里没有可引用的 xAI 内部分钟数。若要少几台机器继续训练，还需调整数据并行度、优化器分片和数据切分，弹性恢复比原拓扑重启更复杂。

重同步：所有存活 rank 必须同意同一个 step、同一份 RNG、同一段数据偏移。错一步数据，loss 表面还在降，checkpoint 已经脏。集合通信句柄不能复用已经死掉的 rank。恢复后先做一次短的 dummy all-reduce 当探活，再进正式 step。

还要区分 Dojo 和 Colossus，不能把两者的规模或设计混用。

## 追问

**以太网能训 MoE 吗？**
公开只说 Spectrum-X 以太网做扩展。MoE 的 all-to-all 对延迟敏感。能不能训取决于拓扑和计算通信重叠，不取决于口号。
**为什么不每步都 ckpt？**
状态是 TB 级，每步写会变成存储任务。要在丢失窗口和 IO 之间取点。
**和推理故障的差别？**
训练要步对齐的全局一致性；推理可以丢一个 replica。别用「重启 pod」一套话搪塞两边。
**公开 10 万卡是不是你内部数字？**
不是。那是 Series C 博文的公开表述。更大口径以当时官网为准，面试不需要背未公开拓扑。
