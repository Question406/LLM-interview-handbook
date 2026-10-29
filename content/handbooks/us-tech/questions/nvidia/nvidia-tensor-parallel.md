---
id: nvidia-tensor-parallel
section: nvidia
order: 3
level: S
title: NVIDIA：张量并行切 QKV/MLP，通信是哪一次 all-reduce，和序列并行差在哪
quick: "张量并行沿层内权重矩阵的输入维或输出维切分。Megatron 的 QKV 和 MLP 上投影用列并行，输出投影和下投影用行并行，正向各需一次 all-reduce；序列并行沿激活的 $T$ 维切分，将相应通信组织为 reduce-scatter 和 all-gather，减少 LayerNorm、Dropout 等处的激活副本。"
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

Megatron 的张量并行会把同一层的矩阵乘法分到多张卡上：QKV 和 MLP 上投影按列切，输出投影和下投影按行切。按列切时，每张卡算自己的输出片段；按行切时，每张卡只算出完整输出的一部分贡献，需要把结果相加。因此一层正向的两次 all-reduce，分别落在 attention 输出投影和 MLP 下投影之后。

我会先沿着一层的数据流解释这两次通信，再讲序列并行怎么减少激活副本。整个模型的并行配置见 `nvidia-trillion-train`。

## 一层里切什么

输入 $[B, T, D]$。列并行把 $W$ 沿输出维切开，每卡一份 $[D, D/N]$，输入在 TP 组内是完整的（或 all-gather 之后完整），输出 $[B, T, D/N]$，这段没有 all-reduce。行并行把 $W$ 沿输入维切开，输入已经是分片 $[B, T, D/N]$，局部 GEMM 得到完整宽度的 partial，必须对 partial 求和才得到完整输出。

Transformer 的默认接法（Megatron 论文）：

1. QKV：列并行。每卡拿到一部分 head，shape 大约 $[B, T, H/N, d_h]$。
2. Attention 在本地 head 上算，卡之间不传 $QK^{\top}$。
3. 输出投影：行并行，正向 all-reduce ①，残差加回去。
4. MLP 上投影（$D\to 4D$）：列并行，GeLU 本地。
5. MLP 下投影（$4D\to D$）：行并行，正向 all-reduce ②。

一层正向就是这两次。反向时，列并行各卡对同一输入的梯度贡献需要相加，因此 forward、backward 各有两次 all-reduce。QKV 刚投影后，每卡持有自己的 head，可以先本地做 attention，不需要立即通信。

```python
# x: [B, T, D]，已在 TP 组内对齐
qkv = x @ W_qkv_col  # 列并行，无通信；W 是 [D, 3D/N]
ctx = local_attn(split_heads(qkv))
h = all_reduce(ctx @ W_o_row)  # 行并行，all-reduce ①
h = ln(h + x)
u = gelu(h @ W_fc1_col)  # 列并行，无通信
y = all_reduce(u @ W_fc2_row)  # 行并行，all-reduce ②
return ln(y + h)
```

## 和序列并行差在哪

序列并行沿激活的 $T$ 维切分，权重切法保持原来的 TP。LayerNorm、Dropout 和残差可以各自处理一部分 token：每个 token 的完整 $D$ 维仍留在同一卡，序列的 $T$ 维则分开。没有 SP 时，行并行后面的 all-reduce 让每卡都持有完整 $[B, T, D]$，LN 也在完整序列上做，激活显存按 TP 度数复制。有 SP 时：行并行之后改 reduce-scatter（沿 $T$），每卡只留 $[B, T/N, D]$，LN / Dropout 在分片上做；下一层列并行之前再 all-gather（沿 $T$）把序列拼回来。

再算通信量，一次 all-reduce 的字节数，和 reduce-scatter + all-gather 同阶，都是 $2(N-1)/N$ 倍消息大小。省下的是激活，不是通信。SP 绑在同一个 TP 组上，度数相同；单独说「我做了序列并行」却没有 TP，对不上 Megatron 的实现。

context parallel、ring attention 则进一步切开 attention 本身的 $T$，每卡算一段 Q，K/V 沿环传。这里的 SP 只减少 TP 下 LN 等位置的激活副本，不能解决超长 attention 的 $T^2$ 开销。

两次 all-reduce 的 payload 都是 $[B, T, D]$ 量级，延迟敏感。NVLink 域内（一台 8 卡 $N=8$）通常划得来；跨节点做大 TP，PCIe / IB 延迟会把 kernel 切碎，MFU 掉。所以常见是节点内 TP，节点间 PP / DP。集合算法见 `nvidia-nccl-allreduce`。

可以用 bf16 的例子算数量级： $B=4,T=2048,D=8192$，一次 all-reduce 大约 $134\,\mathrm{MB}$；NVLink 六百 GB/s 只要零点几毫秒。同层 MLP 的 FLOPs 高一个数量级，单节点往往还是计算瓶颈。一上 IB，带宽低一个数量级，TP 就可能变成通信瓶颈。这组数量级能说明为什么通常把 TP 留在机内，并让机间承担 PP、DP。

## 追问

**反向那两次在哪？**
列并行对 $x$ 的梯度要 all-reduce（各卡只看到 $D/N$ 的输出，backpropagation 到完整 $D$ 要对齐）；行并行的权重梯度本地可算。和正向两次配对，不是另起一套拓扑。
**QKV 不 fuse 成一块列并行？**
三次独立列并行也对，通信次数不变，只是 kernel 启动变多。fuse 是为了占满 Tensor Core，不是为了少一次 all-reduce。
**ZeRO-3 能替代这两次 all-reduce 吗？**
不能直接替代。ZeRO-3 分片保存参数，使用时仍要组装对应矩阵来算；TP 才把层内大 GEMM 的计算分给多卡。万亿 dense 通常两个都要，见 `nvidia-trillion-train`。
**vocab 并行呢？**
embedding / softmax 沿 vocabulary 切，那是另一组 all-reduce / all-gather，不要算进「一层两次」里。
