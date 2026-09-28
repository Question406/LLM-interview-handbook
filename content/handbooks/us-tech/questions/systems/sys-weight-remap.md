---
id: sys-weight-remap
section: systems
order: 44
level: A
title: 系统：训练分片怎么送进 vLLM，为什么不能按 rank 原样拷？
quick: >-
  FSDP 常把一个参数沿第 0 维切开。vLLM 的张量并行按注意力头和 MLP 的隐藏维切。
  同步时要按名字把训练分片拼成推理要的那一刀，再送进对应 rank。更新权重之后清掉前缀缓存。
tags:
  - Post-train
  - FSDP
  - vLLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: verl rollout 配置，权重加载格式
    url: https://verl.readthedocs.io/en/latest/examples/config.html
    type: primary
  - title: vLLM rollout 的 update_weights
    url: https://github.com/verl-project/verl/blob/0a1c5b64/verl/workers/rollout/vllm_rollout/vllm_rollout.py
    type: primary
---

## 题怎么来的

这道是按 verl 的权重加载说明拟的。配置里 `load_format` 要选和训练后端匹配的 loader：Megatron 的分片、FSDP 的 DTensor、或 Hugging Face 的整模。选错了，名字对得上，切分对不上，生成的下一 token 是乱的，loss 还可能看起来正常。

## 两套切分

FSDP / ZeRO-3 为了省显存，把每个参数张量切成数据并行份数那么多片，通常沿第 0 维。推理引擎要的是另一刀：QKV 按头拆开，MLP 按中间维拆开，而且 Q、K、V 往往拼在一个线性层里。

同步的顺序是：训练侧按参数 all-gather 出完整张量，或直接产出推理 rank 需要的那一片；推理侧按自己的 TP 布局写入。同机可以用 CUDA IPC，跨机再走集合通信。不能把训练 rank 0 的字节缓冲 memcpy 到推理 rank 0。

verl 的更新路径写完权重后会清 KV 前缀缓存。不清的话，旧权重留下的缓存会被新权重接着用。

## 会错的地方

Megatron 训练若还有流水线，一个推理 rank 要的层可能散在多个流水线 stage 上，要先沿流水线收齐，再按 TP 切开。配置注释写明：Megatron loader 假设输入已经沿 TP 分好、沿 PP 聚好，且名字和形状与推理模型一致。

数据并行大于 1 时，唤醒或释放显存必须广播到全部推理副本。只通知一个 TP 组，另一组还占着权重，训练反向时显存不够。

LoRA 时只传 adapter。全量权重每步都传，带宽会吃掉后训练的步时间。

## 代码

```python
import torch

def fsdp_to_tp_qkv(full_qkv, tp_rank, tp_size, n_heads, head_dim):
    # full_qkv: [3 * n_heads * head_dim, hidden], gathered from FSDP
    d = n_heads * head_dim
    q, k, v = full_qkv.split(d, dim=0)
    h = n_heads // tp_size
    s = slice(tp_rank * h * head_dim, (tp_rank + 1) * h * head_dim)
    return torch.cat([q[s], k[s], v[s]], dim=0)
```

## 追问

**能不能让训练和推理用同一套 TP，省掉重切？** 可以，Megatron 训练加匹配的推理 TP 时就是这条路。FSDP 训练没有这套 TP，省不掉。换切分比重写训练并行便宜。

**更新到一半失败了？** 推理进程还是半新半旧的权重。这一步不能用来采样。丢掉这次同步，用上一版完整权重，或者整组重载。
