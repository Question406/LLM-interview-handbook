---
id: code-fused-ce
section: coding
order: 58
level: S
title: 手写融合 Linear + Cross Entropy：不要物化 $[N,V]$ logits
quick: "把 loss 拆成 $\\ell_i=-h_i^\\top W_{y_i}+\\mathrm{logsumexp}_v(h_i^\\top W_v)$：第一项只要 gather 目标那一行，第二项把词表分块做 GEMM，边算边维护 online logsumexp。这样显存从 $O(NV)$ 降到 $O(N\\cdot\\mathrm{chunk})$，完整的 $[N,V]$ logits 从来不落地。"
tags:
  - CrossEntropy
  - Fusion
  - Memory
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Efficient Cross-Entropy (Megatron / Apex style)
    url: https://github.com/NVIDIA/apex/tree/master/apex/contrib/xentropy
    type: primary
---

## 题目描述

实现线性词表投影与交叉熵的组合运算，按词表分块计算，避免完整保存 N×V logits。此题只要求 PyTorch 数值参考版本，不要求编写 CUDA 内核。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `fused_linear_ce(h,weight,target,chunk=128)`。h 为 [N,D] 隐藏状态，weight 为 [V,D] 投影权重，target 为 [N] 整数标签，范围 0 到 V-1；chunk 为正的词表块大小。

### 输出与约束

返回长度 N 的逐样本交叉熵，不取均值；其值应等于对 h@weight.T 做普通交叉熵。支持最后一个词表块不足 chunk，保留可训练梯度；本题不含 `ignore_index`。

### 示例

```text
h=[[0],[0]], weight=[[1],[2]], target=[0,1], chunk=1
每行两个 logits 都是0，返回 [ln(2),ln(2)]≈[0.693147,0.693147]。
```

## 解题思路与参考答案

融合 Linear + Cross Entropy 的做法是把每个 token 的 loss 拆成两项：$\ell_i=-h_i^\top W_{y_i}+\mathrm{logsumexp}_v(h_i^\top W_v)$。第一项只要把目标 token 那一行权重 gather 出来做点积；第二项把词表切成小块，一块一块做 GEMM，同时维护一个 online logsumexp。整个过程只保留 hidden 和一小段词表的 logits，完整的 $[N,V]$ 从来不落地。

先算一下为什么要这么做。$V=128\mathrm{k}$、$N=B T=8\mathrm{k}$、$d=4096$ 时，logits 有 $NV$ 个 fp32，就是几个 GB。直接 `logits = h @ W.T` 再 `cross_entropy`，形状是对的，但显存这一关的追问过不去。

## 分块 logsumexp

每来一块 logits $z_{\mathrm{blk}}$，更新 running max 和 running sum：

$$
m\leftarrow\max(m,\;\mathrm{rowmax}(z_{\mathrm{blk}})),\quad
s\leftarrow s\,e^{m_{\mathrm{old}}-m}+\sum e^{z_{\mathrm{blk}}-m}.
$$

最后 $\mathrm{lse}=m+\log s$，$nll=-h\cdot W_y+\mathrm{lse}$。

```python
import torch

def fused_linear_ce(h, weight, target, chunk=128):
    # h: [N,D], weight: [V,D], target: [N]
    nll = -(h * weight[target]).sum(-1)
    m = h.new_full((h.size(0),), -float("inf"))
    s = h.new_zeros(h.size(0))
    for v0 in range(0, weight.size(0), chunk):
        z = h @ weight[v0:v0 + chunk].T          # [N, chunk]
        bm = z.amax(-1)
        nm = torch.maximum(m, bm)
        s = s * (m - nm).exp() + (z - nm[:, None]).exp().sum(-1)
        m = nm
    return nll + m + s.log()
```

`chunk` 取 1024 还是 4096 看显存。这和 FlashAttention 的 online softmax 是同一个递推，只是归约的维度从 $S$ 换成了 $V$。有 `ignore_index` 的话，把那几行的 $nll$ 乘 0，算 mean 时只除以有效 token 数。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

词表大小 5、chunk=2 可以覆盖最后一个不满块。把逐样本结果与先完整投影再调用标准交叉熵的结果比较，并确认更换 chunk 不影响值。

```python
torch.manual_seed(7)
h, weight = torch.randn(3, 2), torch.randn(5, 2)
target = torch.tensor([0, 2, 4])
expected = torch.nn.functional.cross_entropy(h @ weight.T, target, reduction="none")
for chunk in (1, 2, 8):
    torch.testing.assert_close(fused_linear_ce(h, weight, target, chunk), expected)
print("simple tests passed")
```

## 追问

**和 `F.cross_entropy` 对得上吗？**
必须对上，这是默写完要做的检查。chunk 大小只影响显存，不影响数值。

**TP 下词表切分怎么办？**
每张卡拿 $V/P$ 的一块，先算本地的 lse，再 all-gather 做一次 logsumexp。手写写单卡就行。

**加 label smoothing 呢？**
目标不再是单个 token，$nll$ 变成对所有 $v$ 的加权和。照样能融合，只是公式长一些。
