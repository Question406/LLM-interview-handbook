---
id: apple-mask-pack-unpack
section: tensor
order: 3
level: S
title: cumsum＋scatter/gather：按 mask 压缩 token 并还原
quick: >-
  将 valid 展平做 cumsum，得到每个真实 token 的全局紧凑下标；scatter 写入 packed，gather
  按下标还原。用额外的零行处理无效位置，避免 -1 索引误读最后一个 token。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - Cumsum 矩阵 Mask
  - 完整编程练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: PyTorch cumsum
    url: 'https://docs.pytorch.org/docs/2.14/generated/torch.cumsum.html'
    type: primary
  - title: PyTorch Tensor.scatter
    url: 'https://docs.pytorch.org/docs/2.14/generated/torch.Tensor.scatter.html'
    type: primary
  - title: PyTorch gather
    url: 'https://docs.pytorch.org/docs/2.14/generated/torch.gather.html'
    type: primary
---

## 题目描述

原创 tensor 练习。建议限时 30 分钟。你要压缩带任意空位的 token 特征，再还原到原布局，供变长 batch 与稀疏处理使用。

### 输入与接口

实现两个函数：

- `pack_by_mask(x, valid)`：x 为 `[B,T,D]` 有限浮点 tensor，valid 为同设备 `[B,T]` bool tensor。D 为正，B、T 可为 0；valid 可有任意空位。
- `unpack_by_index(packed, index)`：输入为前一函数产生的 packed 和 index，保证匹配，不要求处理重复或非法下标。

### 输出与约束

pack 返回 `(packed, cu, index)`。packed 是 `[N,D]`，按 batch 优先、行内从左到右保存所有有效 token，N 为有效总数；cu 是 long `[B+1]`，以 0 开始，是每行有效数的 prefix sum；index 是 long `[B,T]`，有效处写全局 packed 下标，无效处为 -1。

unpack 返回 `[B,T,D]`，有效处恢复原特征，无效处为 0。数据 tensor 保持 x 的 dtype/device 与自动求导路径，不修改输入。必须用 cumsum 生成 index，并在 pack/unpack 中分别使用 scatter 和 gather；不写逐样本/逐 token 循环，不经 NumPy 重建数据。

### 示例

```text
x=[[[1,10],[2,20],[3,30]], [[4,40],[5,50],[6,60]]]
valid=[[True,False,True],[False,True,False]]
packed=[[1,10],[3,30],[5,50]]
cu=[0,2,3]，index=[[0,-1,1],[-1,2,-1]]
还原=[[[1,10],[0,0],[3,30]], [[0,0],[5,50],[0,0]]]
```

## 解题思路与参考答案

有效位置的 prefix sum 每遇到 True 增一，因此减一后恰好得到唯一、不重复的全局下标。scatter 只写有效位置，避免多个 padding 共用 -1 或某个位置而互相覆盖。

还原时在 packed 末尾追加一行零，把无效下标映射到这行，再统一 gather；即使 N=0 也有合法的零行可读。

```python
import torch


def pack_by_mask(x, valid):
    batch, length, dim = x.shape
    flat_valid = valid.reshape(-1)
    compact = flat_valid.long().cumsum(0) - 1
    index = compact.masked_fill(~flat_valid, -1).reshape(batch, length)
    total = int(flat_valid.sum())
    target = compact[flat_valid, None].expand(-1, dim)
    packed = x.new_zeros((total, dim)).scatter(
        0, target, x.reshape(-1, dim)[flat_valid]
    )
    cu = torch.cat(
        [torch.zeros(1, dtype=torch.long, device=x.device), valid.sum(-1).cumsum(0)]
    )
    return packed, cu, index


def unpack_by_index(packed, index):
    total, dim = packed.shape
    table = torch.cat([packed, packed.new_zeros((1, dim))], dim=0)
    safe = torch.where(index >= 0, index, total).reshape(-1, 1).expand(-1, dim)
    return table.gather(0, safe).reshape(*index.shape, dim)
```

时间与主要空间为 $O(BTD+ND)$，包含还原输出。此题 N 是动态长度，`int(...)` 在 GPU 上可能引入同步；生产内核可使用预分配容量或其他动态形状协议，但不要以此改变本题输出语义。cu 按每行有效数计算，空行会形成重复 document offsets。

## 简单测试怎么写

实现和测试放进 `solution.py`，运行 `python3 solution.py`，需要 PyTorch。先检查题面例子，再对恢复值求和 backpropagation：有效位置 gradient 应为 1，无效位置为 0。补全空 batch 与全无效场景。

```python
x = torch.tensor(
    [[[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]], [[4.0, 40.0], [5.0, 50.0], [6.0, 60.0]]],
    requires_grad=True,
)
valid = torch.tensor([[True, False, True], [False, True, False]])
before = x.detach().clone()
packed, cu, index = pack_by_mask(x, valid)
assert packed.tolist() == [[1.0, 10.0], [3.0, 30.0], [5.0, 50.0]]
assert cu.tolist() == [0, 2, 3]
assert index.tolist() == [[0, -1, 1], [-1, 2, -1]]
restored = unpack_by_index(packed, index)
assert torch.equal(restored, x.detach() * valid[..., None])
restored.sum().backward()
assert torch.equal(x.grad, valid[..., None].expand_as(x).to(x.dtype))
assert torch.equal(x.detach(), before)
assert cu.dtype == index.dtype == torch.long
z = torch.randn(2, 3, 2, requires_grad=True)
p, c, i = pack_by_mask(z, torch.zeros(2, 3, dtype=torch.bool))
assert p.shape == (0, 2) and c.tolist() == [0, 0, 0]
zero = unpack_by_index(p, i)
assert torch.equal(zero, torch.zeros_like(z))
zero.sum().backward()
assert torch.equal(z.grad, torch.zeros_like(z))
for shape in [(0, 3, 2), (2, 0, 2)]:
    empty = torch.empty(shape)
    p, c, i = pack_by_mask(empty, torch.empty(shape[:2], dtype=torch.bool))
    assert unpack_by_index(p, i).shape == shape
    assert c.shape == (shape[0] + 1,)
```

## 面试追问

**为什么不让 padding 的 index 为 0？** 会与第一个有效 token 混淆。即使输出再乘零，也可能已经做了不正确的写入或读取；应使用明确标记和独立占位行。

**同一个输入被 gather 多次时 gradient 怎样？** 对同一个源位置累加。本题映射保证有效位置唯一，但其他复用场景需要理解 gradient accumulation 和设备上的确定性限制。

**cu 能直接用于所有 attention 内核吗？** 不一定。内核还可能要求 int32、连续内存、最大长度与特定 packing 约定。此题输出 long，接入前按接口范围安全转换并校验。
