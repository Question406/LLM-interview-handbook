---
id: p3a-apple-cvml-circular-padding
section: tech-screen
order: 71
level: A
title: Apple CVML 面经：手写二维 circular padding，怎样保留自动求导？
quick: >-
  把输出行列映射到原图的模索引，再用 index_select 取值。这样能处理非对称及超过图像尺寸的补边，并保留 gradient；环形补边会改变
  boundary conditions，不能不加分析地替换普通图像的零补边。
companies:
  - apple
tags:
  - 一亩三分地继续检索
  - Apple
  - 一亩三分地
  - 真实面经
  - 完整编程练习
  - PyTorch
  - AFM 专项 2026-10
  - 2026-10 论坛核对第二批
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: 2026-10-26T00:00:00.000Z
sources:
  - title: 水果cvml全套（2025-05-21）
    url: 'https://www.1point3acres.com/bbs/thread-1129820-1-1.html'
    type: interview
  - title: PyTorch torch.nn.functional.pad
    url: 'https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.pad.html'
    type: primary
---

## 题目描述

原帖仅明确 ML coding 要求手写 circular padding，未披露维度、function signature 或 edge-case conventions。下面是手册补充的完整练习约定，不代表原帖全部细节；建议限时 20 分钟。来源为 CVML，不确认属于 AFM Data Team。

### 输入与接口

实现 `circular_pad2d(x, padding)`。x 为 `[B,C,H,W]` 有限浮点 PyTorch tensor，四维大小均为正；padding 是 `(left,right,top,bottom)` 四个非负整数。允许补边超过原始 H/W。x 可以需要 gradient。

### 输出与约束

返回同设备、同 dtype tensor，形状 `[B,C,H+top+bottom,W+left+right]`。输出位置 `(i,j)` 读取原图 `((i-top)%H,(j-left)%W)`；B/C 维不变，不修改输入，保持自动求导。禁止调用现成 pad 函数，禁止经 NumPy 或 Python list 重建数据 tensor。全零 padding 不要求返回同一个对象。

### 示例

```text
x=[[[[1,2],[3,4]]]], padding=(1,1,1,1)
输出=[[[[4,3,4,3],[2,1,2,1],[4,3,4,3],[2,1,2,1]]]]
```

### 来源核对范围

2026-10-26 经 Chrome 读取原帖主楼，正文直接可见；页面发帖时间 2025-05-21 10:23:20，经历字段标 2024 年第四季度，时区未推断。本题任意宽补边语义是练习约定，不声称与库函数所有限制一致。

## 解题思路与参考答案

先构造从负 top 到 H+bottom 的行坐标，再对 H 取模；列坐标同理。两次索引保留批次与通道，重复索引的位置在 backpropagation 时会向同一输入元素累加 gradient。

```python
import torch


def circular_pad2d(x, padding):
    left, right, top, bottom = padding
    height, width = x.shape[-2:]
    rows = torch.arange(-top, height + bottom, device=x.device) % height
    cols = torch.arange(-left, width + right, device=x.device) % width
    return x.index_select(-2, rows).index_select(-1, cols)
```

时间按输出元素量计为 $O(BC(H+t+b)(W+l+r))$；除了输出还会创建中间按行扩展的 tensor 和两个索引向量。超大补边会增加显存，即使索引构造本身很小。GPU 上重复索引的 gradient 累加可能涉及不同内核行为，不能把 CPU 测试的逐位复现承诺外推到全部设备。

## 简单测试怎么写

保存实现与以下测试为 `solution.py`，用含 PyTorch 和 NumPy 的 Python 运行 `python3 solution.py`。先核对手算 matrix，再检查非对称、多圈补边、零补边及 gradient 重复计数。

```python
x = torch.tensor([[[[1.0, 2.0], [3.0, 4.0]]]], requires_grad=True)
y = circular_pad2d(x, (1, 1, 1, 1))
expected = torch.tensor(
    [
        [
            [
                [4.0, 3.0, 4.0, 3.0],
                [2.0, 1.0, 2.0, 1.0],
                [4.0, 3.0, 4.0, 3.0],
                [2.0, 1.0, 2.0, 1.0],
            ]
        ]
    ]
)
assert torch.equal(y, expected)
y.sum().backward()
assert torch.equal(x.grad, torch.full_like(x, 4.0))
assert torch.equal(x.detach(), torch.tensor([[[[1.0, 2.0], [3.0, 4.0]]]]))
assert torch.equal(circular_pad2d(x, (0, 0, 0, 0)), x)
wide = circular_pad2d(torch.tensor([[[[1.0, 2.0]]]]), (3, 0, 0, 0))
assert wide.tolist() == [[[[2.0, 1.0, 2.0, 1.0, 2.0]]]]
asymmetric = circular_pad2d(x.detach().double(), (0, 1, 1, 0))
assert asymmetric.tolist() == [[[[3.0, 4.0, 3.0], [1.0, 2.0, 1.0], [3.0, 4.0, 3.0]]]]
assert asymmetric.dtype == torch.float64
assert asymmetric.shape == (1, 1, 3, 3)
# 多batch、多channel，两个方向都超过原始尺寸；独立对照NumPy wrap。
import numpy as np

multi = torch.arange(36, dtype=torch.float64).reshape(2, 3, 2, 3)
original = multi.clone()
large = circular_pad2d(multi, (4, 2, 3, 1))
reference = np.pad(multi.numpy(), ((0, 0), (0, 0), (3, 1), (4, 2)), mode="wrap")
assert large.shape == (2, 3, 6, 9)
assert np.array_equal(large.numpy(), reference)
assert torch.equal(multi, original)
# 在库函数支持的范围内再对照一次。
import torch.nn.functional as F

assert torch.equal(
    circular_pad2d(multi, (1, 2, 1, 1)), F.pad(multi, (1, 2, 1, 1), mode="circular")
)
```

## 面试追问

**circular、reflect、replicate 有何不同？** circular 从另一侧绕回；reflect 在 image edges 反射；replicate 重复最近的 image-edge values。它们给模型不同的 boundary conditions，不能只看输出尺寸是否一致。

**为什么图片可能不适合环形补边？** 普通图片左右边缘通常并不相邻，绕回可能引入虚假连续关系；周期信号或全景图则可能有合理用途，要按数据与任务决定。

**如何进一步验证？** 对库函数支持的合法尺寸与补边范围，可以与其 circular 模式对照；对本题允许的多圈补边按模索引独立手算，不假设库的约束完全相同。
