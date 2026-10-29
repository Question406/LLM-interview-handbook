---
id: sys-weight-remap
section: systems
order: 44
level: A
title: 系统：训练分片怎么送进 vLLM，为什么不能按 rank 原样拷？
quick: "训练分片和 vLLM 的 TP 布局不同，不能按 rank 直接拷贝。我会按参数名收齐训练分片，再按 QKV 头和 MLP 中间维重切到推理 rank；同步完整后清掉旧前缀缓存，避免新权重继续用旧 KV。"
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

同步权重时要先对齐参数名字和切分布局，不能把训练 rank 原样拷到同号推理 rank。比如 FSDP 按第 0 维切参数，vLLM 的 TP 却按 attention 头切 QKV，缓冲区大小即使对得上，内容也可能放错。

这道题按 verl 的权重加载说明拟定。`load_format` 要匹配训练后端的 loader：Megatron 分片、FSDP DTensor 或 Hugging Face 整模。选错时，下一 token 可能生成错误，训练 loss 仍可能看似正常。

FSDP / ZeRO-3 为了省显存，把每个参数张量切成数据并行份数那么多片，通常沿第 0 维。推理引擎要的是另一刀：QKV 按头拆开，MLP 按中间维拆开，而且 Q、K、V 往往拼在一个线性层里。

同步的顺序是：训练侧按参数 all-gather 出完整张量，或直接产出推理 rank 需要的那一片；推理侧按自己的 TP 布局写入。同机可以用 CUDA IPC，跨机再走集合通信。不能把训练 rank 0 的字节缓冲 memcpy 到推理 rank 0。

verl 的更新路径写完权重后会清 KV 前缀缓存。不清的话，旧权重留下的缓存会被新权重接着用。

## 并行组和加载顺序要一起检查

Megatron 训练若还有流水线，一个推理 rank 要的层可能散在多个流水线 stage 上，要先沿流水线收齐，再按 TP 切开。配置注释写明：Megatron loader 假设输入已经沿 TP 分好、沿 PP 聚好，且名字和形状与推理模型一致。

数据并行大于 1 时，唤醒或释放显存必须广播到全部推理副本。只通知一个 TP 组，另一组还占着权重，训练反向时显存不够。

LoRA 时只传 adapter。全量权重每步都传，带宽会吃掉后训练的步时间。

下面示意把已经收齐的 QKV 按推理 TP 重新切分：

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

**能不能让训练和推理用同一套 TP，省掉重切？**
可以。Megatron 训练配匹配的推理 TP 就能这样做。FSDP 训练没有这套 TP，仍要重切；通常换切分比重写训练并行便宜。

**更新到一半失败了？**
这一步不能 sampling。进程可能持有半新半旧的权重，要丢掉这次同步，恢复上一版完整权重，或整组重载。
