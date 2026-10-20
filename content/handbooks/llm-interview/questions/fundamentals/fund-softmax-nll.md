---
id: fund-softmax-nll
section: fundamentals
order: 3
level: S
title: 从 logits 到 Softmax 再到交叉熵，梯度为什么是 $\hat{p}-y$？
quick: "$\\ell=-z_y+\\log\\sum_j e^{z_j}$，对 $z_k$ 求导得 $p_k-\\mathbf{1}[k=y]$：正确类是 $p_y-1$，其余类是 $p_k$，合起来就是 $\\nabla_z\\ell=\\hat{p}-y$。"
tags:
  - Math
  - Cross Entropy
  - Softmax
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Softmax function
    url: https://en.wikipedia.org/wiki/Softmax_function
    type: primary
  - title: PyTorch CrossEntropyLoss
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html
    type: reference
---

LLM 的 next-token 损失就是这件事。记 logits $z\in\mathbb{R}^V$，

$$
p_i=\frac{e^{z_i}}{\sum_{j=1}^V e^{z_j}},\qquad \ell(z,y)=-\log p_y=-z_y+\log\sum_j e^{z_j}.
$$

第二式是数值上该写的形式：`log_softmax` + NLL，不要先 `softmax` 再 `log`（容易下溢到 $0$ 再取 $\log$）。

## 逐步求导

先看 $\log\sum_j e^{z_j}$ 对 $z_k$ 的导数：

$$
\frac{\partial}{\partial z_k}\log\sum_j e^{z_j}=\frac{e^{z_k}}{\sum_j e^{z_j}}=p_k.
$$

于是

$$
\frac{\partial\ell}{\partial z_k}=-\mathbf{1}[k=y]+p_k.
$$

向量写法：标签的 one-hot 为 $y$，模型分布为 $\hat{p}$，

$$
\nabla_z\ell=\hat{p}-y.
$$

含义：正确类梯度 $p_y-1\le 0$（往上推 logit）；错误类梯度 $p_k\ge 0$（往下压）。模型越自信且答对，$\hat{p}\approx y$，梯度接近 $0$。

## 和熵 / KL 对上

若标签是软分布 $p$（label smoothing 或蒸馏教师），损失是交叉熵 $H(p,\hat{p})=-\sum_i p_i\log\hat{p}_i$，梯度变成 $\hat{p}-p$。当 $p$ 是 one-hot，退回上式。又因为 $H(p,\hat{p})=H(p)+D_{\mathrm{KL}}(p\|\hat{p})$，对 $\hat{p}$ 优化等价于正向 KL。

## 容易栽的点

- Temperature：$p_i\propto e^{z_i/T}$，等于把 logits 除以 $T$。$T\to 0$ 趋近 argmax；$T\to\infty$ 趋近均匀。这只改采样或蒸馏软标签，不自动等于训练时的 entropy bonus。
- 词表 $V=10^5$、随机初始化时 $p_y\approx 1/V$，$\ell\approx\log V\approx 11.5$ nat。见「10 万词表交叉熵起步」。
- `ignore_index`（pad）不进平均，否则起步损失会被 pad 稀释。
