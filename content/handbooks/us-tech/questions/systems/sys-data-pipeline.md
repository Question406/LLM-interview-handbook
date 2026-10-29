---
id: sys-data-pipeline
section: systems
order: 16
level: A
title: 系统：万亿 token 数据管道，shuffle、checkpoint、坏样本
quick: >-
  先在文档层 shuffle，再 pack 成定长序列，并把文档游标、shuffle / blend RNG 与模型一起保存。坏样本需同步 skip
  标志，让所有 rank 一起跳过 step，恢复后还要验证下一条 pack 与逻辑 sample id 对齐。
tags:
  - NVIDIA
  - Megatron
  - Data
  - Training
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      Efficient Large-Scale Language Model Training on GPU Clusters Using
      Megatron-LM
    url: 'https://arxiv.org/abs/2104.04473'
    type: primary
  - title: Scaling Language Model Training to a Trillion Parameters Using Megatron
    url: >-
      https://developer.nvidia.com/blog/scaling-language-model-training-to-a-trillion-parameters-using-megatron/
    type: secondary
  - title: MosaicML Streaming
    url: 'https://docs.mosaicml.com/projects/streaming/en/stable/'
    type: secondary
  - title: NVIDIA Megatron-LM
    url: 'https://github.com/NVIDIA/Megatron-LM'
    type: primary
---

## 可以这样回答

数据管道先洗文档顺序，再打包成训练序列；恢复训练时，数据位置必须与模型 checkpoint 对齐。比如模型恢复了，shuffle RNG 却丢了，loss 可能仍能接上，但重复样本和语料混合比例已经变化。

NVIDIA Megatron 的万亿 token 训练，以及 Meta / Microsoft 数据岗常涉及 shuffle、恢复与坏样本同步，OpenAI 式追问还会核对是否重复消费 token。脏 pack 引起的数值尖刺见 `sys-loss-spike`。

## 技术备查

数据管道先洗文档顺序，再打包成训练序列；恢复训练时，数据位置必须与模型 checkpoint 对齐。比如模型恢复了，shuffle RNG 却丢了，loss 可能仍能接上，但重复样本和语料混合比例已经变化。

NVIDIA Megatron 的万亿 token 训练，以及 Meta / Microsoft 数据岗常涉及 shuffle、恢复与坏样本同步，OpenAI 式追问还会核对是否重复消费 token。脏 pack 引起的数值尖刺见 `sys-loss-spike`。

throughput 掉在 CPU 解压而不是 GEMM 时，加 TP 没有用。先看 loader 空窗，再谈模型并行。

万亿 token 若先逐个展开再随机洗牌，索引和随机 IO 的成本都很高，甚至可能超过数据本身。Megatron 常见路径是 indexed dataset（`.bin` / `.idx` mmap）：文档或样本一条条顺序可读，shuffle 的是 **文档 id 列表**，不是每个 token。每个 epoch 用固定种子洗一遍 id，再按 DP rank 切 shard。混合语料按权重抽样（blend），权重进 checkpoint，否则 resume 后配比漂。

Packing 把变长文档拼到训练长度 $T$，document boundaries 要留特殊 token。丢失 document separators 等于把两篇无关文章粘成一句，损失（loss） 局部爆炸，看起来像训练不稳。Padding 浪费 FLOPs；packing 提高有效 token 比例，但让「一个 batch 里有哪些文档」更难复放，所以 sample id 日志要记 pack 里的文档列表，不只记 batch 号。

在线流式（WebDataset / Mosaic Streaming）适合数据还在写、不想预建 index。权衡是跨 epoch 精确去重和精确 resume 更烦：要记 shard 名、字节偏移、本 epoch 已消费计数。预建 index 适合稳态预训练；流式适合持续进数据的后训练。CPU tokenize / 解压跟不上时，GPU 在等 H2D，MFU 掉在数据面，Nsight 上是 loader 空窗而不是 NCCL。

只存模型、不存 dataloader，resume 有两种坏法：从头再洗，前面已看过的 token 再看一遍（局部 overfitting、曲线假掉）；或按 wall-clock 瞎跳，中间一段永远没人看。正确状态包括：当前 epoch、已消费 sample / token 计数、shuffle RNG、blend 抽样器状态、每个 DP rank 的 shard 游标。PP / TP 组内游标应相同，只在 DP 维不同。

异步 ckpt 时这份状态要和权重同一快照编号，见 `sys-async-ckpt`。弹性加卡之后 DP 变了，游标要按逻辑 sample id 重切，不能按旧 rank 号接着读，见 `sys-straggler`。验收时核对 resume 后下一条 pack 的 sample id 是否与原本下一条相同，再看 loss 是否连续。

损坏 UTF-8、长度为 0、解压失败、激活 inf、偶发 NaN：不能只在发现的那张卡 `except: continue`。那张卡少进一次 collective，其余人挂在 all-reduce 上，栈像网络故障。做法是一次小 all-reduce 或广播 skip 标志，**所有 rank 一起跳过这一 step**。偶发损坏可以跳并打计数；比例高说明数据或 tokenizer 坏了，该停，不能靠跳过把 hang 伪装成 NCCL 超时。

文档级去重、质量过滤放在离线；训练循环里只做便宜的 sanity（长度、有限性）。把重去重放进每个 step 的 CPU 路径，loader 会变成 straggler。Pack 过长、某 rank 解压特别慢，先看数据面直方图，再怀疑 GPU。

例如练习按 2048 卡、每卡 4 个 loader worker、mmap indexed dataset 来分析。CPU 解压跟不上时，Nsight 上 GEMM 之间是长空窗，不是 NCCL。加 worker 或预 tokenize 成 token id，比加 TP 有用。Resume 后若没存 shuffle RNG，下一个 epoch 的文档顺序变了，loss 接得上但数据覆盖和评测会漂，过一个月才在重复文档上露馅。

## 追问

**为什么不 token 级 shuffle？**
随机 IO 和巨大索引。文档级洗再 pack，相关 token 仍可能同窗，这是有意的上下文，不是 bug。
**resume 重复看数据有多糟？**
短作业无所谓；万亿 token 若重复一个 epoch 的几个百分点，评测会漂，曲线在恢复点附近假下降。
**坏样本只丢本地行不行？**
不行。控制流上的通信点必须对所有 rank 是常量。变的只能是张量内容。
**packing 和 padding 怎么选？**
预训练要有效 token，默认 pack。要对齐文档、做文档级 loss 再 pad 或用 attention mask，别把两篇粘成一句还当一句。
**blend 权重要不要进 ckpt？**
要。配比 RNG 和文档游标一样，丢了 resume 后语料配比会漂，曲线接上但数据混合物变了。
**mmap 和流式怎么选？**
稳态预训练预建 index 更准、更好 resume。数据还在写、不想预建，用 Streaming / WebDataset，但精确续跑更烦。
