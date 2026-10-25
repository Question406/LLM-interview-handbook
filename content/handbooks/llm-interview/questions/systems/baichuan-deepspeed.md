---
id: baichuan-deepspeed
section: systems
order: 164
level: A
title: 百川智能：DeepSpeed 了解吗，怎么做？
quick: "DeepSpeed 主要靠 ZeRO 分片优化器状态、梯度和参数来放大能训的模型规模，再叠加 offload 和激活检查点。怎么配取决于哪块显存先不够：我一般先上 ZeRO-2，不够再上 3，不会一开始就全 offload。"
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

DeepSpeed 的核心是 ZeRO：用分片换单卡显存，代价是通信变多。具体选哪个 stage，取决于先超出显存的是优化器状态、激活还是参数本身。我的顺序是先 ZeRO-2，不够再 3，CPU offload 放到最后。答这题我会按「显存账 → 选 stage → 再决定要不要 offload」来讲，背得出 ZeRO-1/2/3 却说不清这次为什么选这个 stage，面试官会觉得没用过。

ZeRO 三档切的东西不一样。它还是数据并行，每卡算自己的 batch，只是把状态分片存。ZeRO-1 分优化器状态，Adam 的一阶二阶约占参数的 8 字节量级，往往最先爆；ZeRO-2 再把梯度分片；ZeRO-3 连参数也分片，前向和反向时按需 all-gather，用完就丢。stage 越高通信量越大，换来的是能训更大的模型。CPU / NVMe offload 是继续拿时间换显存，适合撑过峰值，不适合当默认的吞吐方案。

激活检查点是和 ZeRO 正交的另一条轴。长序列下激活爆了，应该开 checkpoint，盲目升到 3 解决不了。显存账要分开报：参数、Adam 状态、梯度、激活。升 stage 只动前三项，激活还得靠 checkpoint 或者缩短序列。DeepSpeed 还包了通信重叠和一些 fused kernel，但这题重点是 ZeRO 分片，别跑去讲 pipeline 引擎。

「怎么做」要对上模型规模。配置上主要是 `zero_stage`、bf16、梯度累积；stage 3 还要处理分片的保存和加载，以及和生成引擎之间的权重同步。监督微调（SFT）加 LoRA 一般 ZeRO-2 就够，全参 70B 才认真上 3。别把它和 vLLM 混成一个框架：DeepSpeed 主要做训练分片，vLLM 主要做推理的 KV 和调度。蚂蚁二面也问过 DeepSpeed，答法一样；百川还常接着问「用了多少卡、训了多久」，你得能把 stage、卡数、batch 和有没有 offload 对上账，光说一句「用了 DeepSpeed」不够。

## 追问

**为什么不默认上 ZeRO-3？**
通信和 kernel 启动开销更重，小模型可能更慢。先确认参数是不是真的放不下。

**和 Megatron TP 怎么选？**
单卡放不下的是宽矩阵或激活，常用 TP；放不下的是优化器副本，先上 ZeRO。大规模训练两者叠着用，见 `sys-parallel`。

**Offload 一定更省吗？**
显存省了，迭代变慢；GPU 要是一直在等 PCIe 传输，MFU 会很难看。先用 stage 2 把 GPU 打满，再考虑 offload。

**LoRA 还要不要 ZeRO？**
看基座是否驻留在 GPU 上。基座全参在 GPU 上，可能还要 2；只训很小的 adapter，1 或 2 就够。存 checkpoint 时确认能从分片恢复成推理引擎能读的完整模型。

相关：`sys-zero`、`tencent-zero-123`
