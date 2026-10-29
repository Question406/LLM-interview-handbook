---
id: google-jax-transformer
section: google
order: 20
level: S
title: Google：用 JAX 写一层 Transformer，shard、scan、remat 怎么摆
quick: >-
  我会先把 decoder block 写成可复用的循环体，再用 `lax.scan` 跨层执行、用 `remat`
  在反向时重算激活；PartitionSpec 负责声明权重和激活在 mesh 上怎么切。这样分别控制编译图大小、激活内存和设备分片，下面的 CPU
  练习只验证 scan / remat 的语义。
tags:
  - 完整编程练习
  - Google
  - JAX
  - Transformer
  - remat
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: Distributed arrays and automatic parallelization (JAX)
    url: >-
      https://jax.readthedocs.io/en/latest/notebooks/Distributed_arrays_and_automatic_parallelization.html
    type: primary
  - title: jax.lax.scan
    url: 'https://jax.readthedocs.io/en/latest/_autosummary/jax.lax.scan.html'
    type: primary
  - title: jax.checkpoint / remat
    url: 'https://jax.readthedocs.io/en/latest/generated/jax.checkpoint.html'
    type: primary
  - title: PaLM — Scaling Language Modeling with Pathways
    url: 'https://arxiv.org/abs/2204.02311'
    type: primary
---

## 题目描述

实现一个可由 JAX scan 执行和重计算的简化 Transformer 堆栈。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`block(h,w)` 返回 `(updated_h,None)`。h 为 `[B,T,D]`，w 含 q/k/v/o `[D,D]`、up `[D,F]`、down `[F,D]` 权重。每层包含单头因果缩放点积 attention 和 SiLU MLP，两分支均为预 RMSNorm 加残差；RMSNorm 使用 eps=1e-6，即 `x/sqrt(mean(x²)+eps)`，无可学习缩放；无 dropout。attention 仅看当前位置及之前位置，分数除以 sqrt(D)，沿 key 轴用 `exp(score)/sum(exp(score))` normalization。MLP 先投影到 F，应用 `SiLU(z)=z*sigmoid(z)`，再投影回 D。

`stack(h,weights,remat=False)` 中权重各叶子的首维为层数 L，用 lax.scan 执行，返回 `[B,T,D]`。remat=True 对层体启用重计算，不改变前向值或梯度。`loop_stack(h,weights)` 用普通循环提供等价接口。stack 要能被 jit 编译。

### 示例

```text
h=[[[1,2],[3,4]]]，L=2，D=F=2，所有层权重全为 0。
block 的 updated_h、stack、loop_stack 均返回原 h。
remat=False 与 True 得到相同输出。
```

## 解题思路与参考答案

我会把隐藏状态作为 `lax.scan` 的 carry，把逐层参数堆成前导层维，再按内存需求给循环体加 `jax.checkpoint`。这样同一个 decoder block 可以逐层执行，反向时按需重算；跨设备切分还需要单独声明 sharding。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + JAX，只在 CPU 上验证 scan / remat 的语义；没有跨设备 sharding，也不能当作 TPU 分片的验收。

### 题面、接口与约束

- `block(h, w) -> (h, None)`：一层 decoder block。单头因果 attention 和 SiLU MLP，前面各有一个 RMSNorm（pre-norm，无可学习 scale），都带残差，没有 dropout。`h` 是 `[B, T, D]`，`w` 是这一层的参数字典：`q`、`k`、`v`、`o` 为 `[D, D]`，`up` 为 `[D, F]`，`down` 为 `[F, D]`。返回值的形式是为了直接当 `lax.scan` 的循环体。
- `stack(h, weights, remat=False)`：用 `jax.lax.scan` 跨层执行 `block`。`weights` 的每个叶子多一个前导层维 $L$，比如 `q` 是 `[L, D, D]`。`remat=True` 时循环体包一层 `jax.checkpoint`。
- `loop_stack(h, weights)`：用 Python `for` 逐层调用 `block` 的对照实现。
- 要求：`stack` 和 `loop_stack` 的前向一致；`remat` 开关不改变前向和梯度；`jax.jit` 下可运行；因果性成立。

### 输入输出示例

```text
L=2, B=1, T=3, D=F=4
stack(h, weights)              -> [1, 3, 4]，与 loop_stack 一致
把 h 的最后一个 token 加 10    -> 输出的前两个位置不变（因果）
```

### 解题思路与正确性

`lax.scan` 的 carry 是隐藏状态 `h`，xs 是按层堆好的参数；每一步取出一层的权重切片，喂给同一个循环体，所以循环体只编译一次，结果和 Python 逐层循环一样。

