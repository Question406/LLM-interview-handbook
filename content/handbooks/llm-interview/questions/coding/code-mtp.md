---
id: code-mtp
section: coding
order: 59
level: A
title: 手写 Multi-Token Prediction：第 $k$ 个头预测 $t+1+k$，loss 怎么 shift
quick: >-
  第 $k$ 个头在位置 $t$ 预测 $x_{t+1+k}$，target 取 `idx[:, 1+k:]`，有效长度随 $k$ 变短，各头的 CE
  取平均。$k=0$ 就是普通的 next-token loss。
tags:
  - MTP
  - DeepSeek
  - Loss
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28T00:00:00.000Z
sources:
  - title: DeepSeek-V3 Technical Report
    url: 'https://arxiv.org/abs/2412.19437'
    type: primary
---

## 题目描述

实现多 token 预测（MTP）的训练损失：第0个预测头预测下一 token，第1个头预测再后一个 token，以此类推。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `mtp_loss(logits_list,idx,ignore_index=-100)`。idx 为[B,T]整数 token 序列；第 k 个 logits 为[B,Lk,V]，对应目标 idx[:,1+k:1+k+Lk]；1≤Lk≤T-k-1。各有效标签均在 vocabulary 范围，忽略标签可为`ignore_index`。

### 输出与约束

对每个头分别计算非忽略位置的平均 cross entropy，再对各头等权平均，返回标量。列表非空且每头至少一个非忽略目标；不同头可以有不同时间长度。无需实现完整 Transformer 或 MTP 网络。

### 示例

```text
idx=[[0,1,0]]，两个头logits分别为[1,2,2]和[1,1,2]的全零张量
每个目标概率都是1/2，mtp_loss -> ln(2)≈0.693147。
```

## 解题思路与参考答案

MTP 的 loss 就是给每个头单独错开标签：第 $k$ 个头在位置 $t$ 预测 $x_{t+1+k}$，target 取 `idx[:, 1+k:]`，头越靠后预测得越远，有效长度也越短，最后把各头的 CE 平均。普通语言模型算损失时用 `logits[:, :-1]` 对 `idx[:, 1:]`（见 `code-decoder-block`），$k=0$ 的头就是这一项。

常见的错有两种。一种是三个头都去预测 `idx[:, 1:]`，同一个目标学了三遍，根本没有「多 token」。另一种是第 $k$ 个头还用长度 $T$ 的 logits，尾部那几个位置没有对应的 target。

对序列 $x_0,x_1,\ldots,x_{T-1}$ 来说：

- $k=0$：位置 $t$ 预测 $x_{t+1}$，有效长度 $T-1$
- $k=1$：位置 $t$ 预测 $x_{t+2}$，有效长度 $T-2$
- $k=D$：位置 $t$ 预测 $x_{t+1+D}$

$$
\mathcal{L}=\frac1{D+1}\sum_{k=0}^{D}\mathrm{CE}\big(\mathrm{logits}^{(k)},\,x_{1+k:}\big).
$$

白板上可以先写 $D$ 个独立的线性头，接在同一份 $h$ 上。DeepSeek-V3 的真实结构是顺序模块：第 $k$ 个 MTP block 接收上一个模块的输出和真实 token $x_{t+k}$ 的 embedding，经过 RMSNorm 和一层 Transformer，最后共享 `lm_head`。先把 target 对齐写对，再补结构。

```python
import torch.nn.functional as F


def mtp_loss(logits_list, idx, ignore_index=-100):
    # logits_list[k]: [B, T-k, V]，预测 idx[:, 1+k :]
    losses = []
    for k, logits in enumerate(logits_list):
        tgt = idx[:, 1 + k : 1 + k + logits.size(1)]
        losses.append(
            F.cross_entropy(
                logits.reshape(-1, logits.size(-1)),
                tgt.reshape(-1),
                ignore_index=ignore_index,
            )
        )
    return sum(losses) / len(losses)
```

推理时主模型还是逐 token 生成（decode），MTP 头可以给 speculative decoding 当草稿模型，接受规则见 `code-spec-decode`。辅助头的梯度要不要缩放，论文里有个 $\lambda$，白板上写平均就行。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

两类 logits 全零时，无论预测第几个未来 token，平均 cross entropy 都是 log(2)。再让两个 head 对各自正确偏移的目标给高分，确认不是只测了形状。

```python
import math
import torch

idx = torch.tensor([[0, 1, 0]])
logits = [torch.zeros(1, 2, 2), torch.zeros(1, 1, 2)]
torch.testing.assert_close(mtp_loss(logits, idx), torch.tensor(math.log(2)))
logits = [torch.tensor([[[0.0, 10.0], [10.0, 0.0]]]), torch.tensor([[[10.0, 0.0]]])]
assert mtp_loss(logits, idx).item() < 0.001
print("simple tests passed")
```

## 追问

**和 Medusa 有什么区别？**
Medusa 在同一个 hidden 上挂几个平行的头，推理时走树状投机。MTP 论文走的是顺序模块，训练信号沿时间多看几步。

**padding 怎么处理？**
每个头都要屏蔽自己 target 里的 padding。序列很短、$T\le D+1$ 时，较深的头可能一个有效 token 都没有，这一项损失就跳过。

**显存吃得消吗？**
$D$ 个 `[B,T,V]` 不能全物化。辅助头用 `code-fused-ce`，或者停掉梯度、只训模块自身。
