---
id: nvidia-fused-moe
section: nvidia
order: 26
level: S
title: NVIDIA：fused MoE 的 permute、grouped GEMM、unpermute
quick: "先按 expert 把 token 行聚齐，再用 grouped GEMM 处理不同的 $M_i$，最后按原位置乘 top-$k$ 权重合并输出。融合主要省掉 gather、激活和 scatter 的 HBM 往返；decode 时每个专家分到的 token 太少，仍会限制利用率。"
tags:
  - NVIDIA
  - MoE
  - Fused Kernel
  - Grouped GEMM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Scaling Expert Parallelism in TensorRT-LLM (Part 2)
    url: https://nvidia.github.io/TensorRT-LLM/blogs/tech_blog/blog8_Scaling_Expert_Parallelism_in_TensorRT-LLM_part2.html
    type: primary
  - title: Mixture of Experts — Megatron Core
    url: https://docs.nvidia.com/megatron-core/developer-guide/latest/user-guide/features/moe.html
    type: primary
  - title: Mixtral of Experts
    url: https://arxiv.org/abs/2401.04088
    type: primary
  - title: NVIDIA CUTLASS
    url: https://github.com/NVIDIA/CUTLASS
    type: primary
---

fused MoE 先把 token 按 expert 聚齐，再成组计算，最后写回原来的顺序；融合省的是中间数据的搬运。NVIDIA 专家并行博客具体提到 `expandInputRowsKernel`、activation、`finalizeMoeRoutingKernel` 和 grouped GEMM。解释时可以沿这条数据路径，说明哪些步骤能放进同一 CTA，哪些必须等 EP 的 all-to-all 完成。训练侧为什么要避免 $E$ 次 launch，见 `nvidia-moe-gemm`。

## token 怎么从路由走到输出

一层 MoE 的 hidden $x$ 形状是 $[N, D]$。router 为每个 token 选出 top-$k$ expert id 和门控权重，随后 expert $i$ 用下面的 MLP 计算输出：

$$
y_i=\mathrm{SiLU}(x W_{\mathrm{gate},i})\odot (x W_{\mathrm{up},i}),\quad
z_i=y_i W_{\mathrm{down},i}.
$$

$x$ 在内存里按请求 / 序列排，同一 expert 的行不相邻。不 permute 就变成不规则 gather GEMM，Tensor Core tile 对不齐，$M_i=3$ 那种边角会把吞吐打穿。

Permute（有的实现叫 expand / sort）：把 $N\cdot k$ 个 token-expert 对按 expert id 排序，得到 $x_{\mathrm{perm}}$ 和一组 `group_sizes` $[M_0,\ldots,M_{E-1}]$，$\sum M_i=Nk$。CUTLASS grouped GEMM 要求同一核里 $K,N$ 维相同，只允许 $M_i$ 变：MoE 正好满足。再 launch 两次（或三次）grouped：gate/up、down。Unpermute：按逆置换把 $z$ 写回，并

$$
h=\sum_{j=1}^{k} w_{i,j}\,z_{i,j}.
$$

```python
ids, w = router_topk(x, k)                 # [N, k]
xp, sizes, inv = permute(x, ids)           # [N*k, D], M_i
h = silu(grouped_gemm(xp, Wg, sizes)) * grouped_gemm(xp, Wu, sizes)
z = grouped_gemm(h, Wd, sizes)
y = unpermute_weighted(z, inv, w)          # [N, D]
```

Permute / unpermute 本身是 $\Theta(NkD)$ 的带宽核，Megatron 训练侧常单独执行。推理中的 fused 核可以在读取 GEMM 的 A 时完成 gather，在第二段 GEMM 的 epilogue 中完成 scatter 和门控乘法，中间激活也不必完整写回 HBM。FLOPs 没有因此减少，减少的是几次 $NkD$ 数据的往返。

TRT-LLM 的 Triton / CUTLASS / DeepGEMM 后端都走这套骨架。Triton 核注释写得很直：`sorted_token_ids` 按 expert 聚齐并 pad 到 `BLOCK_M` 的倍数，无效 pad 行要 mask，否则脏数据进累加器。

## Decode 时各专家的 $M_i$ 很小

Prefill：$N=B\cdot T$ 可以到几千，即使 $E=64$、$k=2$，$M_i$ 的均值还能喂满 tile。Decode：$N\approx B_{\mathrm{inflight}}$，再除 $E$，很多 expert 的 $M_i$ 是 0 或 1。Grouped 仍比 Python 循环强，但 Tensor Core 利用率差。可以用 IFB 提高瞬时 $B$，见 `nvidia-inflight-batch`。没有足够的 $M$，融不融合都慢。

EP 大于 1：permute 之前先 all-to-all，每卡只看到自己那 $E/\mathrm{EP}$ 个 expert 的 token。NVIDIA 博客写过：naive 实现给每个 expanded token 起一个 CTA，大 EP 时大量 CTA 发现自己是无效 token 直接退出，launch 税比计算还大。后来改成只给有效行起 block。热点 expert 让某 rank 的 $M$ 爆炸，别人空转，这是负载问题不是 GEMM 公式，见 `nvidia-moe-gemm`。

CUDA Graph：`group_sizes` 每步变。要么 pad 到固定容量再 mask，要么 piecewise graph。Fused 核能减少 launch 次数，让 Graph 更容易录，见 `nvidia-cuda-graph`。

融合也有边界。

可以融：token sort 的元数据、第一段 grouped、SiLU$\odot$、量化 cast、第二段 grouped、scatter 加权。不要把 router 的 softmax 硬塞进 GEMM：$E$ 很大时 router 是另一类核。共享 expert（DeepSeek 一类）形状和 routed expert 不同，$K,N$ 不一致，grouped 要求拆核或共享那路单独 GEMM。

FP8 / W4 的 grouped 路径还要带 per-group scale，tile 对齐更烦。质量问题和 dense 量化相同，见 `nvidia-w4a8`。面试顺序：先能画出 permute 前后的 $[N,D]\to[Nk,D]$，再说融合，最后才是 EP。

## 追问

- **不 permute 行不行？** 行，变成 gather GEMM，几乎总更慢。permute 的代价是一次读写，换的是规整 $M_i$。
- **pad 到 `BLOCK_M` 算不算浪费？** Decode 上浪费比例高，这是小 $M$ 带来的额外开销。减小 block 会伤 输入预填充（prefill，即处理输入并建立缓存）。常两套核或按 $N$ 分发。
- **top-$k$ 权重何时乘？** 乘在 down-proj 之后、unpermute 之时，避免门控缩放到中间激活再进第二段 GEMM 的量化范围。有的核融进 epilogue。
- **和 dense MLP 比 FLOPs？** 每 token 只算 $k$ 个 expert，算术上 $k/E$。实际耗时还要加 permute + 不规则 $M$ + all-to-all，MFU 按 dense 套会骗人。

## 相关题

- [[nvidia-moe-gemm]]：本题的前篇，和本题大量重合，讲训练侧为什么不能按专家循环 $E$ 次 GEMM，没有展开融合。
- [[google-moe-routing]]：permute 之前的路由和容量，top-$k$ 选完怎么排 token、超出容量怎么 drop。
- [[xai-moe-decode]]：本题「decode 时 $M_i$ 很小」一节的产品侧版本，专家不齐和连续 batch 碎片。
