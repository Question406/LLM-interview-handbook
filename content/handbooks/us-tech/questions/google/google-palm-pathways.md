---
id: google-palm-pathways
section: google
order: 4
level: S
title: Google：PaLM / Pathways 规模化训练，你怎么讲「一条模型服务多任务」
quick: >-
  Pathways 是跨 Pod 的数据流运行时；PaLM 是跑在它上面的 540B 稠密解码器。多任务首先是「一个 LM、很多
  few-shot 任务」，不是一专家一任务。别把 PaLM 讲成 MoE，也别把 Pathways 讲成又一个 Megatron 启动脚本。
tags:
  - Google
  - PaLM
  - Pathways
  - Scaling
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: PaLM — Scaling Language Modeling with Pathways
    url: https://arxiv.org/abs/2204.02311
    type: primary
  - title: Pathways — Asynchronous Distributed Dataflow for ML
    url: https://arxiv.org/abs/2203.12533
    type: primary
  - title: Introducing Pathways — A next-generation AI architecture
    url: https://blog.google/technology/ai/introducing-pathways-next-generation-ai-architecture/
    type: secondary
---

Google 研究 / TPU 系统岗爱把「Pathways 愿景」和「PaLM 这篇训练报告」揉成一问。先拆开：一个是运行时，一个是在这个运行时上训出来的稠密 LM。Gemini 的稀疏专家是另一条线，见 `google-gemini-moe`。

## 先报配置，再讲系统

PaLM 540B：decoder-only Transformer，在 6144 块 TPU v4 上训，跨两个 Cloud TPU v4 Pod。当时多数大模型停在单 Pod；跨 Pod 的梯度交换要走数据中心网络，这是 Pathways 要证明的点。

训练切分：Pod 内部仍是常规数据并行 + 模型并行；Pod 之间是两路数据并行：一个 Python 客户端把 batch 劈成两半，各 Pod 算正反向，再交换梯度，两边都更新到 bitwise 相同的参数。面试要能说出「跨 Pod 是 DP，不是又加一层流水线」。芯片上 batch / 模型维怎么切，见 `google-tpu-mesh`。

Pathways 论文的卖点不是新优化器。它是异步分布式数据流：单客户端把切好的程序派到远程 Pod，gang-schedule 遮住下发延迟，分片数据流把传输摊掉。对面试官这意味着：大规模不是「Python for 循环多机」，而是编译出来的一张 SPMD 图在几千芯上跑。编译时切分见 `google-jax-pjit`。

## 「一条模型服务多任务」讲三层，不混

Jeff Dean 公开 Pathways 愿景：一个模型覆盖很多任务和模态，稀疏激活，而不是每个任务一座集群。PaLM 这篇没有实现「输入一张图就路由到视觉专家」那种产品形态。它证明的是更窄、但可量化的一步：

1. 能力层。 一个稠密 LM，用 next-token 训完，靠 prompt / few-shot 覆盖上百个理解、推理、代码任务。BIG-bench 上部分任务随规模出现不连续跳变。这是「一条权重，很多任务」，任务切换发生在上下文里，不发生在重新加载 checkpoint。
2. 系统层。 同一套 Pathways runtime 可以在不同加速器子集上跑不同计算图。愿景是训练和推理、多任务数据流共享一台超级计算机，而不是任务 A 独占 Pod 1、任务 B 独占 Pod 2。PaLM 用到的是其中「跨 Pod 训一个大模型」这一刀。
3. 产品层（现在怎么答）。 Gemini 一类：一个 serving 栈、多个表面（搜索、办公、代码），靠提示、工具、权限，而不是 50 份微调副本。副本会把改进摊薄、把 KV 和量化配置分裂。多任务是共享主干 + 窄适配，不是「每个产品一个 540B」。

千万别说「PaLM 用 MoE 所以能多任务」。论文写明是 densely activated。Google 的 MoE 训练线是 GShard / Switch / GLaM。Pathways 原文把数据相关路由当成系统想支持的未来能力，不是 PaLM 540B 已经在用的结构。

Serving 侧同一句话：一份 540B 权重、很多产品表面，用 prompt / 工具切任务，而不是每个下游一份微调副本。副本会把量化、KV 布局、安全策略复制成 N 套。Pathways 愿景里的「一台超级计算机跑很多图」，落地就是共享主干、窄适配、统一 serving。真正的稀疏条件计算要到 Gemini MoE 才公开成主叙事。

Few-shot 能覆盖多任务，是因为预训练已经把「按指令接龙」学进同一套 next-token。它不是系统层的多租户调度。面试若把 few-shot 和 Pathways runtime 说成一件事，评委会认为你没拆开论文。能力是 PaLM 的；调度是 Pathways 的；稀疏专家是后来 Gemini 的。

## 白板主动报的坑

跨 Pod 梯度要在优化器 step 前对齐，否则两半模型分叉，以后再也合不回来。吞吐的瓶颈可能是 DCN 上那一次梯度交换，不是 HBM。若 MFU 掉了，先问是 Pod 内集合通信还是跨 Pod 传输，别一上来改 microbatch。

多任务微调如果真上了：要防任务抢梯度。PaLM 主叙事是 few-shot 不做逐任务微调。若面试官改成「同一 backbone 训翻译 + 问答」，再讲数据配比、温度、和会不会把代码能力冲掉。那是数据配比题，不是 Pathways 题。

数字锚要一次报全：540B 稠密、6144 块 TPU v4、两个 Pod。漏掉「稠密」就把 PaLM 讲成 MoE 了。

## 追问

- **Pathways 等于 JAX 吗？** 不是。PaLM 的计算仍走 JAX/XLA；Pathways 管跨 Pod 调度和分片数据流。没有它，单客户端很难把 6144 芯当一台机器用。先拆词：Pathways 是运行时愿景，PaLM 是跑在上面的稠密 LM。
- **和 GPU 上 3D 并行比？** 目标相同：把状态塞进芯片并掩盖通信。实现不同：TPU Pod 拓扑更规整，PaLM 跨 Pod 只加了两路 DP。类比见 `google-tpu-mesh`。
- **一条模型会不会任务互相干扰？** 会。few-shot 把干扰推迟到上下文竞争；真多任务梯度则要看数据权重。答「共享一定更好」是空话。
- **和 Gemini 什么关系？** PaLM 证明规模 + 跨 Pod 系统。后来的 Gemini 接模态和长上下文，1.5 起公开走稀疏 MoE。数字锚：540B 稠密、6144 块 TPU v4、两个 Pod。漏掉「稠密」或把 6144 说成专家数，就是把 PaLM 和 MoE 拼错了。
- **跨 Pod 那一次梯度交换失败怎么办？** 不能各写各的。要么整步重算，要么用 bitwise 对齐的归约。失败模式是参数分叉，不是流水线气泡；分叉副本没有「平均一下」这种合法修复。
