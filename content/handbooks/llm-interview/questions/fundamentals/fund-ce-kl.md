---
id: fund-ce-kl
section: fundamentals
order: 1
level: S
title: Cross Entropy、MLE、KL 的关系？
quick: "三者在数据分布 $p$ 固定时是同一件事：$H(p,q)=-\\mathbb{E}_{x\\sim p}[\\log q(x)]=H(p)+D_{\\mathrm{KL}}(p\\|q)$，$H(p)$ 不含模型，所以最小交叉熵、最大似然、最小正向 KL 是同一个优化。监督微调（SFT）就是在有限样本上做这件事。"
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
数据分布 $p$ 固定时，最小化交叉熵、最大似然和最小化正向 KL 是同一个优化，因为交叉熵等于 $H(p)$ 加正向 KL，而 $H(p)$ 跟模型无关。我会先把三个定义写齐，$p$ 是目标 / 数据，$q$ 是模型：

$$
\begin{aligned}
H(p)&=-\sum_x p(x)\log p(x),\\
H(p,q)&=-\sum_x p(x)\log q(x),\\
D_{\mathrm{KL}}(p\|q)&=\sum_x p(x)\log\frac{p(x)}{q(x)}.
\end{aligned}
$$

## 恒等式要能手推

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

$H(p)$ 不含 $q$，对模型求梯度时 $\nabla_q H(p,q)=\nabla_q D_{\mathrm{KL}}(p\|q)$，所以最小化交叉熵损失（CE）就是在最小化正向 KL。再用 KL 非负，马上得到 $H(p,q)\ge H(p)$，$q=p$ 时取等号。

最大熵也是从这条来的：取均匀分布 $u(x)=1/V$，就有 $H(p)=\log V-D_{\mathrm{KL}}(p\|u)\le\log V$。

## 接到 MLE

拿 i.i.d. 样本 $x_1,\ldots,x_n\sim p_{\mathrm{data}}$ 训练模型 $q_\theta$，平均对数似然是

$$
\frac1n\sum_{i=1}^n\log q_\theta(x_i)\approx \mathbb{E}_{x\sim p_{\mathrm{data}}}[\log q_\theta(x)]=-H(p_{\mathrm{data}},q_\theta).
$$

所以最大似然、最小经验交叉熵、最小经验正向 KL 是一回事。LLM 的 next-token 损失（loss）就是把 $p$ 换成 one-hot 标签（或者教师的软标签）之后的这个目标。比如句子「今天天气很」的下一个词标签是「好」，one-hot 的 $p$ 只在「好」上有质量，交叉熵就只剩 $-\log q(\text{好})$。

有限数据、teacher forcing（用真实历史 token 作条件）和 mask 会让「SFT = 完美 mode-covering」只停留在直觉，算不上定理；但方向仍然是正向的：从 $p$ 采样（数据），去拟合 $q$。

## 别和反向 KL 混

PPO / 基于人类反馈的强化学习（RLHF）里的策略偏移约束是 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$，期望在当前策略上取，是反向的。交叉熵 $H(\pi_{\mathrm{ref}},\pi_\theta)$ 展开后是正向的 $D_{\mathrm{KL}}(\pi_{\mathrm{ref}}\|\pi_\theta)$ 再加一项常数。所以蚂蚁问「PPO 的 KL 能不能改成 CE」，答案是不能直接换，一换方向就变了，推导见那张真题卡。
