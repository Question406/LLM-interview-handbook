---
id: nvidia-tensor-parallel
section: nvidia
order: 3
level: S
title: NVIDIA：张量并行切 QKV/MLP，通信是哪一次 all-reduce，和序列并行差在哪
quick: >-
  TP 切的是层内矩阵的列/行，不是样本。QKV 和 MLP 上投影走列并行，本地算完；输出投影和 MLP
  下投影走行并行，正向各一次 all-reduce。序列并行切的是激活的 $T$ 维，把那次 all-reduce 拆成
  reduce-scatter + all-gather，用来省 LayerNorm / Dropout 的激活，不是另一种切权重。
tags:
  - NVIDIA
  - Tensor Parallel
  - Megatron
  - Sequence Parallel
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Megatron-LM — Training Multi-Billion Parameter Language Models Using Model Parallelism
    url: https://arxiv.org/abs/1909.08053
    type: primary
  - title: Scaling Language Model Training to a Trillion Parameters Using Megatron
    url: https://developer.nvidia.com/blog/scaling-language-model-training-to-a-trillion-parameters-using-megatron/
    type: secondary
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: https://arxiv.org/abs/2205.05198
    type: primary
  - title: NVIDIA Megatron-LM
    url: https://github.com/NVIDIA/Megatron-LM
    type: primary
---

## 题怎么来的

NVIDIA 训练 / CUDA / NeMo 岗爱从 Megatron 一层往下挖。万亿怎么切见 `nvidia-trillion-train`；这题更窄。我会先画一层，标 QKV 和 MLP 的权重切在哪一维、正向到底几次集合通信，再主动说序列并行不是「再切一次 TP」。要落到通信落点，别背 3D 并行表。

## 一层里切什么

输入 $[B, T, D]$。列并行把 $W$ 沿输出维切开，每卡一份 $[D, D/N]$，输入在 TP 组内是完整的（或 all-gather 之后完整），输出 $[B, T, D/N]$，这段没有 all-reduce。行并行把 $W$ 沿输入维切开，输入已经是分片 $[B, T, D/N]$，局部 GEMM 得到完整宽度的 partial，必须对 partial 求和才得到真输出。

Transformer 的默认接法（Megatron 论文）：

1. QKV：列并行。每卡拿到一部分 head，shape 大约 $[B, T, H/N, d_h]$。
2. Attention 在本地 head 上算，卡之间不传 $QK^{\top}$。
3. 输出投影：行并行，正向 all-reduce ①，残差加回去。
4. MLP 上投影（$D\to 4D$）：列并行，GeLU 本地。
5. MLP 下投影（$4D\to D$）：行并行，正向 all-reduce ②。

一层正向就是这两次。反向对称：列并行的输入梯度要再 reduce 一次，所以论文说 forward / backward 各两次 all-reduce。把「QKV 切完就要 all-reduce」说出来是常见错法：QKV 刚切完每卡算的是自己的 head，还没有东西需要对齐。

```python
# x: [B, T, D]，已在 TP 组内对齐
qkv = x @ W_qkv_col            # 列并行，无通信；W 是 [D, 3D/N]
ctx = local_attn(split_heads(qkv))
h = all_reduce(ctx @ W_o_row)  # 行并行，all-reduce ①
h = ln(h + x)
u = gelu(h @ W_fc1_col)        # 列并行，无通信
y = all_reduce(u @ W_fc2_row)  # 行并行，all-reduce ②
return ln(y + h)
```

## 和序列并行差在哪

序列并行切的是激活的时间维，不是再切一份权重。LayerNorm、Dropout、残差沿 $D$ 独立、沿 $T$ 可分。没有 SP 时，行并行后面的 all-reduce 让每卡都持有完整 $[B, T, D]$，LN 也在完整序列上做，激活显存按 TP 度数复制。有 SP 时：行并行之后改 reduce-scatter（沿 $T$），每卡只留 $[B, T/N, D]$，LN / Dropout 在分片上做；下一层列并行之前再 all-gather（沿 $T$）把序列拼回来。

通信量：一次 all-reduce 的字节数，和 reduce-scatter + all-gather 同阶，都是 $2(N-1)/N$ 倍消息大小。省下的是激活，不是通信。SP 绑在同一个 TP 组上，度数相同；单独说「我做了序列并行」却没有 TP，对不上 Megatron 的实现。

不要和 context parallel / ring attention 混：那是把注意力自己的 $T$ 切开，每卡算一段 Q，K/V 沿环传。SP 不解决超长注意力的 $T^2$，只解决 TP 下 LN 激活翻倍。

## 通信落在哪、卡往哪摆

两次 all-reduce 的 payload 都是 $[B, T, D]$ 量级，延迟敏感。NVLink 域内（一台 8 卡 $N=8$）通常划得来；跨节点做大 TP，PCIe / IB 延迟会把 kernel 切碎，MFU 掉。所以常见是节点内 TP，节点间 PP / DP。集合算法见 `nvidia-nccl-allreduce`。

粗算：bf16 下 $B=4,T=2048,D=8192$，一次 all-reduce 大约 $134\,\mathrm{MB}$；NVLink 六百 GB/s 只要零点几毫秒。同层 MLP 的 FLOPs 高一个数量级，单节点往往还是计算墙。一上 IB，带宽掉一位，TP 就可能变成通信墙。面试落到「为什么 TP 不跨机」，用这组数量级比背「NVLink 更快」有用。

## 追问

- **反向那两次在哪？** 列并行对 $x$ 的梯度要 all-reduce（各卡只看到 $D/N$ 的输出，反传到完整 $D$ 要对齐）；行并行的权重梯度本地可算。和正向两次配对，不是另起一套拓扑。
- **QKV 不 fuse 成一块列并行？** 三次独立列并行也对，通信次数不变，只是 kernel 启动变多。fuse 是为了占满 Tensor Core，不是为了少一次 all-reduce。
- **ZeRO-3 能替代这两次 all-reduce 吗？** 能把参数打散，但层内 GEMM 仍要一块完整乘。TP 是在算力上切开大矩阵；ZeRO 是在存储上切开状态。万亿 dense 通常两个都要，见 `nvidia-trillion-train`。
- **vocab 并行呢？** embedding / softmax 沿词表切，那是另一组 all-reduce / all-gather，不要算进「一层两次」里。
