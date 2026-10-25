---
id: coding-decode-step
section: coding
order: 33
level: S
title: 白板：一步 decode，取 q、concat KV、GQA repeat、出 logits
quick: "当前 token 在 `cache_len` 位置做 RoPE，把 $k,v$ 沿序列维追加进 cache，再计算注意力和 `[B, 1, V]` logits。cache 始终保留 $H_{\\mathrm{kv}}$ 个头，只在注意力计算时扩展到 $H_q$。"
tags:
  - 完整编程练习
  - Coding
  - Decode
  - GQA
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
  - title: Fast Transformer Decoding — One Write-Head is All You Need
    url: https://arxiv.org/abs/1911.02150
    type: primary
---

## 题目描述

实现带分组查询注意力（GQA）与 KV cache 的一次 decoder 生成调用。输入已经投影并完成位置旋转的本步 Q/K/V，返回词表 logits 以及追加后的紧凑缓存。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `repeat_kv(x, n_rep)`：把 `[B, H_kv, S, D]` 的每个 KV 头连续复制 `n_rep` 次，得到 `[B, H_kv * n_rep, S, D]`，语义等同 `repeat_interleave(n_rep, dim=1)`。
- `decode_step(q, k_t, v_t, cache_k, cache_v, w_o, w_head, n_rep)`：做一步生成。`q` 是 `[B, H_q, 1, D]`，本步的 `k_t`、`v_t` 是 `[B, H_kv, 1, D]`，三者都已经用当前位置做过 RoPE。`cache_k`、`cache_v` 是 `[B, H_kv, S, D]`，$S$ 可以是 0。返回 `(logits, new_cache_k, new_cache_v)`，logits 是 `[B, 1, V]`，新 cache 长度为 $S+1$，仍然只有 $H_{\mathrm{kv}}$ 个头。
- `w_o` 是 `[H_q * D, H_q * D]`，`w_head` 是 `[V, H_q * D]`，按 PyTorch 线性层的约定用 `x @ w.T`。
- 必须满足 `H_q == H_kv * n_rep`。不修改传入的 cache 张量。
- 每个 query head 对应重复后的 KV head，分数为 dot(q,k)/sqrt(D)，对全部缓存及当前 key 做 softmax，加权 V 后按 head 顺序拼成 Hq*D，经过 `w_o` 和 `w_head` 得到 logits。没有 dropout 或额外 bias，输入有限，`n_rep`>=1。

### 输入输出示例

```text
B=Hq=Hkv=D=n_rep=1；旧 cache 长度为 0
q=[[[[0]]]], k_t=[[[[0]]]], v_t=[[[[2]]]]
w_o=[[1]], w_head=[[3],[4]]
decode_step(q,k_t,v_t,empty_cache_k,empty_cache_v,w_o,w_head,1) -> logits=[[[6,8]]]
new_cache_k=[[[[0]]]], new_cache_v=[[[[2]]]]
```

## 解题思路与参考答案

一步 decode 先把本步 $k,v$ 接到 cache 末尾，让当前 query 对所有已缓存 key 计算注意力，再做输出投影和词表层。当前 query 是序列里最新的位置，所有已缓存的 key 都在它之前或就是它自己，所以 $T=1$ 时因果 mask 退化成「全部可见」，不需要再造一张下三角。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，只在 CPU 浮点张量上验证，没有验证 GPU、多卡或性能。

### 题面、接口与约束

- `repeat_kv(x, n_rep)`：把 `[B, H_kv, S, D]` 的每个 KV 头连续复制 `n_rep` 次，得到 `[B, H_kv * n_rep, S, D]`，语义等同 `repeat_interleave(n_rep, dim=1)`。
- `decode_step(q, k_t, v_t, cache_k, cache_v, w_o, w_head, n_rep)`：做一步生成。`q` 是 `[B, H_q, 1, D]`，本步的 `k_t`、`v_t` 是 `[B, H_kv, 1, D]`，三者都已经用当前位置做过 RoPE。`cache_k`、`cache_v` 是 `[B, H_kv, S, D]`，$S$ 可以是 0。返回 `(logits, new_cache_k, new_cache_v)`，logits 是 `[B, 1, V]`，新 cache 长度为 $S+1$，仍然只有 $H_{\mathrm{kv}}$ 个头。
- `w_o` 是 `[H_q * D, H_q * D]`，`w_head` 是 `[V, H_q * D]`，按 PyTorch 线性层的约定用 `x @ w.T`。
- 必须满足 `H_q == H_kv * n_rep`，否则抛 `ValueError`。不修改传入的 cache 张量。

### 输入输出示例

```text
B=2, H_q=4, H_kv=2, n_rep=2, D=2, V=5, cache 长度 S=0
第一步：每个头只有一个 key，注意力权重是 1，输出就是本步的 v
        logits 形状 [2, 1, 5]，new_cache_k 形状 [2, 2, 1, 2]
第二步：传入上一步的 cache，new_cache_k 形状 [2, 2, 2, 2]
```

### 解题思路与正确性

