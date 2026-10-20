---
id: fund-ce-kl
section: fundamentals
order: 1
level: S
title: Cross Entropy、MLE、KL 的关系？
quick: "$H(p,q)=-\\mathbb{E}_{x\\sim p}[\\log q(x)]=H(p)+D_{\\mathrm{KL}}(p\\|q)$。数据分布 $p$ 固定时，最小交叉熵、最大似然、最小正向 KL 是同一件事。监督微调（SFT） 就是在有限样本上做这件事。"
tags:
  - Math
  - MLE
  - KL
  - Cross Entropy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Cross-entropy
    url: https://en.wikipedia.org/wiki/Cross-entropy
    type: primary
  - title: Relationship to maximum likelihood
    url: https://en.wikipedia.org/wiki/Cross-entropy#Relationship_to_maximum_likelihood_estimation
    type: reference
---

我会先把三个定义写齐。$p$ 是「目标 / 数据」，$q$ 是「模型」：

$$
\begin{aligned}
H(p)&=-\sum_x p(x)\log p(x),\\
H(p,q)&=-\sum_x p(x)\log q(x),\\
D_{\mathrm{KL}}(p\|q)&=\sum_x p(x)\log\frac{p(x)}{q(x)}.
\end{aligned}
$$

## 恒等式（必须能手推）

把 KL 拆开：

$$
\begin{aligned}
D_{\mathrm{KL}}(p\|q)
&=\sum_x p(x)\log p(x)-\sum_x p(x)\log q(x)\\
&=-H(p)+H(p,q).
\end{aligned}
$$

于是

$$
H(p,q)=H(p)+D_{\mathrm{KL}}(p\|q).
$$

$H(p)$ 不含 $q$。对模型做梯度时 $\nabla_q H(p,q)=\nabla_q D_{\mathrm{KL}}(p\|q)$。所以最小化交叉熵损失（CE） 就是最小正向 KL。KL 非负还立刻给出 $H(p,q)\ge H(p)$，等号当 $q=p$。

最大熵也是这条：均匀 $u(x)=1/V$，则 $H(p)=\log V-D_{\mathrm{KL}}(p\|u)\le\log V$。

## 接到 MLE

i.i.d. 样本 $x_1,\ldots,x_n\sim p_{\mathrm{data}}$，模型 $q_\theta$。对数似然

$$
\frac1n\sum_{i=1}^n\log q_\theta(x_i)\approx \mathbb{E}_{x\sim p_{\mathrm{data}}}[\log q_\theta(x)]=-H(p_{\mathrm{data}},q_\theta).
$$

所以最大似然 = 最小经验交叉熵 = 最小经验正向 KL。LLM 的 next-token 损失（loss）就是把 $p$ 换成 one-hot 标签（或教师软标签）后的这个目标。

有限数据、teacher forcing（用真实历史 token 作为条件）和 mask 会让「SFT = 完美 mode-covering」只是直觉，不是定理；但方向仍是正向：$p$ 采样（数据），$q$ 被拟合。

## 不要和反向 KL 混

PPO / 基于人类反馈的强化学习（RLHF）的策略偏移约束项是 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，期望在当前策略上取，那是反向。交叉熵 $H(\pi_{\mathrm{ref}},\pi_\theta)$ 展开后是正向 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$ 加一项常数。蚂蚁会问「PPO 的 KL 能不能改成 CE」：不能直接换，换了就改方向。推导见那张真题卡。
