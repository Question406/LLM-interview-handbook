---
id: code-attn-sink
section: coding
order: 50
level: A
title: 手写 Attention Sink：固定留下开头几个 token，再加滑动窗口
quick: >-
  在因果 mask 的基础上，只保留开头 $s$ 个 sink token 和最近 $w$ 个 token。开头几个 token 吸走了大量
  attention，纯滑窗把它们丢掉，attention 分布就乱了，所以 decode 时 sink 的 K/V 一直留在 cache 里。
tags:
  - AttentionSink
  - StreamingLLM
  - KV Cache
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28T00:00:00.000Z
sources:
  - title: Efficient Streaming Language Models with Attention Sinks
    url: 'https://arxiv.org/abs/2309.17453'
    type: primary
---

## 题目描述

生成结合固定前缀与局部窗口的因果 attention 可见性矩阵。序列位置从 0 到 T-1，最前面的 sink 个位置称为固定前缀。

### 接口与约束

实现 `sink_window_keep(T, sink, window, device=None)`，返回形状 `[T,T]` 的布尔张量，第一维是 query，第二维是 key。对位置 q 的 query，key k 可见必须同时满足：k 不在 q 的未来，并且 k 位于固定前缀中，或位于以 q 结尾、包含自身的最近 window 个位置中。

T 为正整数，`0 <= sink <= T`，window 为正整数；True 表示可见，False 表示屏蔽。可选 device 决定输出设备。不需要执行 attention 或维护真实 KV 数据。

### 示例

```text
T=5, sink=1, window=2
最后一行(q=4) -> [True,False,False,True,True]
第一行(q=0)  -> [True,False,False,False,False]
```

固定前缀也不能绕过因果限制，较早的 query 不能提前看见尚未到达的前缀位置。

## 解题思路与参考答案

Attention Sink 的写法是在因果 mask 上再加一个条件：只保留开头 $s$ 个 token（sink）和最近 $w$ 个 token，中间的全部丢掉。这么做是因为很多头会把大量 attention 放在开头那几个位置上；纯 SWA（`code-swa-mask`）把位置 0 切掉之后，这些头没了原来的高权重位置，attention 就挤到窗口左沿去了。StreamingLLM 把最初的 $s$ 个 token（常见 $s=4$）当成 sink，和窗口一起保留。

## keep 条件

$$
\mathrm{keep}(q,k)=(k\le q)\land\big[(k\lt s)\lor(k>q-w)\big].
$$

举个例子，位置 $10$、$s=2$、$w=4$ 时，能看到 $0,1$ 和 $7,8,9,10$，中间 $2..6$ 被丢掉。

```python
import torch


def sink_window_keep(T, sink, window, device=None):
    q = torch.arange(T, device=device)[:, None]
    k = torch.arange(T, device=device)[None, :]
    causal = k <= q
    local = k > q - window
    sinks = k < sink
    return causal & (local | sinks)
```

逐 token 生成（decode）时，cache 的布局是 `[sink | last w-1 | new]`。新 token 进来后如果总数超过 $s+w$，就丢掉 sink 后面那个最老的窗口 token，sink 不动。RoPE 要用 token **原来的**绝对位置；cache 里下标变了就从 0 重数的话，sink 的旋转就错了。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

T=5、sink=1、window=2 时，最后一个 query 应看到位置 0、3、4。再检查第一行只能看位置 0，确保 sink 没有突破因果限制。

```python
mask = sink_window_keep(5, sink=1, window=2)
assert mask[-1].tolist() == [True, False, False, True, True]
assert mask[0].tolist() == [True, False, False, False, False]
assert not mask.triu(1).any()
print("simple tests passed")
```

## 追问

**sink 一定是 BOS 吗？**
不一定。论文观察到的是最初几个位置，不要求是特殊 token。有的实现会学一个专门的 sink 占位。

**模型本来就用 SWA 训练的呢？**
Mistral 训练时就是窗口 attention，推理时再加 sink 算是打补丁。从零训的话可以显式加 sink。

**显存能省多少？**
cache 从 $O(S)$ 收到 $O(s+w)$。$s$ 很小，省下来的主要取决于 $w$。
