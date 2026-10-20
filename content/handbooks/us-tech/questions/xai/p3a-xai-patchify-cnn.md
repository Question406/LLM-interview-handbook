---
id: p3a-xai-patchify-cnn
section: xai
order: 750
level: S
title: "xAI：图像 Patchify 与 CNN 输入轴转置"
quick: "原帖作者在评论里补充的第二轮：先 reshape 拆出 patch 网格轴，再 transpose 把通道移到 patch 内高宽之前、送入 CNN；具体形状由练习约定。"
companies:
  - xai
tags:
  - xAI
  - Coding
  - Frontier-2026-10
  - 完整编程练习
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: 1Point3Acres xAI source
    url: https://www.1point3acres.com/interview/thread/1171574
    type: candidate-first-hand
---

## 题目

把一批图像切成固定大小的图块（patch），并把通道轴移到高宽之前，整理成 CNN 能直接吃的输入格式，再送进一个卷积层。考的是多维数组的 reshape 和 transpose 能不能写对。

> 来源：一亩三分地 xAI 原帖（thread 1171574），原帖作者在评论里补充了第二轮的内容：把图像拆成图块，通道移到高宽之前，再送入 CNN。原帖没有给出具体形状和接口，下面的函数签名、形状约定、实现和测试都是手册补的练习约定，不作为已确认的面试事实。

## 思路

关键是分两步走：先用 reshape 把轴「拆开」，再用 transpose 把轴「换位」，最后 reshape 合并。

以 NHWC 输入 `[B, H, W, C]` 为例：

1. reshape 成 `[B, H/ph, ph, W/pw, pw, C]`。这一步只是把 H 拆成「第几行 patch」和「patch 内第几行」，元素在内存里的顺序不变。
2. transpose 成 `[B, H/ph, W/pw, C, ph, pw]`：patch 网格的两个轴放前面，通道放到 patch 内的高宽之前。
3. reshape 成 `[P, C, ph, pw]`，P 是所有 patch 的个数。

常见的错误是跳过第 2 步直接 reshape，形状对了但内容是乱的。所以验证时不能只看 shape，要检查第一个 patch 的具体数值，并确认逆变换能还原原图。

动手前和面试官确认：输入是 NHWC 还是 NCHW；H、W 不整除 patch 尺寸时是报错、补零还是裁剪；patch 的排列顺序（先行后列）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `patchify(images, ph, pw)`：输入 NumPy 数组 `[B, H, W, C]`，输出 `[B * (H/ph) * (W/pw), C, ph, pw]`。patch 顺序是 batch、patch 行、patch 列。
- `unpatchify(patches, B, H, W, C)`：`patchify` 的逆变换。
- `conv1x1(patches, weight, bias)`：`weight` 形状 `[O, C]`，`bias` 形状 `[O]`，输出 `[P, O, ph, pw]`。
- H、W 不能被 patch 尺寸整除或者形状对不上时抛 `ValueError`，不插值也不补零。各维尺寸不超过 128，只用 NumPy，不依赖 PyTorch。

### 输入输出示例

```text
images = np.arange(16).reshape(1, 4, 4, 1)
patchify(images, 2, 2).shape     -> (4, 1, 2, 2)
patchify(images, 2, 2)[0, 0]     -> [[0, 1], [4, 5]]    # 左上角
patchify(images, 2, 2)[1, 0]     -> [[2, 3], [6, 7]]    # 同一行右边那块
```

### 解题思路与正确性

reshape 只是重新解释轴的划分，不改变每个元素在行优先顺序中的位置，所以拆轴之后 `grid[b, i, r, j, s, c]` 正好是原图 `images[b, i*ph + r, j*pw + s, c]`。transpose 只交换轴，把 `(i, j)` 放在前面、`c` 放到 `(r, s)` 之前，最后合并 `(b, i, j)` 就是先 batch、再行、再列的 patch 序号。`unpatchify` 按相反的轴顺序做同样三步。

1x1 卷积在每个像素位置上对通道做一次线性变换，用 `einsum` 写成 `out[p, o, h, w] = Σ_c patches[p, c, h, w] · weight[o, c] + bias[o]`。它用来检查「通道在第 1 维」这个 CNN 输入约定，又不会引入 padding 和步长的歧义。

### 完整参考实现（Python 3）

