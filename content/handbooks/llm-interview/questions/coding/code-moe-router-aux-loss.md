---
id: code-moe-router-aux-loss
section: coding
order: 17
level: S
title: 手写 MoE router（softmax + top-k）和 Switch 风格 aux loss
quick: >-
  $x\in\mathbb{R}^{T\times d}$ 乘 $W_r$ 得到 logits，softmax 成 $P$，再 top-$k$ 取门控。Aux 用 $N\sum_i f_i P_i$，$f_i$ 是专家实际被选中的频率，$P_i$ 是平均门控概率，梯度走 $P$。我会把 $k=1$ 和 $k\gt 1$ 都写出来，再说清 capacity 和 ties 怎么处理。
tags:
  - MoE
  - Router
  - Aux Loss
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

## 题目描述

实现 MoE 的 top-k 路由与负载均衡辅助损失。输出每个 token 的专家编号、归一化路由权重，以及整批的辅助损失。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `moe_router_aux(x,W_r,k=1)`。x 为 [T,d]，`W_r` 为 [d,N]，T>0且1≤k≤N。先由路由 logits 得到每个 token 对N个专家的概率P。

### 输出与约束

返回 idx [T,k]、gates [T,k]、标量aux。idx按概率选择top-k，gates将所选概率重新归一化为和1。令 `f_i` 为选择了专家i的token比例（每个所选专家记1，不除k），`Pbar_i`为整批平均概率，aux=N*sum(`f_i`*`Pbar_i`)。避免在示例边界上产生并列专家。

### 示例

```text
x=[[1,0],[0,1]], W_r=[[5,0],[0,5]], k=1
idx=[[0],[1]], gates=[[1],[1]], aux=1。
```

## 解题思路与参考答案

我会把 router 写成三段：先打分，再做离散选择，最后加一个能反传的负载均衡惩罚。打分是 $x$ 乘 $W_r$ 再 softmax，选择是 top-$k$，惩罚用 Switch 的 aux loss，$N\sum_i f_i P_i$。现场允许伪代码，但形状必须对。

$N$ 个 expert，token 矩阵 $x\in\mathbb{R}^{T\times d}$，router $W_r\in\mathbb{R}^{d\times N}$：

$$
P=\mathrm{softmax}(xW_r)\in\mathbb{R}^{T\times N}.
$$

Top-$k$ 沿 expert 维取出下标和门控。$k=1$ 时门控就是 $P_{t,i^\star}$；$k\gt 1$ 时常对选中的 $k$ 个概率再归一化。Switch 的 aux 是

$$
\mathcal{L}_{\mathrm{aux}}=N\sum_{i=1}^N f_i P_i,\quad
P_i=\frac{1}{T}\sum_t P_{t,i},\quad
f_i=\frac{1}{T}\sum_t \mathbf{1}[i\in\mathrm{TopK}(t)].
$$

$f$ 是对离散选择的计数，对 logits 的梯度主要走 $P$。完全均匀时 $f_i=P_i=1/N$，$\mathcal{L}_{\mathrm{aux}}=1$。比如所有 token 都挤到同一个专家上，这个专家的 $f_i$ 和 $P_i$ 都接近 1，aux 就会远大于 1，梯度会把它的概率往下压。

```python
import torch
import torch.nn.functional as F

def moe_router_aux(x, W_r, k=1):
    # x: [T, d], W_r: [d, N]
    logits = x @ W_r
    P = F.softmax(logits, dim=-1)
    T, N = P.shape
    val, idx = torch.topk(P, k, dim=-1)
    gates = val / val.sum(dim=-1, keepdim=True)
    chosen = torch.zeros_like(P)
    chosen.scatter_(1, idx, 1.0)
    f = chosen.mean(dim=0)
    P_bar = P.mean(dim=0)
    aux = N * (f * P_bar).sum()
    return idx, gates, aux
```

还有三处细节要能说出来。分数相等时 `topk` 的结果不稳定，要给一个唯一的次序，比如加极小的噪声或者用稳定排序。真正 dispatch 时还要按容量 $C$ 截断，aux 统计的是 router「想选谁」，容量截断属于系统层，别混进这一行公式。如果被问到 DeepSeek 的无辅助损失做法：选择用 `sigmoid(score)+bias` 的 top-$k$，gates 用没加 bias 的分数，相当于 aux 被一个 bias 控制器替换掉了，见 `arch-moe-noaux`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

两个 token 分别偏向不同专家，top-1 下门控权重都应为 1。两专家负载均匀时这里定义的辅助损失为 1，用于检查 token 维和 expert 维是否混淆。

```python
x, router = torch.eye(2), torch.tensor([[5., 0.], [0., 5.]])
idx, gates, aux = moe_router_aux(x, router, k=1)
assert idx.tolist() == [[0], [1]]
torch.testing.assert_close(gates, torch.ones(2, 1))
torch.testing.assert_close(aux, torch.tensor(1.))
print("simple tests passed")
```

## 追问

**$f$ 要不要 detach？**
Switch 原文把 $f$ 当经验频率；实现里常对 one-hot 用 STE，或者直接当常数。我会说「$f$ 统计负载，$P$ 可导」，这样就够了。

**aux 和交叉熵损失（CE）怎么加？**
$\mathcal{L}=\mathcal{L}_{\mathrm{LM}}+\lambda\mathcal{L}_{\mathrm{aux}}$。$\lambda$ 太大会伤害按语义路由。

**怎么测？**
均匀输入下 $f$ 应该接近 $1/N$；再构造一个某个 expert 分数恒大的输入，aux 应该明显大于 1。
