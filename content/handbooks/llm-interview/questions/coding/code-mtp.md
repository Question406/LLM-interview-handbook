---
id: code-mtp
section: coding
order: 59
level: A
title: 手写 Multi-Token Prediction：第 $k$ 个头预测 $t+1+k$，loss 怎么 shift
quick: "第 $k$ 个头在位置 $t$ 预测 $x_{t+1+k}$，target 取 `idx[:, 1+k:]`，有效长度随 $k$ 变短，各头的 CE 取平均。$k=0$ 就是普通 next-token loss。"
tags:
  - MTP
  - DeepSeek
  - Loss
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
---

普通语言模型计算损失时，用 `logits[:, :-1]` 对 `idx[:, 1:]`，见 `code-decoder-block`。MTP 对每个预测头分别错开标签，越后面的头预测的位置越远。常见误区是：三个头都去预测 `idx[:, 1:]`，等于同一目标学三遍，没有「多 token」；或 $k$ 头仍用长度 $T$ 的 logits，尾部没有对应 target。

## shift

序列 $x_0,x_1,\ldots,x_{T-1}$：

- $k=0$：位置 $t$ 预测 $x_{t+1}$，有效长度 $T-1$
- $k=1$：位置 $t$ 预测 $x_{t+2}$，有效长度 $T-2$
- $k=D$：位置 $t$ 预测 $x_{t+1+D}$

$$
\mathcal{L}=\frac1{D+1}\sum_{k=0}^{D}\mathrm{CE}\big(\mathrm{logits}^{(k)},\,x_{1+k:}\big).
$$

白板可以先写 $D$ 个独立线性头接在同一份 $h$ 上。DeepSeek-V3 的真结构是顺序模块：第 $k$ 个 MTP block 接收上一模块输出和真实 token $x_{t+k}$ 的 embedding，再经 RMSNorm / 一层 Transformer，最后共享 `lm_head`。先把 target 对齐写对，再补结构。

```python
import torch.nn.functional as F

def mtp_loss(logits_list, idx, ignore_index=-100):
    # logits_list[k]: [B, T-k, V]，预测 idx[:, 1+k :]
    losses = []
    for k, logits in enumerate(logits_list):
        tgt = idx[:, 1 + k:1 + k + logits.size(1)]
        losses.append(F.cross_entropy(
            logits.reshape(-1, logits.size(-1)),
            tgt.reshape(-1),
            ignore_index=ignore_index,
        ))
    return sum(losses) / len(losses)
```

推理时，主模型仍然逐 token 生成（decode）。MTP 头可以给投机解码当草稿模型，接受规则见 `code-spec-decode`。训练时辅助头的梯度要不要缩放，论文里有 $\lambda$，白板写平均即可。

## 追问

- **和 Medusa？** Medusa 是在同一 hidden 上挂平行头，推理走树状投机。MTP 论文路线是顺序模块，训练信号沿时间多看几步。
- **padding？** 每个头都要屏蔽自己 target 中的 padding。短序列 $T\le D+1$ 时，较深的头可能没有有效 token，这种损失项应跳过。
- **显存？** $D$ 个 `[B,T,V]` 不能都物化，辅助头用 `code-fused-ce` 或停梯度只训模块自身。