```python
import numpy as np


def patchify(images, ph, pw):
    """[B, H, W, C] -> [B * (H/ph) * (W/pw), C, ph, pw]，patch 顺序为 batch、patch 行、patch 列。"""
    images = np.asarray(images)
    if images.ndim != 4 or ph <= 0 or pw <= 0:
        raise ValueError("images must be [B, H, W, C] and patch size positive")
    B, H, W, C = images.shape
    if H % ph or W % pw:
        raise ValueError(f"image {H}x{W} is not divisible by patch {ph}x{pw}")
    grid = images.reshape(B, H // ph, ph, W // pw, pw, C)  # 拆出 patch 网格轴和 patch 内轴
    grid = grid.transpose(0, 1, 3, 5, 2, 4)                # [B, 行, 列, C, ph, pw]
    return grid.reshape(-1, C, ph, pw)


def unpatchify(patches, B, H, W, C):
    """patchify 的逆变换：[P, C, ph, pw] -> [B, H, W, C]。"""
    patches = np.asarray(patches)
    if patches.ndim != 4:
        raise ValueError("patches must be [P, C, ph, pw]")
    ph, pw = patches.shape[-2:]
    if H % ph or W % pw:
        raise ValueError(f"image {H}x{W} is not divisible by patch {ph}x{pw}")
    expected = (B * (H // ph) * (W // pw), C, ph, pw)
    if patches.shape != expected:
        raise ValueError(f"expected patches of shape {expected}, got {patches.shape}")
    grid = patches.reshape(B, H // ph, W // pw, C, ph, pw)
    grid = grid.transpose(0, 1, 4, 2, 5, 3)  # [B, 行, ph, 列, pw, C]
    return grid.reshape(B, H, W, C)


def conv1x1(patches, weight, bias):
    """在每个 patch 上做 1x1 卷积：patches [P, C, ph, pw]，weight [O, C]，bias [O] -> [P, O, ph, pw]。"""
    patches = np.asarray(patches)
    weight = np.asarray(weight)
    bias = np.asarray(bias)
    if patches.ndim != 4 or weight.ndim != 2 or weight.shape[1] != patches.shape[1]:
        raise ValueError("weight must be [O, C] matching the patch channels")
    if bias.shape != (weight.shape[0],):
        raise ValueError("bias must be [O]")
    return np.einsum("pchw,oc->pohw", patches, weight) + bias[None, :, None, None]
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")

# 单张 4x4 单通道图，2x2 patch：首个 patch 是左上角
image = np.arange(16).reshape(1, 4, 4, 1)
patches = patchify(image, 2, 2)
assert patches.shape == (4, 1, 2, 2)
assert patches[0, 0].tolist() == [[0, 1], [4, 5]]
assert patches[1, 0].tolist() == [[2, 3], [6, 7]]  # 第二个是同一行右边那块
assert np.array_equal(unpatchify(patches, 1, 4, 4, 1), image)

# 1x1 卷积：输出通道 0 = 2 * 输入 + 1
out = conv1x1(patches, np.array([[2], [3]]), np.array([1, 0]))
assert out.shape == (4, 2, 2, 2)
assert np.array_equal(out[:, 0], patches[:, 0] * 2 + 1)
assert np.array_equal(out[:, 1], patches[:, 0] * 3)

# 多 batch、多通道、非正方形 patch、非连续输入都能往返
images = np.arange(2 * 4 * 6 * 3).reshape(2, 4, 6, 3)[:, ::-1]
assert np.array_equal(unpatchify(patchify(images, 2, 3), 2, 4, 6, 3), images)

# 不整除和形状不符
expect_value_error(patchify, image, 3, 2)
expect_value_error(unpatchify, patches, 2, 4, 4, 1)
expect_value_error(conv1x1, patches, np.ones((2, 3)), np.zeros(2))
```

### 复杂度与追问

设图像元素总数为 N = BHWC。`patchify` 和 `unpatchify` 是 O(N) 时间和空间：transpose 本身只返回 view，但随后的 reshape 遇到非连续内存会复制一份。`conv1x1` 是 O(P · ph · pw · C · O)。

- 输入是 NCHW 怎么办？拆轴和 transpose 的轴号相应调整即可，思路不变。原帖没有披露维度约定，这里的 NHWC 是练习假设。
- 在 PyTorch 里通常怎么写？可以用 `unfold`，或者直接用 kernel 和 stride 都等于 patch 尺寸的 `Conv2d`，ViT 的 patch embedding 就是这样实现的。
- 不整除时：要么提前 padding 到整数倍，要么裁掉边缘，选哪种要和面试官确认。
