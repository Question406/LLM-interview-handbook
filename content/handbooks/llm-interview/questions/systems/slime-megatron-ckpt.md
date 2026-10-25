---
id: slime-megatron-ckpt
section: systems
order: 255
level: A
title: slime 为什么不能直接 load HuggingFace 权重？`torch` 和 `torch_dist` 差在哪？
quick: "slime 的 Megatron 训练端需要自己的层名和 TP/PP/EP 分片，HF 权重要先转换。老格式 `torch`（`mp_rank_*`）受原 TP/PP 限制，推荐的 `torch_dist`（`.distcp`）能按当前并行度重切；SGLang 另用 `--hf-checkpoint` 做推理。"
tags:
  - slime
  - Megatron
  - Checkpoint
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
---

slime 的训练端用 Megatron，HF 权重需要先转换成 Megatron ckpt，不能直接按 HF `from_pretrained` 的方式加载。原因是 Megatron 有自己的层名和 TP/PP/EP 切分，还要提供 `--num-layers` 等结构参数，这些参数可以复用 pretrain 脚本。veRL 常用的 FSDP 路径更接近 HF 格式，所以使用体验会不同。

Megatron 把线性层按并行组切开，state dict 的 key 和 shard 边界都不是 HF 的 `model.layers.i.*`。并行度变了，同一份连续张量的切法也变。所以训练入口是 `--ref-load` / Megatron 路径，并显式填层数、隐层、头数、MoE 专家数。漏填结构参数，加载时会因张量形状不匹配而报错，而不是默默 reshape。

slime 训练用 packing / varlen，最大上下文不必靠 `--seq-length` 决定。这个参数更多沿用 Megatron 的旧习惯，含义和 HF `max_position_embeddings` 不同。

- **`torch`（`mp_rank_*`）**：每个 rank 一个目录，并行度锁死。换 TP/PP 必须重切或按原并行拉起。
- `torch_dist`（`.distcp`）：一份 ckpt 能按当前 TP/PP/EP 重切，slime 推荐。MoE 还要 EP/ETP 能整除 world size，否则专家对不齐。

这两种格式的区别是：`torch` 是「按当时切分冻住的分片」；`torch_dist` 是「可再切的分布式 ckpt」。改并行先换 `torch_dist`，不要先改 `--tensor-model-parallel-size` 再赌旧目录能 load。

训练用 Megatron 路径（常见 BF16 `torch_dist`）；生成训练轨迹的 rollout 端用 `--hf-checkpoint`（可走 FP8 推理权）。GLM 大 MoE 脚本里就是「BF16 给 Megatron，FP8 HF 给 SGLang」。两边不是同一份文件，靠 `update_weights` 对齐，见 `slime-sglang-native`、`slime-weight-sync`。训练端和采样端需要分别准备对应格式的权重。

## 追问

**veRL 为什么看起来能直接 HF？**
FSDP 路径的 key 更接近 HF；Megatron 路径同样要转换。slime 默认绑 Megatron，没有这条捷径。
**改 TP 必须重转吗？**
`torch` 必须；`torch_dist` 可按新并行 load。生产留 `torch_dist`。
**`--hf-checkpoint` 能拿来训吗？**
给 SGLang 做推理/采样。训练图要 Megatron 格式，否则层名和 shard 对不上。
**MoE 整除是什么约束？**
专家数与 EP/ETP、world size 要对齐，否则某个 rank 分到残缺专家，load 或 forward 直接失败。
