---
id: code-softmax-stable
section: coding
order: 40
level: A
title: 手写数值稳定 Softmax：减 max、全 mask 行、以及和 CE 的关系
quick: "沿计算轴先减最大值再 $\\exp$ 和归一化，分布不变，指数落在 $(0,1]$ 不会上溢。整行都被 mask 成 $-\\infty$ 时会出 NaN，要把这一行的概率置 0。"
tags:
  - Softmax
  - Numerics
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Deep Learning (Goodfellow et al.), §4.1 / softmax overflow
    url: https://www.deeplearningbook.org/contents/numerical.html
    type: primary
---

## 题目描述

实现数值稳定且支持mask的softmax，包括一个query没有任何可见位置时的明确输出约定。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `softmax_stable(x,dim=-1,mask=None)`。x为浮点张量，归一化维非空；未屏蔽位置的logits有限。mask为可广播到x的布尔张量，True表示保留；全False行是允许的合法输入。

### 输出与约束

返回同形同dtype张量；有效位置等于该行有效logits的softmax，屏蔽位置为0，全部被屏蔽的行也全部为0。内部用float32计算，避免较大有限logits带来数值溢出。无需为NaN、无穷等非法logits添加检查。

### 示例

```text
x=[[1000,1000]]
无mask -> [[0.5,0.5]]
mask=[[True,False]] -> [[1,0]]
mask=[[False,False]] -> [[0,0]]
```

## 解题思路与参考答案

数值稳定的 softmax 就是沿计算轴先减掉最大值，再取 $\exp$ 和归一化。分子分母同乘一个常数，分布不变，最大项变成 $e^0=1$，就不会上溢。另一个要处理的是整行都被 mask 掉的情况，那一行会算出 NaN，要把概率置 0。

白板上最常写错的也就是这两处：直接 `exp(x)` 再除；causal 或 padding 把一整行打成 $-\infty$ 之后照样去做 softmax。Attention 的分数矩阵见 `code-attention`，交叉熵见 `pdd-ce-handwrite`。

$$
\mathrm{softmax}(x)_i=\frac{e^{x_i-m}}{\sum_j e^{x_j-m}},\qquad m=\max_j x_j.
$$

$m$ 是当前计算轴上的最大值。Attention 沿 key 维算，把 `[B,H,T,S]` 归约成 `[B,H,T,1]`。减掉 $m$ 以后，最大项是 $e^0=1$，其余都 $\le 1$，fp16 下也不容易上溢。

全 mask 行是指所有 $i$ 都有 $x_i=-\infty$，这时 $m=-\infty$，$x-m$ 就是 NaN。逐 token 生成（decode）时碰上左 padding，或者滑动窗口把所有可见的 key 都排除了，就会出现这种行。工程上把这一行的概率写成 0，残差才不会被 NaN 污染。

```python
import torch

def softmax_stable(x, dim=-1, mask=None):
    # mask: True=keep。全被挡住的行压成 0，避免 NaN。
    if mask is not None:
        x = x.masked_fill(~mask, float("-inf"))
    z = x.float()
    z = z - z.amax(dim=dim, keepdim=True)
    p = torch.exp(z)
    p = p / p.sum(dim=dim, keepdim=True)
    return p.nan_to_num(0.0).to(x.dtype)
```

和交叉熵放在一起看：$\ell=-z_y+\mathrm{logsumexp}(z)$，别先 softmax 再取 `log`。`logsumexp` 内部也是先减 max。FlashAttention 的 online 版本把 max 和 sum 拆成了递推，见 `code-flash-attn-fwd`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

相同的大 logits 应得到各 0.5，验证减 max 避免上溢。再测只留一个位置和全 mask 行，预期分别是 [1,0] 与 [0,0]。

```python
x = torch.tensor([[1000., 1000.]])
torch.testing.assert_close(softmax_stable(x), torch.tensor([[0.5, 0.5]]))
torch.testing.assert_close(softmax_stable(x, mask=torch.tensor([[True, False]])), torch.tensor([[1., 0.]]))
y = softmax_stable(x, mask=torch.tensor([[False, False]]))
assert torch.isfinite(y).all()
torch.testing.assert_close(y, torch.zeros_like(x))
print("simple tests passed")
```

## 追问

**减 max 会改变分布吗？**
不会。分子分母同乘 $e^{-m}$，分布不变。

**为什么常转 fp32？**
低精度下 $e^{x-m}$ 的小项容易下溢成 0，累加起来误差更明显，所以常先用 fp32 算，再转回原来的类型。

**temperature 放在哪一步？**
先算 $z/T$，再走上面这段。$T\to 0$ 时别真的除以 0，直接 argmax。完整顺序见 `code-sampling`。
