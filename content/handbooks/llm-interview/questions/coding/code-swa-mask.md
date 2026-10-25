---
id: code-swa-mask
section: coding
order: 44
level: A
title: 手写 Sliding Window Attention：prefill 的带状 mask 和 decode 怎么切 cache
quick: "query $i$ 只看 $[i-w+1,\\,i]$ 这一段：prefill 用带状下三角 mask，decode 只保留窗口内的 key。窗口外的旧 KV 可以直接丢，cache 从 $O(S)$ 降到 $O(w)$。"
tags:
  - SlidingWindow
  - Attention
  - KV Cache
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Mistral 7B
    url: https://arxiv.org/abs/2310.06825
    type: primary
---

## 题目描述

构造滑动窗口因果注意力的可见性mask，明确窗口是否包含query自身，以及decode时使用的绝对位置。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `swa_causal_keep(q_pos,k_pos,window)`、`swa_prefill_mask(T,window,device=None)`、`swa_decode_mask(past,window)`。位置为可广播的整数张量；window≥1，T≥1，past≥0表示已有token数。

### 输出与约束

True表示key可见：必须满足`k_pos`≤`q_pos`且`k_pos`>`q_pos`-window，窗口计入query自身。prefill返回[T,T]布尔张量，位置为0到T-1；decode返回[past+1]，新query位置为past，key位置为0到past。

### 示例

```text
T=4,window=2 ->
[[True,False,False,False],
 [True,True,False,False],
 [False,True,True,False],
 [False,False,True,True]]
past=3,window=2 -> [False,False,True,True]
```

## 解题思路与参考答案

Sliding Window Attention 就是在因果 mask 上再加一个下界：query $i$ 只看 $[i-w+1,i]$。prefill 时这是一条带状的下三角 mask，decode 时只留窗口里的 key，cache 也就只存最近 $w$ 个。和 `code-attention` 的全因果比，keep 集合只多了这一个条件。

举个数，$w=4096$ 时，位置 $10000$ 只看 $5905..10000$。常见写错有两种：窗口写成 $|i-j|\lt w$ 却忘了因果，未来 token 混进了可见范围；或者逐 token 生成（decode）时还用 `triu(T,T)`，这时 $T=1$，和 cache 长度对不上。

## keep 条件

$$
\mathrm{keep}(q,k)=(k\le q)\land(k>q-w).
$$

Gemma-2 是每隔几层插一层全因果，其余 local 层用 SWA。手写先把 local 层写对。

```python
import torch

def swa_causal_keep(q_pos, k_pos, window):
    return (k_pos <= q_pos) & (k_pos > q_pos - window)

def swa_prefill_mask(T, window, device=None):
    q = torch.arange(T, device=device)[:, None]
    k = torch.arange(T, device=device)[None, :]
    return swa_causal_keep(q, k, window)          # [T,T], True=keep

def swa_decode_mask(past, window, device=None):
    # query 绝对位置 = past，keys 长度 S = past+1
    k = torch.arange(past + 1, device=device)
    return swa_causal_keep(past, k, window)       # [S]
```

decode 的实现可以只在 cache 里留最近 $w$ 个 K/V，这样 mask 就全是 True。前缀复用时要小心：fork 出来的 cache 如果已经按窗口裁剪过，就再也访问不到更早的 token。和 sink 一起用见 `code-attn-sink`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

T=4、窗口为 2 时，每个 query 只能看自己和前一个位置。逐行写出布尔矩阵，再检查 decode 的最后一行与 prefill 一致。

```python
expected = torch.tensor([[1, 0, 0, 0], [1, 1, 0, 0],
                         [0, 1, 1, 0], [0, 0, 1, 1]], dtype=torch.bool)
assert torch.equal(swa_prefill_mask(4, 2), expected)
assert torch.equal(swa_decode_mask(3, 2), expected[-1])
assert torch.equal(swa_prefill_mask(3, 1), torch.eye(3, dtype=torch.bool))
print("simple tests passed")
```

## 追问

**复杂度降了多少？**
attention 从 $O(T^2)$ 降到 $O(Tw)$。预填充（prefill）仍然要处理全部 $T$ 个位置，但每个 query 只和 $w$ 个 key 算注意力。

**窗口外的 token 还有用吗？**
有，信息能一层一层往前传，和 CNN 的感受野一样。Mistral 就是靠深度把远处的信号递过来。

**GQA 和 SWA 一起用怎么写？**
先 repeat KV，再 mask。cache 按 $H_{\mathrm{kv}}\times w$ 算。
