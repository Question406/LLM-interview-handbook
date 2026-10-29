---
id: p3a-openai-autograd-hillis-steele-scan
section: openai
order: 607
level: S
title: OpenAI：matrix prefix product：手写 backpropagation 与并行扫描
quick: >-
  我会保存 forward prefix product，backward 从后往前累积每个输出传回的 gradient，再按 matrix
  乘法的左右顺序求导。Hillis–Steele 每层读上一层副本，用结合律并行合并；比如左块与右块交换会算错，浮点结果则用容差比较。
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · OpenAI · autograd-hillis-steele-scan
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/autograd-hillis-steele-scan
    type: secondary
---

## 题目描述

实现 matrix 序列的有序前缀乘积及其 backpropagation；matrix 乘法不交换，结果必须保留原始输入顺序。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `prefix(A)`：输入 n 个 D×D matrix，形状 `[n, D, D]`，返回有序 prefix product $P_i = A_0 A_1 \cdots A_i$，形状相同。
- `scan(A)`：用 Hillis–Steele 的分层方式算出同样的 prefix product。各层具有并行读旧层、写新层的执行语义。
- `backward(A, G)`：`G` 与 `A` 同形状，返回标量 $L = \sum_i \langle G_i, P_i \rangle$ 对每个 $A_i$ 的 gradient。
- 输入为形状合法的浮点数组。$n \le 100$，$D \le 20$；`n = 0` 时返回形状为 `[0, D, D]` 的空数组。

### 输入输出示例

```text
A = [[[2]], [[3]]]
prefix(A)                    -> [[[2]], [[6]]]
backward(A, ones_like(A))    -> [[[4]], [[2]]]
```

## 解题思路与参考答案

我会先保存每步 prefix product，避免 forward 原地覆盖反向需要的数据，再从后往前累积 gradient。比如两个 1×1 matrix 2 和 3，前缀是 2、6，gradient 是 4、2；这个小例子能先检查链式法则，随后再处理不可交换的 matrix 和并行扫描。

## 题目

从一段原地做 matrix 乘法的代码出发，先把 forward 改写成能做 autograd 的版本，再手写 backward，最后用 Hillis–Steele 并行扫描计算一串 matrix 的 prefix product。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

backpropagation 要用到 forward 的中间结果。原地 matrix 乘法会把这些中间值覆盖掉，所以改成 autograd 版本的第一步，就是让每一步的输出写到新数组里，并保存反向需要的 tensor。

对 $Y = AB$，如果上游 gradient 是 $\partial L / \partial Y = G$，那么 $\partial L / \partial A = G B^\top$，$\partial L / \partial B = A^\top G$。matrix 链求导时要保持乘法的左右顺序，不能随意交换。

Hillis–Steele 扫描把 prefix product 拆成 $\lceil \log_2 n \rceil$ 层，每层所有位置可以并行计算。它只依赖 matrix 乘法的结合律，不依赖交换律，所以合并时左边的块必须留在左边。结合顺序变了，浮点误差也会变，并行结果和顺序结果可能在末位上不完全一样，比较时要用容差。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `prefix(A)`：输入 n 个 D×D matrix，形状 `[n, D, D]`，返回有序 prefix product $P_i = A_0 A_1 \cdots A_i$，形状相同。
- `scan(A)`：用 Hillis–Steele 的分层方式算出同样的 prefix product。每层都从上一层的副本读，不能在同一层里读到刚写入的值。
- `backward(A, G)`：`G` 与 `A` 同形状，返回标量 $L = \sum_i \langle G_i, P_i \rangle$ 对每个 $A_i$ 的 gradient。
- 形状不是 `[n, D, D]` 或 `G` 形状不符时抛 `ValueError`。$n \le 100$，$D \le 20$；`n = 0` 时返回形状为 `[0, D, D]` 的空数组。

### 输入输出示例

```text
A = [[[2]], [[3]]]
prefix(A)                    -> [[[2]], [[6]]]
backward(A, ones_like(A))    -> [[[4]], [[2]]]
```

1×1 matrix 就是标量：$L = A_0 + A_0 A_1$，所以 $\partial L / \partial A_0 = 1 + A_1 = 4$，$\partial L / \partial A_1 = A_0 = 2$。

### 解题思路与正确性

`scan` 的第 k 层让每个 `out[i]` 变成 `old[i - 2^k] @ old[i]`。第 k 层之后，`out[i]` 是以 i 结尾、长度最多 $2^{k+1}$ 的一段连乘积，所以 $\lceil \log_2 n \rceil$ 层之后每个位置都覆盖了从 0 开始的整段。左边那段始终乘在左边，顺序和顺序 prefix product 一致。

`backward` 从后往前走。$P_i$ 既直接出现在 loss 里（贡献 $G_i$），又通过 $P_{i+1} = P_i A_{i+1}$ 影响后面所有输出。所以 $\partial L / \partial P_i$ 等于 $G_i$ 加上从后面传回来的 $(\partial L / \partial P_{i+1}) A_{i+1}^\top$，代码里后者存在 `from_later` 中。有了 $\partial L / \partial P_i$，再由 $P_i = P_{i-1} A_i$ 得到 $\partial L / \partial A_i = P_{i-1}^\top \, \partial L / \partial P_i$，其中 $P_{-1}$ 是单位 matrix。