GQA 的 repeat 只在算分数前做，写回的 cache 保持 $H_{\mathrm{kv}}$ 个头。`repeat_kv` 用 `expand` 加 `reshape`，第 $h$ 个 query 头对应第 $\lfloor h / n_{\mathrm{rep}}\rfloor$ 个 KV 头，和 `repeat_interleave` 一致。

### 完整参考实现（Python 3）

```python
import torch


def repeat_kv(x, n_rep):
    """[B, H_kv, S, D] -> [B, H_kv * n_rep, S, D]，每个 KV 头连续复制 n_rep 次。"""
    if n_rep == 1:
        return x
    batch, kv_heads, seq_len, head_dim = x.shape
    expanded = x[:, :, None].expand(batch, kv_heads, n_rep, seq_len, head_dim)
    return expanded.reshape(batch, kv_heads * n_rep, seq_len, head_dim)


def decode_step(q, k_t, v_t, cache_k, cache_v, w_o, w_head, n_rep):
    """一步 decode：追加 KV，GQA 注意力，输出投影和 lm_head。

    q: [B, H_q, 1, D]，k_t / v_t: [B, H_kv, 1, D]，都已做过 RoPE。
    cache_k / cache_v: [B, H_kv, S, D]。返回 logits [B, 1, V] 和长度 S + 1 的新 cache。
    """
    if q.size(1) != k_t.size(1) * n_rep:
        raise ValueError(f"H_q={q.size(1)} must equal H_kv={k_t.size(1)} * n_rep={n_rep}")
    cache_k = torch.cat([cache_k, k_t], dim=2)  # [B, H_kv, S + 1, D]
    cache_v = torch.cat([cache_v, v_t], dim=2)
    k = repeat_kv(cache_k, n_rep)               # [B, H_q, S + 1, D]
    v = repeat_kv(cache_v, n_rep)
    scale = q.size(-1) ** -0.5
    scores = torch.matmul(q, k.transpose(-2, -1)) * scale  # [B, H_q, 1, S + 1]
    probs = torch.softmax(scores.float(), dim=-1).to(q.dtype)
    heads = torch.matmul(probs, v)                         # [B, H_q, 1, D]
    hidden = heads.transpose(1, 2).reshape(q.size(0), 1, -1)  # [B, 1, H_q * D]
    hidden = hidden @ w_o.T
    logits = hidden @ w_head.T                              # [B, 1, V]
    return logits, cache_k, cache_v
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert logits.shape == (2, 1, 5)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


torch.set_num_threads(1)
torch.manual_seed(0)
q = torch.randn(2, 4, 1, 2)
k_t = torch.randn(2, 2, 1, 2)
v_t = torch.randn_like(k_t)
empty_k = torch.empty(2, 2, 0, 2)
empty_v = empty_k.clone()
w_o = torch.eye(8)
w_head = torch.randn(5, 8)

# 空 cache：注意力权重为 1，输出就是本步 v 经过 GQA repeat 后的投影
logits, cache_k, cache_v = decode_step(q, k_t, v_t, empty_k, empty_v, w_o, w_head, 2)
expected = v_t.repeat_interleave(2, 1).transpose(1, 2).reshape(2, 1, 8) @ w_head.T
assert logits.shape == (2, 1, 5)
assert cache_k.shape == (2, 2, 1, 2)
assert torch.allclose(logits, expected)

# 传入的 cache 不被修改，新 cache 只有 H_kv 个头
assert empty_k.shape[2] == 0
assert cache_k.shape[1] == 2

# 第二步：cache 长度加一，结果与手算的 softmax 注意力一致
logits, cache_k, cache_v = decode_step(q, k_t, v_t, cache_k, cache_v, w_o, w_head, 2)
assert cache_k.shape[2] == 2
k_full = cache_k.repeat_interleave(2, 1)
v_full = cache_v.repeat_interleave(2, 1)
probs = torch.softmax(q @ k_full.transpose(-2, -1) / 2 ** 0.5, dim=-1)
expected = (probs @ v_full).transpose(1, 2).reshape(2, 1, 8) @ w_head.T
assert torch.allclose(logits, expected, atol=1e-6)

# repeat_kv 与 repeat_interleave 语义相同；n_rep=1 原样返回
x = torch.randn(1, 3, 4, 2)
assert torch.equal(repeat_kv(x, 3), x.repeat_interleave(3, 1))
assert repeat_kv(x, 1) is x

# 头数对不上时报错
expect_error(ValueError, decode_step, q, k_t, v_t, empty_k, empty_v, w_o, w_head, 3)
```

### 复杂度与追问

设 batch 为 $B$、query 头数 $H_q$、KV 头数 $H_{\mathrm{kv}}$、cache 长度 $S$、头维 $D$、模型宽度 $D_{\mathrm{model}}=H_qD$、词表 $V$。这一步的注意力是 $O(BH_qSD)$，cache 占 $O(BH_{\mathrm{kv}}SD)$，输出投影和词表层另需 $O(BD_{\mathrm{model}}^2+BD_{\mathrm{model}}V)$。

