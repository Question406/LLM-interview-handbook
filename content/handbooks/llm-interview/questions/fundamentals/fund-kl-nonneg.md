---
id: fund-kl-nonneg
section: fundamentals
order: 2
level: S
title: KL 散度为什么一定非负？等号何时成立？
quick: >-
  因为 $-\log$ 是凸函数，对 $D_{\mathrm{KL}}(p\|q)=\sum_x p(x)\log\frac{p(x)}{q(x)}$ 用 Jensen 就得到 Gibbs 不等式 $D_{\mathrm{KL}}(p\|q)\ge 0$，等号当且仅当 $p=q$（在 $p$ 的支撑上）。所以它能当损失，但不能当对称距离。
tags:
  - Math
  - KL
  - Probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Kullback–Leibler divergence
    url: https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence
    type: primary
  - title: Jensen's inequality
    url: https://en.wikipedia.org/wiki/Jensen's_inequality
    type: reference
---
KL 非负来自一步 Jensen 不等式：$-\log$ 是凸函数，把 KL 写成 $p$ 下对 $-\log(q/p)$ 的期望，期望的函数值不超过函数值的期望，而 $q/p$ 在 $p$ 下的期望正好是 1，$-\log 1=0$。等号当且仅当 $p=q$。先写定义（离散情形，$p(x)\gt 0$ 的地方必须 $q(x)\gt 0$，否则 KL 为 $+\infty$）：

$$
D_{\mathrm{KL}}(p\|q)=\sum_x p(x)\log\frac{p(x)}{q(x)}=\mathbb{E}_{x\sim p}\big[\log p(x)-\log q(x)\big].
$$

## 推导（Gibbs / Jensen）

把对数底固定为 $e$，令 $f(t)=-\log t$，$f$ 是凸的。于是

$$
D_{\mathrm{KL}}(p\|q)=\sum_x p(x)\,f\!\left(\frac{q(x)}{p(x)}\right)\ge f\!\left(\sum_x p(x)\cdot\frac{q(x)}{p(x)}\right)=f\!\left(\sum_x q(x)\right)=f(1)=0.
$$

中间那步就是 Jensen：$\mathbb{E}[f(Z)]\ge f(\mathbb{E}[Z])$，这里 $Z=q/p$，在 $p$ 下取期望。$\sum q=1$ 用到了 $q$ 是一个分布。

等号条件来自严格凸，Jensen 取等当且仅当 $Z$ 几乎处处是常数，也就是 $q/p$ 在 $p$ 的支撑上为常数，再加上归一化，只能是 $q=p$。

## 马上能用的推论

KL 不是距离，因为 $D_{\mathrm{KL}}(p\|q)\neq D_{\mathrm{KL}}(q\|p)$，三角不等式也不成立，要对称就换 JS，或者把两个方向都写上。

它能当损失，因为它非负，且 $p=q$ 时为 $0$，最小化它就是在拟合。

支撑也很关键。$p$ 有质量而 $q=0$ 的点会让 $\log(p/q)\to+\infty$，这就是 forward KL 对「漏掉 $p$ 的某个 mode」零容忍的根源。比如数据里有少量样本是某种少见写法，模型给它的概率压到 0，正向 KL 直接变成无穷大。

它和交叉熵的关系是 $D_{\mathrm{KL}}(p\|q)=H(p,q)-H(p)$，$H(p)$ 与 $q$ 无关，所以「最小 CE」和「最小正向 KL」是同一场优化。

面试里我会按这个顺序讲：定义 → $-\log$ 凸 → Jensen → $\sum q=1$ → 等号条件 → 顺带一句不对称。光背「KL 大于等于 0」不够。