`jax.checkpoint` 只改变 backpropagation 时保存什么、重算什么，不改变函数本身，所以 `remat=True` 和 `False` 的梯度应该在数值误差内相同。因果性来 self-attention 里的下三角 `keep`：位置 $i$ 只看 $j\le i$，MLP 和 RMSNorm 都是逐位置的，所以改最后一个 token 不会影响前面的输出。

### 完整参考实现（Python 3）

```python
import jax
import jax.numpy as jnp


def rms_norm(x, eps=1e-6):
    """沿最后一维的 RMSNorm，不带可学习 scale。"""
    return x * jax.lax.rsqrt(jnp.mean(x * x, axis=-1, keepdims=True) + eps)


def block(h, w):
    """一层 pre-norm decoder block。h: [B, T, D]；w: 单层参数字典。返回 (h, None) 供 scan 使用。"""
    seq_len, model_dim = h.shape[1], h.shape[-1]
    x = rms_norm(h)
    q = x @ w["q"]  # [B, T, D]
    k = x @ w["k"]
    v = x @ w["v"]
    scores = q @ jnp.swapaxes(k, -1, -2) / jnp.sqrt(model_dim)  # [B, T, T]
    keep = jnp.tril(jnp.ones((seq_len, seq_len), dtype=bool))
    attn = jax.nn.softmax(jnp.where(keep, scores, -jnp.inf), axis=-1)
    h = h + (attn @ v) @ w["o"]
    x = rms_norm(h)
    h = h + jax.nn.silu(x @ w["up"]) @ w["down"]
    return h, None


def stack(h, weights, remat=False):
    """用 lax.scan 跨层执行 block；weights 的每个叶子有前导层维 L。"""
    body = jax.checkpoint(block) if remat else block
    h, _ = jax.lax.scan(body, h, weights)
    return h


def loop_stack(h, weights):
    """Python for 循环的对照实现。"""
    num_layers = weights["q"].shape[0]
    for layer in range(num_layers):
        layer_weights = {name: value[layer] for name, value in weights.items()}
        h, _ = block(h, layer_weights)
    return h
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert scanned.shape == (1, 3, 4)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def make_weights(key, num_layers, model_dim, ffn_dim):
    shapes = {
        "q": (model_dim, model_dim),
        "k": (model_dim, model_dim),
        "v": (model_dim, model_dim),
        "o": (model_dim, model_dim),
        "up": (model_dim, ffn_dim),
        "down": (ffn_dim, model_dim),
    }
    keys = jax.random.split(key, len(shapes))
    return {
        name: jax.random.normal(subkey, (num_layers,) + shape) * 0.1
        for (name, shape), subkey in zip(shapes.items(), keys)
    }


weights = make_weights(jax.random.PRNGKey(0), num_layers=2, model_dim=4, ffn_dim=4)
h = jax.random.normal(jax.random.PRNGKey(1), (1, 3, 4))

# scan 与 Python 层循环的前向一致
scanned = stack(h, weights)
assert scanned.shape == (1, 3, 4)
assert jnp.allclose(scanned, loop_stack(h, weights), atol=1e-6)

# jit 下结果不变
assert jnp.allclose(jax.jit(lambda x: stack(x, weights))(h), scanned, atol=1e-6)

# remat 不改变梯度
grad_plain = jax.grad(lambda x: stack(x, weights, remat=False).sum())(h)
grad_remat = jax.grad(lambda x: stack(x, weights, remat=True).sum())(h)
assert jnp.allclose(grad_plain, grad_remat, atol=1e-5)

# 因果：改最后一个 token 不影响前两个位置
perturbed = h.at[:, 2].add(10)
assert jnp.allclose(stack(perturbed, weights)[:, :2], scanned[:, :2])

# F 与 D 不同时形状也对
wide = make_weights(jax.random.PRNGKey(2), num_layers=3, model_dim=4, ffn_dim=8)
assert stack(h, wide).shape == (1, 3, 4)
assert jnp.allclose(stack(h, wide), loop_stack(h, wide), atol=1e-5)
```

### 复杂度与追问

设层数 $L$、batch $B$、长度 $T$、模型维 $D$、MLP 中间维 $F$。算术量是 $O(LB(TD^2+T^2D+TDF))$，每层的稠密 attention 分数占 $O(BT^2)$。remat 降低反向时保留的激活，代价是多一次前向重算；实际的峰值内存和编译时间要另外测量。

