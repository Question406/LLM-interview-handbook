---
id: openai-entropy-l1
section: openai
order: 3
level: A
title: OpenAI ML Coding：用 linear + softmax 算 entropy；换成 L1 怎么做？
quick: >-
  分类分布 $p=\mathrm{softmax}(Wx)$，熵 $H(p)=-\sum_i p_i\log p_i$，要用 log-sum-exp 稳住。L1
  不能再走 softmax：把线性输出收成单纯形上的 $\ell_1$ 几何（ReLU 后归一，或投影到单纯形），距离用
  $\|p-q\|_1$，不再把 CE 当默认损失。
tags:
  - OpenAI
  - Entropy
  - Softmax
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OpenAI ML Coding 面经
    url: https://www.1point3acres.com/bbs/thread-1177444-1-1.html
    type: candidate-first-hand
---

## 真题记录

- 公司：OpenAI（Research org）
- 岗位：候选人写的是 Research 侧 ML Coding，两轮
- 来源：一亩三分地 2026-05 帖，细节对游客隐藏；可见部分明确写了「Entropy 计算」和 follow-up「如果换成 L1 distance，怎么用 neural network 实现」
- 实现：回复里说 numpy，不是必须 PyTorch

公开可见的题面就这两句。下面按信息论和单纯形几何把能公开讲的部分写完，不编造帖子里被藏掉的数据构造。

## Entropy：先得到合法分布，再算 $H$

输入 $x\in\mathbb{R}^d$，线性层 $z=Wx+b$，

$$
p_i=\frac{e^{z_i-\max_j z_j}}{\sum_k e^{z_k-\max_j z_j}},\qquad
H(p)=-\sum_i p_i\log p_i.
$$

减 max 是必须的，直接 `exp(z)` 会 overflow。$p_i=0$ 的项用 $p\log p\to 0$ 的约定，实现里对 $p_i<\varepsilon$ 的项跳过或用 `p*log(p+eps)` 并在注释里承认这是近似。

熵的单位随 log 底：$\log_2$ 是 bit，$\ln$ 是 nat。面试里说一次。均匀分布 $H=\log n$ 最大；one-hot 的熵为 0。用这个做单元测试。

不要把 entropy 写成 CE。CE 是 $H(p,q)=-\sum p\log q$；当 $p$ 是经验 one-hot 时 CE 变成 NLL，和分布自身的 $H(p)$ 不是同一个量。

## L1：换的是单纯形上的几何，不是换一个激活名字

Softmax 把 $\mathbb{R}^n$ 映到单纯形内部，对应的是指数族 / $\ell_2$ 在 log 域的几何，和 CE、KL 一套。L1 距离 $\|p-q\|_1$ 活在单纯形上，但 **softmax 不再是对的归一化**。

可实现的网络：

1. **非负再 $\ell_1$ 归一：** $y=\mathrm{ReLU}(Wx)$，$p=y/\|y\|_1$。这是常见的「线性 + 正部 + L1 归一」，对应稀疏、可出现精确 0 的分布。全 0 要有 fallback（均匀或加 $\varepsilon$）。
2. **欧氏投影到单纯形：** $p=\Pi_{\Delta}(Wx)$，可用 Duchi 的 $O(n\log n)$ 投影。比 ReLU 归一更接近「L1 球 ∩ 概率单纯形」。
3. **损失：** 目标若是贴近分布 $q$，用 $\frac12\|p-q\|_1$ 或 TV；不要再接 CE。对 one-hot 目标，$\|p-e_y\|_1=2(1-p_y)$，等于在优化正确类概率，但梯度和 softmax+CE 不同，零概率处不可微，需要 subgradient。

Sparsemax 是把欧氏投影到单纯形写成可微层，面试提到它能说明你知道「softmax 不是唯一的单纯形映射」，但题目说的是 L1，优先讲 $\ell_1$ 归一和 TV，不要把名字偏到 sparsemax 当标准答案。

数值：L1 归一在 $y\approx 0$ 时不稳定；投影法要处理全分量相同的退化。测试写：输出和为 1、非负、对均匀输入熵接近 $\log n$。

## 追问

- **为什么 softmax 不能直接配 L1？** softmax 永不碰边界，$H(p)>0$；L1 / TV 常希望稀疏。几何和损失要匹配。
- **和 MAE 回归呢？** MAE 是点估计的 $\ell_1$，不是单纯形上的分布距离。题目若给的是 class 概率，不要答成回归。
- **numpy 怎么写 softmax？** `z -= z.max(axis=-1, keepdims=True)`，再 `exp`、求和。不要对整个 batch 减同一个标量。
