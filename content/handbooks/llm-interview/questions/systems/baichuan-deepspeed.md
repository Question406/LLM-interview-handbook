---
id: baichuan-deepspeed
section: systems
order: 164
level: A
title: 百川智能：DeepSpeed 了解吗，怎么做？
quick: >-
  DeepSpeed 用 ZeRO 分片优化器、梯度和参数来放大可训规模，再叠加 offload 与激活检查点。怎么做看模型单卡放不放得下：我一般先
  ZeRO-2，不够再 3，不会一上来全 offload。
tags:
  - Baichuan
  - DeepSpeed
  - ZeRO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面 压力好大
    url: https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530
    type: candidate-first-hand
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary-paper
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“deepspeed了解么如何做的”**

百川实习一面这题，这块容易背 ZeRO-1/2/3 名词却说不清「你这次为什么选这个 stage」，或者把 DeepSpeed 和 vLLM 混成一个框架。我会讲：ZeRO 用分片换单卡显存，通信变多；怎么做取决于哪块先爆，优化器状态、激活还是参数本身。先 2 再 3，不要一上来 CPU offload。相关卡：`sys-zero`、`tencent-zero-123`。最后我会补一句：显存账 → 选 stage → 再决定要不要 offload，别把 DeepSpeed 说成另一种并行算法。

## ZeRO 三档分别切什么

数据并行每卡仍算自己的 batch，但状态分片：ZeRO-1 分优化器状态（Adam 的一阶二阶约占参数的 8 字节量级，往往最先爆）；ZeRO-2 再分梯度；ZeRO-3 连参数也分片，前向/反向按需 all-gather 再丢。通信体积随 stage 上升，换的是可训模型规模。CPU / NVMe offload 继续拿时间换显存，适合撑过峰值，不当默认吞吐方案。激活检查点是另一条轴，和 ZeRO 正交：长序列激活爆了要 checkpoint，不是盲目升到 3。我会先报哪一块显存不够，再选 stage。DeepSpeed 还包了通信重叠和一些 fused kernel，但这题关键在 ZeRO 分片，别跑去讲 pipeline 引擎。

## 「怎么做」要对上模型规模

配 `zero_stage`、bf16、梯度累积；stage 3 还要处理分片保存 / 加载，以及和生成引擎之间的权重同步。SFT + LoRA 常见 ZeRO-2 就够；全参 70B 才认真上 3。和 vLLM 不要混：DeepSpeed 主训练分片，vLLM 主推理 KV 与调度。显存账要分开报：参数、Adam 状态、梯度、激活；升 stage 只动前三项，激活仍靠 checkpoint 或更短序列。蚂蚁二面也问 DeepSpeed，答案同构；百川还常接「用了多少卡、训多久」，要能把 stage、卡数、batch 和是否 offload 对上账，而不是报一个「用了 DeepSpeed」。

## 追问

- **为何不默认 ZeRO-3？** 通信和 kernel 启动更重，小模型可能更慢；先看是否真的放不下参数。
- **和 Megatron TP 怎么选？** 单卡放不下的是宽矩阵 / 激活，常用 TP；放不下的是优化器副本，先 ZeRO。大规模两者叠。见 `sys-parallel`。
- **Offload 一定更省吗？** 显存省、迭代变慢；若 GPU 算力被 PCIe 饿死，MFU 会很难看。先用 stage 2 打满 GPU，再考虑 offload。
- **LoRA 还要不要 ZeRO？** 要看基座是否驻留。基座全参在 GPU 上仍可能要 2；只训很小 adapter 时 1/2 即可。保存 checkpoint 时确认能从分片恢复成推理引擎可读的整模。
