---
id: stepfun-1t-vs-small
section: systems
order: 143
level: A
title: 阶跃星辰：训 1T 级模型和训小模型有何不同？
quick: >-
  规模变大后，通信、容错、数据 throughput 和数值稳定性都要重新设计：组合 3D 并行与 ZeRO，使用异步 checkpoint
  和弹性恢复，并持续检查数据供给与溢出。小模型的学习率等超参不能按卡数直接外推。
tags:
  - StepFun
  - Distributed Training
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阶跃星辰大模型算法实习一面
    url: 'https://www.nowcoder.com/feed/main/detail/5cb1ebe809fd402d844cce47380a926f'
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-03-27
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“训练 1t 模型遇到哪些困难，跟小尺寸模型有什么不同”**

训练到 1T 级时，要重新处理通信、容错、数据 throughput 和数值稳定性，小模型的配置不能直接线性放大。原帖没有定义「1t」是万亿参数还是万亿 token，回答时应先说明自己的理解：前者尤其依赖参数切分，后者尤其依赖长期的数据 throughput 和稳定性。这里可以讨论通用的规模化困难，不补写阶跃未公开的配方。

7B 单机可以逐步 print、单卡 Adam。1T 级必须 3D 并行（TP/PP/DP）再叠加 ZeRO / 专家并行。单步实际耗时里，bubble、all-gather、reduce-scatter 往往大于 GEMM。激活重计算用算力换显存，MFU 看起来低是设计，不是没调好。跨机几乎不能逐步调试，要用 rank 级日志和集体通信超时，见 `sys-collectives`、`sys-zero`。ckpt 本身也从「存一份 state_dict」变成异步、分片、可部分恢复，I/O 会变成新的步间气泡。

拿 7B 来对照，可以先算内存：复制优化器状态会先撑满显存，所以需要分片；全部保留激活也装不下，就要重计算或选择性保存。

故障从「偶发」变成「每个 job 都会遇到」。要异步 ckpt、弹性恢复、跳过坏节点，而不是整作业重来。数据管道要能持续喂饱和可复现混合；loader 卡住时 GPU 空转，看起来像算力不够。评测也更贵，要用探针任务和子集，不能每 N step 跑全套。

batch / lr 的稳定区变窄，小模型 lr 按卡数线性放大常发散。BF16 范围大但仍要盯溢出和 loss spike；MoE 还有路由不均和 token drop。数据侧的 token 配比一变，1T 级要跑很久才看得出，必须用小探针集盯漂移。沿着通信 → 容错 → 数据 → 数值检查，才能判断整个作业能否持续推进。

## 追问

**1T 是参数还是 token？**
原帖未定义。两者都对：万亿参数要切分和容错，万亿 token 要数据 throughput 和稳定性。先声明你按哪边答。
**为什么不能只用 TP？**
TP 切单层计算，优化器副本和 DP 显存是另一维，常和 ZeRO 组合，见 `sys-zero`。
**小模型 lr 直接 $\times N$ 会怎样？**
大 batch 下稳定区变窄，容易 loss spike。要用 warmup、按 token 而不是按卡硬套。
**怎么证明你想过「哪一层先爆」？**
先说优化器状态，再说激活，再说通信气泡和 ckpt I/O，不要先报卡数。
**评测为什么不能照抄 7B？**
全量评测的实际耗时和钱都按集群规模涨，只能用探针和子集盯回归，全量留给里程碑。
**MoE 1T 还多哪一层？**
专家并行和容量/drop。路由不均时有的专家饿死、有的溢出，小 dense 模型没有这条轴。
