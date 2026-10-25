---
id: tencent-beyond-deepspeed
section: systems
order: 211
level: A
title: 腾讯混元：除了 DeepSpeed，训练还能靠哪些优化？
quick: "先量瓶颈，再选优化：显存紧就看状态分片、checkpoint 和 offload；算不满就查算子、padding 和数据供给；跨机通信慢就调并行布局。微调还要先考虑 LoRA / QLoRA，冻结底座后优化器成本会大幅下降。"
tags:
  - Tencent
  - Hunyuan
  - Training Systems
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯-混元大模型面经-华5硕
    url: https://www.nowcoder.com/feed/main/detail/692fed73109e4d31915e46d34d27c762
    type: candidate-first-hand
  - title: Megatron-LM
    url: https://arxiv.org/abs/1909.08053
    type: primary
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

除了 DeepSpeed，还可以从计算图、激活显存、算子和可训参数几层优化。先看峰值显存、MFU 和 step time 里的通信等待，再结合参数量 $N$ 选对应手段，才能说明每项优化解决了什么问题。72B 全参和 72B LoRA 的成本差很多，应该先问清训练方式。

如果放不下，ZeRO / FSDP 能分片参数状态；activation checkpoint 用重算换显存；CPU / NVMe offload 把优化器甚至参数搬出去，以速度换空间。长序列的 activation 不在 ZeRO 分片范围内，还要考虑减序列长度、序列并行 / 上下文并行，或者 checkpoint。开了 ZeRO-3，8k 监督微调（SFT）仍可能出现显存或数值异常。

如果算不满，可以考虑 FlashAttention、fused softmax / LayerNorm、MoE permute 融合、更大的有效 micro-batch 和通信重叠。先查 GPU 是在等 all-reduce、被 padding 稀释，还是 data loader stall。FlashAttention 降低 $T^2$ 工作区，改善同一层的计算与激活峰值，但它不切参数，也不替代 ZeRO。

如果跨节点慢，就检查 TP size 是否跨过节点、PP 的 micro-batch 是否合理，采用 1F1B 等方式减少 PP bubble。小模型过早使用 ZeRO-3，每层 gather 的代价可能比计算还大，继续加分片会更慢。SP/CP 切序列激活，ZeRO 切 DP 维上的状态，长上下文可能两者都需要。

微调先看 LoRA / QLoRA 是否足够。可训参数可以减少两个数量级，优化器状态也随之下降，底座冻结后 FSDP / 单机可能已经够用；若底座仍参与计算、显存还是紧，再叠加分片。显存极紧而吞吐要求不高时，才优先考虑 offload，预训练通常不把它放在最前面。

框架可以点名 Megatron-LM 的 TP/PP、PyTorch FSDP2，或 Megatron-DeepSpeed 混合。TP 切隐层矩阵、PP 切层、SP/CP 切序列、EP 切专家，分别作用于计算图；checkpoint、offload、分片和冻结底座影响要存什么；融合 kernel 则影响同一层怎么算。这几层要解释清楚。

混元这类稠密大模型的常见组合是先用 Megatron TP/PP 让计算图能跑，再用 ZeRO-1/2 放下 Adam，长序列加 checkpoint 或 SP，利用率不足再优化 FlashAttention 和有效 batch。参数状态能放下就可以停在 1/2，避免每层 all-gather；若单卡参数和全参 Adam 已经放不下，再评估 ZeRO-3。面试讲实际经历时，深讲自己用过、量过的那一层即可。

相关：`tencent-zero-123`、`tencent-zero3-qwen72b-mem`、`sys-memory`、`tencent-sft-parameter-gpu-utilization`


## 真题记录

- 公司：腾讯 · 混元
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“除了 DeepSpeed 还有哪些训练优化？”**
