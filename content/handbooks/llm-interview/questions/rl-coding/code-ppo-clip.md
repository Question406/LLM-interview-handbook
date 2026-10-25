---
id: code-ppo-clip
section: rl-coding
order: 4
level: A
title: 手写 PPO clipped surrogate，并解释 $A$ 的符号
quick: "$L=\\min(\\rho A,\\mathrm{clip}(\\rho,1-\\varepsilon,1+\\varepsilon)A)$。Clip 不会把真实的 $\\rho$ 拉回区间，只是让越界且「有利」那一侧的梯度变成 0：$A\\gt 0$ 时上限 $1+\\varepsilon$ 生效，$A\\lt 0$ 时下限 $1-\\varepsilon$ 生效。"
tags:
  - PPO
  - Clip
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Proximal Policy Optimization
    url: https://arxiv.org/abs/1707.06347
    type: primary
---

## 题目描述

实现 `ppo_clip_loss(logp,old_logp,adv,eps=0.2)`，返回用于最小化的 PPO clipped policy loss。

`logp`、`old_logp` 和 `adv` 是同形有限浮点 PyTorch 张量，可以是一维样本向量或二维 token 矩阵；本练习所有元素均有效，不使用 padding mask。旧策略 logprob 和优势作为已固定的输入；`0 < eps < 1`。

逐元素定义概率比 `rho=exp(logp-old_logp)`，目标为 `min(rho*adv,clamp(rho,1-eps,1+eps)*adv)`。返回此目标对全部元素算术平均后的负值，结果是可对 logp 反向传播的标量张量。输入差值保证指数在所用类型中有限。本题没有 value loss、熵正则、KL 项或优势标准化。

### 示例

```text
输入：logp=[log(1.5)]，old_logp=[0]，adv=[1]，eps=0.2
输出：-1.2

输入：logp=[log(0.5)]，old_logp=[0]，adv=[-1]，eps=0.2
输出：0.8

将上面两条合成一个长度2的batch
输出：-0.2
```

## 解题思路与参考答案

PPO 的 clipped surrogate 是 $\min(\rho A,\mathrm{clip}(\rho)A)$，clip 管哪一侧要看 $A$ 的符号：$A\gt 0$ 时管上限，$A\lt 0$ 时管下限，而且它只让越界那部分样本梯度为 0，$\rho$ 本身并没有被夹住。现场最容易写错的就是这两件事：把 `clip` 当成对 $\rho$ 的硬约束，以及不看 $A$ 的符号就说「ratio 被夹在 $[1-\varepsilon,1+\varepsilon]$」。

## 公式

$$
\rho=\exp(\log\pi_\theta-\log\pi_{\mathrm{old}}),\qquad
L(\theta)=\min\big(\rho A,\;\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)\,A\big).
$$

目标是最大化 $L$，实现里常写成 `-L.mean()`。$A\gt 0$ 时我们想增大 $\rho$，可一旦超过 $1+\varepsilon$，$\min$ 就选中了常数项，这个样本的梯度变成 0。$A\lt 0$ 时想减小 $\rho$，低于 $1-\varepsilon$ 之后同样被掐掉。另一侧不 clip，也就是 $A\gt 0$ 但 $\rho$ 很小，或者 $A\lt 0$ 但 $\rho$ 很大的情况，这样策略能从「走错的方向」被拉回来。

举个数：$\varepsilon=0.2$，某个 token 的 $A=1$，$\rho$ 已经到了 1.5。$\min(1.5,1.2)=1.2$ 是常数，这个 token 本轮不再推着 $\rho$ 往上走。同一个 token 如果 $A=-1$，$\min(-1.5,-1.2)=-1.5$，梯度还在，会把 $\rho$ 往回压。

CISPO 不一样，它 clip 的是 IS 权重并且 detach，梯度仍然走 $\log\pi$，见 `pt-cispo`、`pt-ppo-clip`。

```python
import torch

def ppo_clip_loss(logp, old_logp, adv, eps=0.2):
    rho = (logp - old_logp).exp()
    unclipped = rho * adv
    clipped = torch.clamp(rho, 1 - eps, 1 + eps) * adv
    # maximize min(...)  <=>  minimize negative
    return -torch.minimum(unclipped, clipped).mean()
```

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

正优势搭配 ratio=1.5，应被截到 1.2；负优势搭配 ratio=0.5，应按 0.8 计算。这两条可以发现把 min/max 或负号写反的问题。

```python
old = torch.zeros(1)
positive = ppo_clip_loss(torch.tensor([1.5]).log(), old, torch.tensor([1.]))
negative = ppo_clip_loss(torch.tensor([0.5]).log(), old, torch.tensor([-1.]))
torch.testing.assert_close(positive, torch.tensor(-1.2))
torch.testing.assert_close(negative, torch.tensor(0.8))
print("simple tests passed")
```

## 追问

**$\rho$ 真的被夹住了吗？**
没有。网络照样可以把 $\rho$ 推到 10，只是这些 token 本轮不提供更新。

**要不要对 $A$ 做标准化？**
组内或 batch 标准化会改变哪些样本被 clip，这和 GRPO 的组相对优势是同一类设计。

**和 value clip 是什么关系？**
PPO 还有一项 value function clip，那是另一回事，这题只写 policy surrogate。

相关：`code-ppo-grpo-gspo`（GAE、组优势和 GSPO 的序列比怎么接上这段 clip，以及 TRL / verl 的配置名）
