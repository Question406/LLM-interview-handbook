---
id: nvidia-moe-gemm
section: nvidia
order: 19
level: S
title: NVIDIA：MoE grouped GEMM 和专家并行 kernel
quick: >-
  每个 expert 是一次 $[M_i, D]\times[D, D_{\mathrm{ff}}]$，top-$k$ 之后 $M_i$ 又小又不齐。for 循环
  $E$ 次 GEMM 会把 Tensor Core 和 launch 一起浪费。Grouped GEMM 一次核吃进一组不同 $M$ 的矩阵。专家并行先
  all-to-all 把 token 送到持有该 expert 的卡，再在本地 grouped 算。热点 expert 是墙，不是算术公式。
tags:
  - NVIDIA
  - MoE
  - Grouped GEMM
  - Megatron
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Mixture of Experts — Megatron Core
    url: https://docs.nvidia.com/megatron-core/developer-guide/latest/user-guide/features/moe.html
    type: primary
  - title: Mixtral of Experts
    url: https://arxiv.org/abs/2401.04088
    type: primary
  - title: NVIDIA CUTLASS
    url: https://github.com/NVIDIA/cutlass
    type: primary
  - title: NVIDIA Transformer Engine
    url: https://github.com/NVIDIA/TransformerEngine
    type: primary
---

## 题怎么来的

NVIDIA 训 MoE（Megatron-Core / NeMo / Transformer Engine）或用 TensorRT-LLM 伺候 Mixtral / DeepSeek 一类，会问「专家怎么变成一次核」。万亿 dense 的 3D 并行见 `nvidia-trillion-train`；本题是第四轴 EP + grouped GEMM。评委要听 permute、一次 launch、all-to-all，不接受「MoE 就是稀疏 MLP」。

## 为什么 naive GEMM 很慢

一层 MoE：router 给出 $[N, E]$ 的分数，每 token 取 top-$k$（常 $k=1$ 或 $2$）。Expert $i$ 拿到 $M_i$ 行，两段 MLP（或 SwiGLU 的两三次 GEMM）。$N$ 是这步的 token 数（训练里 $B\cdot T$，推理 decode 里接近瞬时 batch）。

错法：对每个 expert 各 launch 一次 GEMM。问题有三：

1. **Launch。** $E=8$ 已经烦，$E=128$ 加上 decode 的短步，host 间隙能比核本身长。CUDA Graph 也难录：$M_i$ 每步在变，见 `nvidia-cuda-graph`。
2. **Tile。** Tensor Core 喜欢 $M$ 对齐到 64/128。$M_i=7$ 的 expert 走边角，占用和吞吐一起掉。这是 decode 路径上 MoE 特有的瘦 $M$，不是泛泛 occupancy 题。
3. **内存不规则。** token 按序列排，不是按 expert 排，每次 GEMM 前都在 gather。

Grouped GEMM（CUTLASS / Transformer Engine 的 grouped linear，Megatron 的 `--moe-grouped-gemm`）：一次核提交一组问题，共享 $K,N$（权重形状一样），只是 $M_i$ 和指针不同。GPU 内部按 expert 调度 CTA，避免 $E$ 次 API。FP8 / MXFP8 的 grouped 路径 TE 也接了，和 dense FP8 配方同一套 Tensor Core，见 `nvidia-fp8`。

```python
# x: [N, D]，先按 expert 排序
x_perm, group_sizes = permute_by_expert(x, expert_ids)  # E 个 M_i
h = silu(grouped_gemm(x_perm, W_gate, group_sizes)) * grouped_gemm(
    x_perm, W_up, group_sizes
)
z = unpermute(grouped_gemm(h, W_down, group_sizes))
```

Permute / unpermute 本身也是带宽核，Megatron 有 router / permute fusion 把 top-k 和辅助损失收短。面试顺序：先 grouped，再融合。

## 专家并行：先搬家，再 grouped

$E$ 大于单卡能放的 expert 数时，每张卡只驻留 $E/\mathrm{EP}$ 个 expert。前向：router 之后 all-to-all（或 all-gather）把 token 送到对应卡，本地 grouped GEMM，再 all-to-all 送回。通信对象是 token 激活 $[M_{\mathrm{local}}, D]$，不是 TP 那种 $[B, T, D]$ 的层内 all-reduce，见 `nvidia-tensor-parallel`。

墙经常不在 GEMM：动态 all-to-all 的形状每步变，热点 expert 让某张卡 $M$ 炸、别的卡空转。Aux loss、expert bias、capacity + drop，是在打负载，不是装饰。Nsight 上看 NCCL 是否和 grouped 重叠，以及各 rank 的 $M_i$ 直方图，见 `nvidia-nccl-allreduce`。

和 TP 叠：每个 expert 内部仍可列 / 行切，通信更碎。Megatron 文档会建议 MoE 路径开序列并行，否则 LN 激活按 TP 复制。并行折叠（attention 一套 TP / CP，MoE 一套 EP）是更新的故事，面试提一句「两套网格可以不对齐」，细节没跑过不装。长上下文那一维仍是 CP，见 `nvidia-megatron-cp`。

推理：decode 每步每条序列只新增 $k$ 个 token-expert 对，$M_i$ 更碎。In-flight 把瞬时 $B$ 做大，才能给 grouped 凑出像样的 $M$，见 `nvidia-inflight-batch`。TRT-LLM 同样走 MoE plugin / grouped，而不是 Python 循环 expert，见 `nvidia-trt-llm`。

## 追问

- **$E$ 个 expert 形状不同怎么办？** Grouped 仍要求同一 kernel 的 $K,N$ 一致。共享 expert + 路由 expert 常拆两次 grouped，或共享那路单独 GEMM 并 overlap。
- **能不用 permute 吗？** 不排就变成不规则 gather GEMM，更慢。排的代价是一次读写 $[N, D]$，通常划得来。
- **Drop token 算不算作弊？** 训练稳定性和负载的取舍；推理一般不 drop，否则质量口子要单开评测。
- **和 dense MLP 比 FLOPs？** 每 token 只算 $k$ 个 expert，FLOPs 按 $k/E$ 稀。但 all-to-all + 小 $M$ 会把墙钟吃回去，所以 MFU 不能按 dense 公式套。