- 追问「为什么不能直接把 PyTorch `nn.Module` 翻成 `jit`」：JAX 的训练步要是一张静态 shape 的 SPMD 图，层循环、分片约束和 remat 策略都要在编译期确定，见下文三件套。

## 题怎么来的

把 decoder block 放到 TPU mesh 上时，要继续说明参数怎样切、层怎样循环，以及哪些激活要保存。`pjit` 的 SPMD 语义见 `google-jax-pjit`，芯片的轴见 `google-tpu-mesh`，MXU 为什么需要大 GEMM 见 `google-tpu-llm`。这里只讲三件套：shard、scan、remat。

## shard：Python 写完整矩阵，编译器去切

激活 $h$ 的形状是 $[B, T, D]$，权重 $W_q$ 是 $[D, D]$。典型的分片方式是 $B$ 走 `data` 轴，$D$ 的输出通道走 `model` 轴。函数里仍然写 `h @ W`，GSPMD 会在需要的轴上插入 all-gather / reduce-scatter。

中间激活如果完全交给编译器选布局，偶尔会多出一次隐式 reshard，MFU 莫名其妙掉下去。长 $T$ 的 attention 输出要用 `with_sharding_constraint` 钉住布局。

动态的 $T$、MoE 的变长 dispatch 会逼着重新编译，或者 pad 到编译期的上界。在 TPU 上这不是细节，而是实打实的耗时。MoE 的静态容量见 `google-moe-routing`。

## scan：层不要在 Python 里展开

96 层在 Python 里用 `for` 展开，XLA 图会非常大，编译要几分钟，HBM 还要给整张图留 workspace。`lax.scan` 把层权重堆成前导轴 $[L, \ldots]$，循环体只编译一次，就是参考实现里的 `stack`：carry 是激活，xs 是按层堆好的参数。

反向时 scan 会再走一遍，和下面的 remat 叠加。`scan` 控制的是编译时间和峰值内存。PaLM / MaxText 这类代码栈都用 scan 堆层，而不是写 118 个 Python 函数。

`scan` 的限制是循环体的 shape 和 sharding 都必须静态，各层结构必须一样。流水线并行（PP）里每个 stage 层数不同，不要硬塞进一个 scan；那是另一条 mesh 轴，见 `google-tpu-llm`。

## remat：用 FLOPs 换激活

不 remat 时，每层都把反向要用的激活留在 HBM。长 $T$ 时这部分按 $B\cdot T\cdot L\cdot D$ 增长，常常比参数还大。`jax.checkpoint`（别名 `jax.remat`）只在 layer boundaries 留一份输入，反向时把这一层的前向再算一遍。参考实现里 `stack(..., remat=True)` 就是 scan 加 remat 的组合。

实际中选择性策略比「每层全部重算」更常见：保存大 GEMM 的输出（MXU 上算得贵，重算不划算），重算 LayerNorm、dropout、softmax 统计量这类便宜的部分。JAX 里 `dots_with_no_batch_dims` 一类 policy 大致就是这个意思。注意和 Flash 式 kernel 的关系：attention 内部本来就不物化 $[T,T]$，这时再以不保存的 attention 分数为 remat 目标就没有收益，见 `google-flash-attention`。

代价是反向多一段前向。如果已经 compute-bound、batch 也喂饱了，多出的 20–30% FLOPs 就是纯开销。如果被 HBM 卡住、microbatch 开不大，用省下的激活把 $B$ 或 $T$ 翻倍，实际耗时往往更好。面试要讲清这个拐点。

常见误区：

- 把 `scan` 说成 `vmap`。`vmap` 是加一个 batch 维，不是循环。
- 说 remat 降低 FLOPs。它增加 FLOPs，降低的是激活内存。
- 在 Python 里对每层嵌套 `jit`，每层一个可执行文件。

## 追问

- **为什么不用 `for` 循环加每层 `jit`？** 每层各有一份编译缓存，看起来能跑；但整步的切分和通信需要对齐，拆开之后中间激活的布局容易漂。训练步应该是一张 SPMD 图。
- **remat 和 ZeRO 先上哪个？** ZeRO / 参数分片砍的是权重和优化器状态，remat 砍的是激活。长上下文时先碰到的是激活。
- **decode 也用 scan 吗？** 训练和 prefill（处理输入并建立缓存）的层循环仍然用 scan。decode 一步 $T=1$，激活不是主要矛盾，KV cache 才是，见 `google-gqa-mqa`。
- **和 PyTorch 的 `torch.utils.checkpoint` 一样吗？** 是同一笔账。区别在于 JAX 的 checkpoint 要和静态图、scan 一起编译，policy 在编译期就定死了。
