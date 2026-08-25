---
id: xai-colossus
section: xai
order: 4
level: S
title: xAI：超大集群训练，故障、checkpoint、重同步面试怎么讲
quick: >-
  只引用公开数字：Colossus 以约 10 万 Hopper 起步、122 天就绪、首批服务器后 19 天跑任务，并公开规划用
  Spectrum-X 以太网扩到约 20 万卡。面试讲故障域、一致 checkpoint、失败后如何对齐 step，不要编内部拓扑和
  MTBF。
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

## 题怎么来的

xAI 训练系统 / 基础设施岗会问：十万卡量级怎么跑起来、挂了怎么办。公开材料够用的只有量级和网络族：Series C 写 Colossus 用 NVIDIA 全栈参考设计、**10 万 Hopper**、**122 天**就绪、第一批服务器到位后 **19 天**开始跑负载，并规划用 **Spectrum-X 以太网**扩到 **20 万 Hopper**。Grok-3 博文把训练算力挂在这座超集群上，没有公布并行切分、checkpoint 间隔或故障率。后面官网若再报更大公开规模，当「公开口径在变」即可。**不要编机柜布局、NCCL 超时、功耗、内部调度器。**

万卡以上的故障和重同步，用 Megatron / MegaScale 这类公开论文当机制，并标明「这是业界做法，不是 xAI runbook」。

## 故障是常态，不是 case

卡数到 $10^5$ 量级，单步里总有人掉队：GPU Xid、网卡、主机、集合通信卡死、存储打满。面试我按故障域切：

| 域 | 典型现象 | 训练侧动作 |
| --- | --- | --- |
| 单卡 / 单机 | kernel 失败、ECC、进程退出 | 踢 rank，从最近一致 ckpt 拉起 |
| 集合通信 | all-reduce / all-to-all 挂起 | 毁 communicator，对齐 step 再重建 |
| 存储 | ckpt 写一半、读到短文件 | 版本目录加提交标记，不见标记当不存在 |
| 数据 | worker 落后、重复喂 | 按全局 token / sample 偏移重定位 |

以太网训练把延迟抖动放进故障模型：straggler 看起来像挂。先看是算得慢还是集合通信在等；不要一上来重跑整天。并行轴仍是张量 / 流水线 / 数据 / 专家并行。xAI 用哪一档，公开材料没写。我只说以太网比 NVLink 域更怕小消息延迟，流水线和 MoE 的同步点会放大 straggler。MoE 通信见 `xai-grok-moe`。

## Checkpoint：原子可见，和 KV 事务同一句话

优化器状态按参数量是数倍于权重的。步与步之间的可见性必须是：**完整一份或完全不可见**，半份权重比没存更糟。这和 `xai-kv-txn` 同一契约。

面试够用的设计：

1. 写到 `step=N/` 临时目录（模型、优化器、RNG、dataloader 偏移、并行拓扑）。
2. 校验 size / checksum，再写 `COMMIT` 标记或原子 rename 成当前最新。
3. 保留最近 $k$ 份。读只认有标记的。
4. 异步流水：拷贝重叠在前向，但提交点仍是一步边界。不要「拷到一半就算成功」。

间隔是浪费算力 vs 重做窗口的权衡。我不会编 xAI 的分钟数。量级说法：若平均无故障时间随卡数变差，checkpoint 太稀会把有效 MFU 打穿；太密则把存储和 CPU 拷贝打满。弹性训练（少几台继续）要能改数据并行度，优化器分片和数据切分都要能 resize，这比重启难，当作 follow-up，不要假装做过他们的弹性栈。

重同步：所有存活 rank 必须同意 **同一个 step、同一份 RNG、同一段数据偏移**。错一步数据，loss 表面还在降，checkpoint 已经脏。集合通信句柄不能复用已经死掉的 rank。恢复后先做一次短的 dummy all-reduce 当探活，再进正式 step。

错法：把 Colossus 答成「卡多所以快」；报无法核对的内部数字；把 Dojo 和 Colossus 混成一个集群。

## 追问

- **以太网能训 MoE 吗？** 公开只说 Spectrum-X 以太网做扩展。MoE 的 all-to-all 对延迟敏感。能不能训取决于拓扑和计算通信重叠，不取决于口号。
- **为什么不每步都 ckpt？** 状态是 TB 级，每步写会变成存储任务。要在丢失窗口和 IO 之间取点。
- **和推理故障的差别？** 训练要步对齐的全局一致性；推理可以丢一个 replica。别用「重启 pod」一套话搪塞两边。
- **公开 10 万卡是不是你内部数字？** 不是。那是 Series C 博文的公开表述。更大口径以当时官网为准，面试不需要背未公开拓扑。