- 追问「`cat` 的问题」：每步都会把整段历史 KV 复制一遍，总代价随长度平方增长。这是教学写法，生产上预分配到最大长度后原地写，或者用分页布局 append，见 `coding-paged-table`。
- 追问「$S$ 很长怎么办」：注意力本身可以按 key 切块并行，再用 log-sum-exp 合并，见 `coding-flash-decode`。

## 题怎么来的

这是 Apple / Meta 手写 Transformer 题的收尾：把 RoPE、KV cache、GQA、lm_head 串成一步生成。OpenAI debug 卷里最常见的植入 bug 是把 decode 按 prefill 的位置逻辑实现，比如用 `arange(q_len)` 得到位置 $0$，或者把 repeat 后的 KV 写进 cache。拆开的部件见 `coding-rope-cache`、`coding-gqa-repeat`、`coding-mq-attn`。验收标准是形状断言通过，并且逐步 greedy 生成的下一个 token 和一次完整 forward 的结果相同。

## 数据沿哪一维增长

进入这一步时，cache 里的 $K,V$ 是 `[B, H_{\mathrm{kv}}, S, D]`，$S$ 是已经处理过的长度（包括输入提示 prompt）。当前隐状态 `[B, 1, D_{\mathrm{model}}]` 投影后得到

$$
q\in\mathbb{R}^{B\times H_q\times 1\times D},\quad
k,v\in\mathbb{R}^{B\times H_{\mathrm{kv}}\times 1\times D}.
$$

RoPE 只旋转这一步的 $q,k$，位置下标 $t=S$：$S$ 是旧长度，$t$ 就是即将 append 的位置。历史的 $K$ 在写入时已经旋转过，不能再转一次。然后沿序列维（shape 里的第 2 维）拼接：

$$
K\leftarrow\mathrm{cat}(K,k),\quad V\leftarrow\mathrm{cat}(V,v)
$$

此时 $S\leftarrow S+1$。cache 本身不 repeat。算 $QK^\top$ 前才 `repeat_interleave` 成 `[B, H_q, S, D]`，fused GQA kernel 则在寄存器里广播。分数是 `[B, H_q, 1, S]`，softmax 沿最后一维，用它对 $V$ 加权得到 `[B, H_q, 1, D]`，再合并各头、做输出投影。最后 lm_head 把 `[B, 1, D_model]` 映射到 `[B, 1, V]`。

滑动窗口、ALiBi、padding 这类约束用 `[1, 1, 1, S]` 的 bias 加上去，见 `coding-swa-mask`、`coding-alibi`、`coding-attn-mask`。

调用方负责三件事：用 `position_ids = cache_len` 做 RoPE，保证 `H_q % H_kv == 0`，以及在 softmax 前加需要的 mask。

## 不变量和常见轴错误

不变量：在同一个前缀上，一步 decode 得到的 $\arg\max$ logits，应该等于把这个 token 接到 prompt 后面做一次因果 prefill、再读最后一个位置的结果。对不上时，先打印 $S$ 和 `position_ids`，再查是不是对 cache 里的 $K$ 又做了一次 RoPE，最后查用的是 `repeat` 还是 `repeat_interleave`。

softmax 的轴必须是 key 长度那一维。写成 `dim=0` 或沿 head 维，就是 `openai-transformer-debug` 里那类 bug；$T=1$ 时沿 $T$ 做 softmax 结果恒为 1，更难发现。MLP 和 RMSNorm 都沿 $D_{\mathrm{model}}$ 计算，和 $S$ 无关，所以逐步生成不会因为「统计量沿序列算」而漂移。

## 追问

**为什么 logits 是 `[B, 1, V]`，不是 `[B, S, V]`？**
一步只需要当前 token 的分类头。算整段既浪费，也容易在 shift 上把自己绕进去。
**先 repeat 再写入 cache 行不行？**
带宽和显存都会乘上 $n_{\mathrm{rep}}$，GQA 省下的东西全白费。repeat 只应该发生在算分数时。
**MQA 怎么处理？**
$H_{\mathrm{kv}}=1$、$n_{\mathrm{rep}}=H_q$，同一个函数照样成立，见 `coding-mq-attn`。

## 相关题

- [[coding-gqa-repeat]]：只拆出 repeat 这一步，专讲 `repeat_interleave` 和 `repeat` 的分组差异和 shape 断言。
- [[coding-mq-attn]]：$H_{\mathrm{kv}}=1$ 的特例，讲 K、V 沿 head 维 broadcast 而不 repeat 进 cache。
- [[meta-gqa-kernel]]：Meta 的 GQA 实现题，追问 kernel 里按 `h_q // g` 取 KV head，不在 HBM 里摊开。
- [[openai-kv-cache-impl]]：从零实现整套 KV cache，要求有/无 cache 的 greedy 逐 token 对齐，这里只写其中一步。
- [[openai-rope-offset]]：专讲这里 RoPE 用 `cache_len` 当位置这一行写错时怎么悄悄出错、怎么查。
