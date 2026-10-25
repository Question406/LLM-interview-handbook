---
id: meta-fsdp-llm
section: meta
order: 24
level: S
title: Meta：FSDP 训 LLM 的具体坑——prefetch、wrap policy、activation
quick: "LLM 的 FSDP 通常按 Transformer block 分 unit，用 backward prefetch 重叠参数 gather 和计算，并限制在途完整参数缓冲。Checkpoint 要与 wrap 边界对齐，避免重算额外触发 gather；长序列激活仍需 Flash、重计算或序列并行单独处理。"
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

FSDP 训练 LLM 时，我会先按 Transformer block 设置 wrap，再量 prefetch 的吞吐收益与峰值显存，最后核对 checkpoint 是否重复触发通信。只知道 `FULL_SHARD` 分状态还不够，长窗阶段常是激活先顶满，见 `meta-llama3-pretrain`。

峰值包括 $P/N$ 状态分片和当前 unit 完整参数。整网一个 unit 会一次 gather 70B；每个 `Linear` 一个 unit，又让 $q,k,v,o$ 与 SwiGLU 三路产生许多小 collective，启动开销高、难重叠。Llama 常以 `LlamaDecoderLayer` 为单位，包含 attn、MLP、两个 RMSNorm，Embedding 与 `lm_head` 单独处理。权重 tying 时不能重复 wrap 同一矩阵。

FSDP1 用 `transformer_auto_wrap_policy`，FSDP2 自底向上给 block 调 `fully_shard`，先包外层会妨碍内层切分。参数和计算用 bf16，梯度 reduce 用 fp32 以减轻溢出。`limit_all_gathers=True` 限制在途 gather 数量，避免长窗激活之外再堆多份完整层缓冲，用少一些并发换显存余量。

## Prefetch 和 checkpoint 一起配置

每层 forward gather、计算、reshard，backward 再 gather、计算、reduce-scatter，具体见 `meta-fsdp2`。`BACKWARD_PRE` 在本层反传时提前 gather 反向顺序下一层，教程给出约 $2\%\sim 10\%$ 的吞吐收益，代价是多驻留完整参数。Forward prefetch 在第 $\ell$ 层计算时拉第 $\ell+1$ 层，更依赖静态执行图，CPU 跟不上时更可能有益；长 $T$ 显存紧可先关闭它。

70B 每层完整权重可能是几 GB，prefetch 多出的这一份要与激活一起算。`CUDA_DEVICE_MAX_CONNECTIONS=1` 还可能将计算通信排进同一队列，使重叠消失，需要核对环境配置。

FSDP 不切 $O(B\cdot T\cdot L\cdot d)$ 激活，8k 到 128k 时仍要 FlashAttention、activation checkpoint 或序列并行，见 `sys-act-checkpoint`、`sys-seq-parallel`，仅 CPU offload 权重救不了激活。

HF `gradient_checkpointing=True` 与 FSDP 边界配合不当，可能使每层 backward gather 两次：重算 forward 一次，正式 backward 再一次，Llama 13B 单机 issue 也复现过。可以关 HF 内置开关，改用 `apply_activation_checkpointing` 与 `CheckpointImpl.NO_REENTRANT`，让 checkpoint 集合与 wrap 集合同为 `LlamaDecoderLayer`。Reentrant checkpoint 更容易与参数视图冲突。

先对齐边界与通信，再做 selective checkpoint：RMSNorm、SwiGLU 逐元素等便宜部分可重算，已经使用 Flash 且反向重算贵的注意力不必一概整层重算。`torch.compile` 也更适合融 block 内部，别为它把 FSDP 拆到每个 Linear；先保证通信正确，再看 graph break，见 `meta-pytorch-compile`。

## 追问

**小模型为什么 DDP 更快？**
它少了两次 all-gather，状态放得下时没必要 FULL_SHARD。LLM 采用 FSDP 是为容纳模型状态，不能把它当天然提速方案。如果 Adam 的一阶、二阶矩都用 fp32，每份每参数 4 字节，两份合计 8 字节；若另保留 fp32 参数副本，再加 4 字节。权重和梯度另算，完整估算见 `sys-param-bytes`。

**HSDP 能解决长窗吗？**
它按 mesh 在机内分片、机间复制等，减少慢跨机链路的每层 gather，激活仍要另管。

**优化器要 all-gather 吗？**
本地分片 step 即可，全局梯度范数另外归约，不必把 Adam 拼回。

**可以和 PP 叠吗？**
可以，但 prefetch 与 microbatch 会抢流，配置更敏感。405B 公开资料讨论大集群，不能据此编 PP 段数。