反向用的 $P_{i-1}$ 是 forward 保存下来的；如果 forward 原地覆盖了这些前缀，反向就拿不到正确的值。

### 完整参考实现（Python 3）

```python
import numpy as np


def as_matrix_stack(matrices):
    """转成 float 数组并检查形状是 [n, D, D]。"""
    stack = np.asarray(matrices, dtype=float)
    if stack.ndim != 3 or stack.shape[1] != stack.shape[2]:
        raise ValueError(f"expected shape [n, D, D], got {stack.shape}")
    return stack


def prefix(matrices):
    """顺序计算有序前缀积：P_i = A_0 @ A_1 @ ... @ A_i。matrices: [n, D, D]。"""
    stack = as_matrix_stack(matrices)
    products = np.empty_like(stack)
    running = np.eye(stack.shape[1])
    for i, matrix in enumerate(stack):
        running = running @ matrix
        products[i] = running
    return products


def scan(matrices):
    """Hillis–Steele 扫描：第 k 层让 out[i] = old[i - 2^k] @ old[i]，共 ceil(log2 n) 层。

    每层都从上一层的副本 old 读，避免同一层里读到刚写入的新值。
    矩阵乘法不满足交换律，左边的块必须放在左边。
    """
    out = as_matrix_stack(matrices).copy()
    step = 1
    while step < len(out):
        old = out.copy()
        for i in range(step, len(out)):
            out[i] = old[i - step] @ old[i]
        step *= 2
    return out


def backward(matrices, upstream):
    """标量 L = sum_i <G_i, P_i> 对每个 A_i 的梯度。matrices 和 upstream 都是 [n, D, D]。

    P_i = P_{i-1} @ A_i，所以 dL/dA_i = P_{i-1}^T @ dL/dP_i，
    并且 dL/dP_{i-1} = G_{i-1} + dL/dP_i @ A_i^T，从后往前累积即可。
    """
    stack = as_matrix_stack(matrices)
    upstream = np.asarray(upstream, dtype=float)
    if upstream.shape != stack.shape:
        raise ValueError(
            f"upstream shape {upstream.shape} != matrices shape {stack.shape}"
        )
    products = prefix(stack)
    identity = np.eye(stack.shape[1])

    grads = np.zeros_like(stack)
    from_later = np.zeros(stack.shape[1:])  # 后面所有输出经由 P_i 传回来的梯度
    for i in range(len(stack) - 1, -1, -1):
        grad_prefix = from_later + upstream[i]  # dL/dP_i
        left = identity if i == 0 else products[i - 1]
        grads[i] = left.T @ grad_prefix
        from_later = grad_prefix @ stack[i].T
    return grads
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(prefix(small), [[[2]], [[6]]])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

数值结果用 `allclose` 一类带容差的 assertion 检查，并同时确认形状；随机输入固定 seed。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


# 1x1 矩阵就是标量连乘：前缀 [2, 6]，dL/dA0 = 1 + 3 = 4，dL/dA1 = 2
small = np.array([[[2.0]], [[3.0]]])
assert np.allclose(prefix(small), [[[2]], [[6]]])
assert np.allclose(backward(small, np.ones_like(small)), [[[4]], [[2]]])

# 随机 2x2 矩阵：scan 与顺序前缀积一致
rng = np.random.default_rng(2)
matrices = rng.normal(size=(5, 2, 2))
upstream = rng.normal(size=matrices.shape)
assert np.allclose(prefix(matrices), scan(matrices))

# 解析梯度与中心差分一致
grads = backward(matrices, upstream)
eps = 1e-6
for index in np.ndindex(matrices.shape):
    plus = matrices.copy()
    minus = matrices.copy()
    plus[index] += eps
    minus[index] -= eps
    numeric = ((prefix(plus) - prefix(minus)) * upstream).sum() / (2 * eps)
    assert np.isclose(numeric, grads[index], atol=1e-6)

# n = 0 返回空结果
empty = np.zeros((0, 3, 3))
assert prefix(empty).shape == (0, 3, 3)
assert scan(empty).shape == (0, 3, 3)
assert backward(empty, empty).shape == (0, 3, 3)

expect_value_error(prefix, np.zeros((2, 2, 3)))  # 不是方阵
expect_value_error(backward, small, np.ones((1, 1, 1)))  # 上游梯度形状不符
```

### 复杂度与追问

设一次 D×D matrix 乘法的代价是 $O(D^3)$。顺序 forward 和反向都是 $O(nD^3)$。Hillis–Steele 的总工作量是 $O(n \log n \cdot D^3)$，比顺序版多一个 log 因子，换来理论上 $O(\log n)$ 层的并行深度。这份 Python 实现在每层内部仍是顺序循环，并没有真正并行。空间是 $O(nD^2)$。

追问「为什么并行结果和顺序结果有微小差异」：浮点乘加不严格满足结合律，扫描改变了相乘的分组方式，舍入误差就不同。测试要用 `allclose` 之类的容差比较。
