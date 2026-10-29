---
id: meta-pytorch-compile
section: meta
order: 11
level: A
title: Meta：torch.compile / 图编译在训练栈里能省什么、何时关掉
quick: >-
  torch.compile 用 Dynamo 抓图、Inductor 融合算子，减少小 kernel 的启动、内存读写和 Python 开销。大 GEMM
  已经饱和时收益有限；调试 NaN、频繁重编译或 graph break 太多时，我会先回 eager 排查，或只编译固定形状的 block。
tags:
  - Meta
  - PyTorch
  - torch.compile
  - Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: torch.compile tutorial
    url: 'https://pytorch.org/tutorials/intermediate/torch_compile_tutorial.html'
    type: primary
  - title: torch.compiler — PyTorch docs
    url: 'https://pytorch.org/docs/stable/torch.compiler.html'
    type: primary
  - title: PyTorch 2.0
    url: 'https://pytorch.org/get-started/pytorch-2.0/'
    type: primary
  - title: FullyShardedDataParallel — PyTorch docs
    url: 'https://pytorch.org/docs/stable/fsdp.html'
    type: secondary
---

`torch.compile` 主要减少小算子的启动、内存读写和 Python 调度开销，是否值得开要看热路径。例如一层中 RMSNorm、RoPE、残差和 SwiGLU 的逐元素操作很多，融合可能有收益；如果时间几乎全花在已饱和的大 GEMM 上，收益就较小。

## 能省什么

栈大致是：Dynamo 在 Python 里追踪、画出 FX 图 → AOTAutograd 拆出前向后向 → Inductor 生成融合 kernel（GPU 上常见是 Triton）。相对 eager：

- **算子融合：** 一串 pointwise（add、mul、silu）合成一个 kernel，少读全局内存。
- **更少的 kernel launch：** Transformer 一层里几十个小 kernel，launch 和 CPU 调度会占实际耗时。Compile 后 launch 变少。
- **少一层 Python：** eager 每步都在 Python 里走 autograd；编译后热路径在生成代码里。

矩阵乘的 FLOPs 不会因此变少。大 GEMM 已经被 cuBLAS / FlashAttention 吃满时，compile 的边际小。收益出在 memory-bound 的小算子和 Python 开销。Llama 式 decoder 层：RMSNorm、RoPE、残差、SwiGLU 的逐元素部分，往往比再抠一版大 GEMM 更值得 compile。

`mode="reduce-overhead"` 会走 CUDA Graph，进一步砍 launch，但对 **静态 shape** 更苛刻。`max-autotune` 第一次更慢，换 throughput。因此第一次迭代要单独记作编译时间，benchmark 从 warmup 之后计算。

和 FSDP 一起用（`meta-fsdp2`）：FSDP2 的设计目标之一就是更好跟 compile 组合。FSDP1 的 `FlatParameter` 和 graph break 更常见。compile 与 FULL_SHARD 组合是否加速，仍要看 graph break 日志和实测。

## 何时关掉，或缩小范围

遇到下面这些情况，我会先关掉编译排查，或缩小编译范围：

1. **调试数值：** NaN、和 eager 对不齐、要逐层打印。Compile 会融掉中间张量，diff 很难看。先 `torch.compile(..., disable=True)` 或对子模块不包。
2. **动态 shape：** 每个新的 $(B,T)$ 都可能再编译。推荐训练变长序列、LLM 变长 pack，会变成频繁的重新编译。处理：pad 到桶、`dynamic=True` 并接受一次更泛的图，或只 compile 固定 shape 的主干。
3. **Graph break：** `.item()`、Python 侧 `if tensor>0`、打印、部分集合通信、自定义 autograd。Break 越多，越接近 eager，还多了框架开销。`fullgraph=True` 用来暴露 break，生产别默认开。
4. **稀疏 embedding / all-to-all：** DLRM 那种动态下标 + 不规则通信（`meta-dlrm`）很容易碎图。Compile MLP、别硬 compile 整张表 lookup。
5. **短作业：** 编译时间几分钟，fine-tune 只跑几百 step，可能净亏。Pretrain 长跑才摊得平。

动态控制流不影响编译独立的静态 block，可以把 data-dependent 路由留在外面。Compile 也可以与 FSDP / FlashAttention 组合：前者分参数，后者优化 attention 核，compile 则减少已有图中的 launch。

排查时先打开 `TORCH_LOGS=graph_breaks` 或 `torch._dynamo.explain`，列出 break 点。再对比 eager / compile 的 kernel 数和 GPU 利用率。利用率已经 $95\%$ 且全是大 GEMM，compile 排不上队。CPU 打满、GPU 空、小 kernel 密，才值得开。

图编译作用在单卡或单 rank 的热路径上，与并行轴切分可以叠加。我会先验证并行正确，再 compile 热路径；并行切分见 `nvidia-trillion-train`。

## 追问

**第一次 step 特别慢？**
在编译。warmup 若干步再计 throughput。不要把编译时间算进 MFU。
**和 `torch.jit` / `torch.fx` 手工导出？**
Compile 是自动抓图；JIT 要可脚本化。现在训练栈默认 compile，不要现场改写一遍 TorchScript。
**能 compile 带 FSDP 的整网吗？**
目标是能。实践中先 compile Transformer block，集合通信和 checkpoint boundaries 当图的边。FSDP2 + compile 是正在完善的方向，用 break 日志说话，不要吹已经零 break。
**推理呢？**
同样能融合 decode 路径上的算子，但 KV cache 变长是动态 shape。Prefill 定长更容易吃到 CUDA Graph。
