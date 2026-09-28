---
id: google-jax-transformer
section: google
order: 20
level: S
title: Google：用 JAX 写一层 Transformer，shard、scan、remat 怎么摆
quick: >-
  权重和激活用 PartitionSpec 钉在 mesh 上，编译器插通信。层循环用 `lax.scan` 压编译时间和 HBM 里的图。`remat`
  丢掉中间激活、反向再算一遍。三件叠在一起才是 TPU 上能编译、能放下的训练步；别把 PyTorch
  `nn.Module` 翻译成 `jit`。
tags:
  - Google
  - JAX
  - Transformer
  - remat
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Distributed arrays and automatic parallelization (JAX)
    url: https://jax.readthedocs.io/en/latest/notebooks/Distributed_arrays_and_automatic_parallelization.html
    type: primary
  - title: jax.lax.scan
    url: https://jax.readthedocs.io/en/latest/_autosummary/jax.lax.scan.html
    type: primary
  - title: jax.checkpoint / remat
    url: https://jax.readthedocs.io/en/latest/generated/jax.checkpoint.html
    type: primary
  - title: PaLM — Scaling Language Modeling with Pathways
    url: https://arxiv.org/abs/2204.02311
    type: primary
---

Google 训练代码默认 JAX。白板题经常是：别讲论文故事，写（或口述）一层 decoder block 怎么在 TPU mesh 上跑起来。`pjit` 的 SPMD 语义见 `google-jax-pjit`；芯片轴见 `google-tpu-mesh`；MXU 为什么要大 GEMM 见 `google-tpu-llm`。这里只抠三件套：shard、scan、remat。

## shard：Python 写完整矩阵，编译器切

激活 $h$ 形状 $[B, T, D]$，权重 $W_q$ 形状 $[D, D]$。典型钉法：$B$ 走 `data`，$D$ 的输出通道走 `model`。你在函数里仍写 `h @ W`，GSPMD 在需要的轴上插 all-gather / reduce-scatter。中间激活若让编译器自己选布局，偶发一次隐式 reshard，MFU 莫名掉。长 $T$ 的注意力输出用 `with_sharding_constraint` 钉住。

动态 $T$、MoE 变长 dispatch 会逼着重编译或 pad 到编译期上界。TPU 上这不是细节，是墙钟。MoE 的静态容量见 `google-moe-routing`。

## scan：层不要在 Python 里展开

96 层在 Python 里 `for` 展开，XLA 图巨大，编译要分钟级，HBM 还要给整张图留 workspace。`lax.scan` 把层权重堆成前导轴 $[L, \ldots]$，循环体只编译一次：

```python
def block(h, w):
    # h: [B, T, D]
    x = rms_norm(h)
    h = h + attn(x, w.attn)
    y = rms_norm(h)
    h = h + mlp(y, w.mlp)
    return h, None

def stack(h, weights):
    # weights 每张叶子 [L, ...]
    h, _ = jax.lax.scan(block, h, weights)
    return h
```

carry 是激活，xs 是按层堆好的参数。反向 scan 会再走一遍，和下面 remat 叠。不要把 `scan` 说成「为了写着好看」：它是在控编译时间和峰值内存。PaLM / MaxText 这类栈都是 scan 层，不是 118 个 Python 函数。

`scan` 的限制：循环体静态 shape、静态 sharding。层与层结构必须一样。PP 那种每 stage 层数不同，不要硬塞进一个 scan；那是另一条 mesh 轴，见 `google-tpu-llm`。

## remat：激活换成 FLOPs

不 remat 时，每层把反向要用的激活留在 HBM。长 $T$ 时这份东西按 $B\cdot T\cdot L\cdot D$ 涨，常常比参数还大。`jax.checkpoint`（别名 `jax.remat`）只在边界留一份，反向再前向一遍。

选择性策略比「每层全重算」更常见：保存大 GEMM 输出（MXU 贵、重算不划算），重算 LayerNorm / dropout / softmax 统计（便宜）。JAX 的 `dots_with_no_batch_dims` 一类 policy 接近这个意思。和 Flash 式核的关系：注意力内部已经不物化 $[T,T]$，再 remat「注意力分数」是空靶，见 `google-flash-attention`。

扫描 + remat 的组合：

```python
block = jax.checkpoint(block, policy=jax.checkpoint_policies.dots_with_no_batch_dims)
h, _ = jax.lax.scan(block, h, weights)
```

代价是反向多一段前向。已经 compute-bound、batch 也喂饱了，再付 20–30% FLOPs 是纯税。被 HBM 卡住、microbatch 开不大，用省下的激活把 $B$ 或 $T$ 加倍，墙钟往往更好。面试要讲这个拐点。

错法：把 `scan` 说成 `vmap`（`vmap` 加 batch 维）；说 remat 降低 FLOPs（它增加 FLOPs、降低激活）；在 Python 里对 layer 做 `jit` 嵌套、每层一张可执行文件。

## 追问

- **为什么不 `for` 层 + 每层 `jit`？** 每层一次编译缓存，看起来能跑；整步的切分和通信要对齐，拆开后中间激活布局容易漂。训练步是一张 SPMD 图。
- **remat 和 ZeRO 谁先？** ZeRO / 参数分片砍的是权重和优化器；remat 砍的是激活。长上下文先碰激活。
- **decode 也 scan 吗？** 训练 / prefill 的层循环仍 scan。decode 步 $T=1$，激活不是主矛盾，KV 才是，见 `google-gqa-mqa`。
- **和 PyTorch `torch.utils.checkpoint`？** 同一笔账。JAX 的差别是 checkpoint 必须和静态图、scan 一起被编译，policy 在编译期定死。
