---
id: meta-pytorch-compile
section: meta
order: 11
level: A
title: Meta：torch.compile / 图编译在训练栈里能省什么、何时关掉
quick: >-
  Dynamo 抓图，Inductor 融 kernel、少 launch、把 Python 开销拿掉。省的是小算子墙钟和 CPU 调度，不是算法
  FLOPs。动态 shape、data-dependent 控制流、稀疏 embedding all-to-all、调试 NaN 时要关或缩小
  compile 范围。
tags:
  - Meta
  - PyTorch
  - torch.compile
  - Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: torch.compile tutorial
    url: https://pytorch.org/tutorials/intermediate/torch_compile_tutorial.html
    type: primary
  - title: torch.compiler — PyTorch docs
    url: https://pytorch.org/docs/stable/torch.compiler.html
    type: primary
  - title: PyTorch 2.0
    url: https://pytorch.org/get-started/pytorch-2.0/
    type: primary
  - title: FullyShardedDataParallel — PyTorch docs
    url: https://pytorch.org/docs/stable/fsdp.html
    type: secondary
---

Meta 是 PyTorch 的大本营，训练 / 平台岗会问 `torch.compile` 到底省什么。别答成「编译了就快」。要能说出图怎么抓住、省在 launch 和融合，以及哪些图会碎、该关。

## 能省什么

栈大致是：Dynamo 在 Python 里追踪、画出 FX 图 → AOTAutograd 拆出前向后向 → Inductor 生成融合 kernel（GPU 上常见是 Triton）。相对 eager：

- **算子融合：** 一串 pointwise（add、mul、silu）合成一个 kernel，少读全局内存。
- **更少的 kernel launch：** Transformer 一层里几十个小 kernel，launch 和 CPU 调度会占墙钟。Compile 后 launch 变少。
- **少一层 Python：** eager 每步都在 Python 里走 autograd；编译后热路径在生成代码里。

省的不是「矩阵乘 FLOPs 变少」。大 GEMM 已经被 cuBLAS / FlashAttention 吃满时，compile 的边际小。收益出在 **memory-bound 的小算子 + Python 开销**。Llama 式 decoder 层：RMSNorm、RoPE、残差、SwiGLU 的逐元素部分，往往比再抠一版大 GEMM 更值得 compile。

`mode="reduce-overhead"` 会走 CUDA Graph，进一步砍 launch，但对 **静态 shape** 更苛刻。`max-autotune` 第一次更慢，换吞吐。面试说清：第一次迭代是编译时间，benchmark 要从 warmup 之后算。

和 FSDP 一起用（`meta-fsdp2`）：FSDP2 的设计目标之一就是更好跟 compile 组合。FSDP1 的 `FlatParameter` 和 graph break 更常见。现场别保证「compile + FULL_SHARD 一定加速」，要看 graph break 日志。

## 何时关掉，或缩小范围

我会主动报这些关掉 / 降级的理由：

1. **调试数值：** NaN、和 eager 对不齐、要逐层打印。Compile 会融掉中间张量，diff 很难看。先 `torch.compile(..., disable=True)` 或对子模块不包。
2. **动态 shape：** 每个新的 $(B,T)$ 都可能再编译。推荐训练变长序列、LLM 变长 pack，会变成编译风暴。处理：pad 到桶、`dynamic=True` 并接受一次更泛的图，或只 compile 固定 shape 的主干。
3. **Graph break：** `.item()`、Python 侧 `if tensor>0`、打印、部分集合通信、自定义 autograd。Break 越多，越接近 eager，还多了框架税。`fullgraph=True` 用来**暴露** break，不是生产默认。
4. **稀疏 embedding / all-to-all：** DLRM 那种动态下标 + 不规则通信（`meta-dlrm`）很容易碎图。Compile MLP、别硬 compile 整张表 lookup。
5. **短作业：** 编译时间几分钟，fine-tune 只跑几百 step，可能净亏。Pretrain 长跑才摊得平。

错误答法：「有动态控制流就完全不能用。」可以 compile 静态的 block，把 data-dependent 的路由留在外面。错误答法二：「compile 替代 FSDP / FlashAttention。」它不切参数，也不替代注意力核；是把已经写好的 PyTorch 图跑得更少 launch。

## 现场怎么查

我会说：打开 `TORCH_LOGS=graph_breaks` 或 `torch._dynamo.explain`，列出 break 点。再对比 eager / compile 的 kernel 数和 GPU 利用率。利用率已经 $95\%$ 且全是大 GEMM，compile 不是优先项。CPU 打满、GPU 空、小 kernel 密，才值得开。

和 `nvidia-trillion-train` 的差别：那边是切并行轴；这边是单卡（或单 rank）上的图编译。两者叠：先并行正确，再 compile 热路径。

## 追问

- **第一次 step 特别慢？** 在编译。warmup 若干步再计吞吐。不要把编译时间算进 MFU。
- **和 `torch.jit` / `torch.fx` 手工导出？** Compile 是自动抓图；JIT 要可脚本化。现在训练栈默认 compile，不要现场改写一遍 TorchScript。
- **能 compile 带 FSDP 的整网吗？** 目标是能。实践中先 compile Transformer block，集合通信和 checkpoint 边界当图的边。FSDP2 + compile 是正在收口的方向，用 break 日志说话，不要吹已经零 break。
- **推理呢？** 同样能融 decode 路径，但 KV cache 变长是动态 shape。Prefill 定长更容易吃到 CUDA Graph。
