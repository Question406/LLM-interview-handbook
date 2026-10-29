---
id: google-jax-pjit
section: google
order: 8
level: S
title: Google：jax.pjit / shard_map 面试怎么讲 SPMD 和编译时切分
quick: >-
  SPMD 让每张芯片运行同一份程序、处理自己的数据分片。带 sharding 的 `jax.jit`（原 `pjit` 能力）按 PartitionSpec
  在编译期安排切分和集合通信；`shard_map` 则让函数看见局部块，由程序员显式写 `psum`。选哪种方式取决于是否需要控制局部通信。
tags:
  - Google
  - JAX
  - pjit
  - SPMD
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Distributed arrays and automatic parallelization (JAX)
    url: >-
      https://jax.readthedocs.io/en/latest/notebooks/Distributed_arrays_and_automatic_parallelization.html
    type: primary
  - title: shard_map docs (JAX)
    url: 'https://jax.readthedocs.io/en/latest/notebooks/shard_map.html'
    type: primary
  - title: GSPMD — General and Scalable Parallelization for ML Computation Graphs
    url: 'https://arxiv.org/abs/2105.04663'
    type: primary
---

## 可以这样回答

`pjit` 的核心是把数组怎样分片告诉编译器，让它生成同一份 SPMD 程序，在每张芯片的数据块上执行。比如写完整的 `x @ w`，编译器会根据分片方式安排局部乘法和通信。这里讲的是带 PartitionSpec 的 `jax.jit`：文档中 `jax.experimental.pjit.pjit` 已弃用，对应能力并入 `in_shardings` / `out_shardings`。Mesh 轴含义见 `google-tpu-mesh`。

SPMD = Single Program Multiple Data。编译器产出一份 XLA 可执行文件，广播到 mesh 上每张芯片。芯片 $i$ 不跑「if rank==i」的分支去执行别的图；它只持有数组的一个 shard，遇到需要完整张量的算子时，图里已经插了 all-gather / reduce-scatter / all-reduce。

## 技术备查

`pjit` 的核心是把数组怎样分片告诉编译器，让它生成同一份 SPMD 程序，在每张芯片的数据块上执行。比如写完整的 `x @ w`，编译器会根据分片方式安排局部乘法和通信。这里讲的是带 PartitionSpec 的 `jax.jit`：文档中 `jax.experimental.pjit.pjit` 已弃用，对应能力并入 `in_shardings` / `out_shardings`。Mesh 轴含义见 `google-tpu-mesh`。

SPMD = Single Program Multiple Data。编译器产出一份 XLA 可执行文件，广播到 mesh 上每张芯片。芯片 $i$ 不跑「if rank==i」的分支去执行别的图；它只持有数组的一个 shard，遇到需要完整张量的算子时，图里已经插了 all-gather / reduce-scatter / all-reduce。

这和「主机 `for` 循环 8 次、每次切一片」不同：切分发生在 编译，运行时是同步的 SPMD 步。也和「每台机器一份完整副本做 DDP」不同：权重本身也可以是分片的。

逻辑上看完整 matmul $Y=XW$，$X$ 为 `[B, D]`，$W$ 为 `[D, H]`。若 $B$ 沿 `data` 切、$H$ 沿 `model` 切，每芯算一块局部 GEMM，再在需要的轴上归约。你在 Python 里写的仍是 `x @ w`。

用 pjit 或带 sharding 的 jit 时，先标注输入输出怎么切，再由 GSPMD 推导中间张量和通信：

```python
from jax.sharding import Mesh, NamedSharding, PartitionSpec as P

mesh = Mesh(devices.reshape(4, 2), ("data", "model"))
in_x = NamedSharding(mesh, P("data", None))
in_w = NamedSharding(mesh, P(None, "model"))
out_y = NamedSharding(mesh, P("data", "model"))


@jax.jit
def f(x, w):
    return x @ w


y = f(x, w)  # 运行前 device_put 到对应 sharding
```

老写法是 `@pjit(in_shardings=(P("data", None), P(None, "model")), out_shardings=P("data", "model"))`。语义一样：编译器看见全局 shape，插入通信。适合整网训练步。

`shard_map` 采用另一种视角：函数体内的 shape 就是单芯局部块的形状。要跨芯求和就自己 `jax.lax.psum` / `psum_scatter`。适合 MoE dispatch、自定义集合通信、或你不信任自动切分的那一层。自动切分很强，但遇到数据相关路由，声明式经常被迫 padding；`shard_map` 把「每芯那一块」露出来。

`pmap` 是更老的「沿 batch 映射、每设备一份」。新代码用 jit sharding 或 `shard_map`。别在 2026 年还把 pmap 当大规模训练默认。

第一次 `jit` 按静态 shape、静态 mesh、静态 PartitionSpec 追踪。之后同样 shape 走缓存的可执行文件。所以：

- 动态 $T$、动态专家容量，会重编译或必须 pad 到编译时上界。TPU 上这就是 MoE / 变长 decode 的额外编译或补齐开销。
- 切分标错：要么隐式 reshard（多一次通信，难查），要么显式模式直接报错。新版 `shard_map` 在 explicit 模式下，输入 PartitionSpec 不匹配会当断言失败。
- 数值：不同切分 $\Rightarrow$ 不同归约树 $\Rightarrow$ 非 bitwise 相同。功能测试应允许适当的数值误差；要 bitwise，PaLM 那种跨 Pod 要对着同一套归约来，见 `google-palm-pathways`。

常见误区是：把 `pjit` 说成「JAX 的 DataParallel」；说切分发生在每个 Python 步由运行时决定；把 `shard_map` 和 `vmap` 混成一个 map。`vmap` 加的是 batch 维，默认还在单设备（除非带 `spmd_axis_name`）。

## 追问

**为什么不手写全部 all-reduce？**
整模型上百层，手写易漏一次 gather。声明切分让中间激活的通信跟权重走。只在编译器插得差的地方下降到 `shard_map`。

**和 PyTorch FullyShardedDataParallel？**
都是参数分片。JAX 把切分编进图；PyTorch 多是模块包装 + 运行时 hook。面试抓「何时通信」，根据实现机制比较框架。

**`with_sharding_constraint` 干什么？**
给中间激活钉切分，防止编译器选一条通信更差的布局。长上下文激活常要钉。

**单机 CPU 能测 SPMD 吗？**
可以起多 CPU 设备的 mesh 测逻辑切分，测不出 ICI 延迟。性能结论必须回 TPU 拓扑，见 `google-tpu-mesh`。
