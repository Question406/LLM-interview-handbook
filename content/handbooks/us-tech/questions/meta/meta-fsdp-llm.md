---
id: meta-fsdp-llm
section: meta
order: 24
level: S
title: Meta：FSDP 训 LLM 的具体坑——prefetch、wrap policy、activation
quick: >-
  Wrap 粒度用 Transformer block，不要整网一块、也不要每个 Linear 一块。Backward prefetch 用
  `BACKWARD_PRE` 把下一层 all-gather 和本层反传重叠。Activation checkpoint 必须和 wrap 单位对齐，否则 backward
  会多一次 all-gather。FSDP 不切激活，长序列照样要 checkpoint / 序列并行。
tags:
  - Meta
  - Llama
  - FSDP
  - Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: FullyShardedDataParallel — PyTorch docs
    url: https://pytorch.org/docs/stable/fsdp.html
    type: primary
  - title: FSDP advanced tutorial
    url: https://docs.pytorch.org/tutorials/intermediate/FSDP_advanced_tutorial.html
    type: primary
  - title: PyTorch FSDP — Experiences on Scaling Fully Sharded Data Parallel
    url: https://arxiv.org/abs/2304.11277
    type: primary
  - title: fully_shard (FSDP2)
    url: https://docs.pytorch.org/docs/stable/distributed.fsdp.fully_shard.html
    type: primary
---

`meta-fsdp2` 讲切什么、和 ZeRO-3 对齐。本题是 **Llama 预训练 / 继续训** 上场会踩的三件事：wrap、prefetch、activation。405B 长窗阶段（`meta-llama3-pretrain`）激活比参数更疼，只背 FULL_SHARD 过不了。

## Wrap policy：峰值显存和通信次数

FSDP 的峰值不只是 $P/N$，还有**当前 unit 的完整参数缓冲**。整网一个 unit：一次 all-gather 把 70B 拼回来，炸。每个 `Linear` 一个 unit：一层里 $q,k,v,o$ 和 SwiGLU 三路各一次 collective，启动延迟吃掉带宽，prefetch 也叠不好。

Llama 默认 wrap `LlamaDecoderLayer`（attn + MLP + 两个 RMSNorm）。通信按层走，缓冲大约一层完整权。Embedding 和 `lm_head` 单独成 unit；若权重 tying，不要把同一份矩阵 wrap 两次。FSDP1 用 `transformer_auto_wrap_policy`；FSDP2 自底向上对每个 block `fully_shard`。自顶向下先包外层，内层切不动。

混合精度：参数/计算 bf16，梯度 reduce 用 fp32，避免小模型也能出现的溢出。`limit_all_gathers=True` 限制同时在飞的 all-gather，长窗时激活已经顶满，再叠多个完整层缓冲会 OOM。这是用吞吐换稳定，不是玄学开关。

## Prefetch：重叠还是抢 HBM

时间线见 `meta-fsdp2`：每层 forward all-gather → 算 → reshard；backward 再 all-gather → 算 → reduce-scatter。不 prefetch，集合通信和 GEMM 串行。

- **Backward prefetch `BACKWARD_PRE`：** 本层反传计算时，提前 all-gather 下一层（按反传顺序的下一层）参数。教程写这是默认该开的，换 $2\%\sim 10\%$ 量级吞吐、略高显存。LLM 反向是大头，这是主旋钮。
- **Forward prefetch：** 算第 $\ell$ 层时拉第 $\ell+1$ 层。文档更谨慎：执行图要静态，CPU 跟不上时才有明显收益。再多一份完整层缓冲。长 $T$ 时激活优先，forward prefetch 往往先关。
- **`CUDA_DEVICE_MAX_CONNECTIONS=1`：** 会把通信和计算排进同一条队列，重叠消失。别为了「确定性」把它开成 1 还抱怨 FSDP 慢。

Prefetch 的显存是「多驻留一个 unit 的未切分权」。70B 一层大约几 GB 量级，要和 activation checkpoint 一起算，不能只看参数分片表。

## Activation：FSDP 不管、还不能和 wrap 打架

激活仍是 $O(B\cdot T\cdot L\cdot d)$。FULL_SHARD 切的是权、梯、Adam，**不切激活**。8k → 128k，激活先爆。该上的是：FlashAttention、activation checkpoint、序列并行（`sys-act-checkpoint`、`sys-seq-parallel`）。CPU offload 权救不了 128k 的激活。

和 checkpoint 的经典坑：HuggingFace `gradient_checkpointing=True` 和 FSDP wrap 套在同一层上，backward 可能 **每层两次 all-gather**：重算 forward 一次，正式 backward 再一次。Issue 里 Llama 13B 单机就复现过。做法：关掉 HF 内置开关，用 `apply_activation_checkpointing` + `CheckpointImpl.NO_REENTRANT`，wrap 集合和 checkpoint 集合对齐到同一个 `LlamaDecoderLayer`。Reentrant checkpoint 和 FSDP 的参数视图更容易打架。

选择性 checkpoint：重算廉价的 RMSNorm / SwiGLU 逐元素，注意力若已经是 Flash、反向重算很贵，就别把整层一刀切。现场说「checkpoint 和 wrap 同边界，先对齐通信，再抠哪些子模块重算」。

`torch.compile` 想融 block 内部，不要把 FSDP unit 切到 Linear。FSDP2 的设计目标之一就是少 graph break，见 `meta-pytorch-compile`。先通信正确，再 compile。

## 追问

- **为什么 DDP 小模型更快？** 没两次 all-gather。参数分得下就别上 FULL_SHARD。LLM 用 FSDP 是因为 Adam 状态是 $8$ 字节 $\times 2$ 再加 fp32 副本，不是因为 FSDP 天生更快。
- **HSDP 呢？** 机内切、机间复制（或按 mesh 反过来）。机间少一次每层全量 all-gather，适合 NVLink 快、跨机慢。长窗激活仍要自己管。
- **Optimizer 要不要 all-gather？** Step 在分片上做。全局 grad norm 对分片做一次归约。不要想象成把 Adam 拼回来。
- **和 PP 一起？** 可以。PP 切层、FSDP 切层内状态。prefetch 和 microbatch 抢流，比单用 FSDP 更脆。405B 公开叙事是大规模集群，现场不要编他们的 PP 段数。
