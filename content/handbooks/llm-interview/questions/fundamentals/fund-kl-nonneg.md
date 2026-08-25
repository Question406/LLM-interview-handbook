---
id: fund-kl-nonneg
section: fundamentals
order: 2
level: S
title: KL 散度为什么一定非负？等号何时成立？
quick: >-
  $D_{\mathrm{KL}}(p\|q)=\sum_x p(x)\log\frac{p(x)}{q(x)}$。$-\log$ 凸，Jensen 给出 Gibbs
  不等式：$D_{\mathrm{KL}}(p\|q)\ge 0$，等号当且仅当 $p=q$（在 $p$ 的支撑上）。所以它能当损失，但不能当对称距离。
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

定义（离散，且 $p(x)\gt 0$ 的地方必须 $q(x)\gt 0$，否则 KL 为 $+\infty$）：

$$
D_{\mathrm{KL}}(p\|q)=\sum_x p(x)\log\frac{p(x)}{q(x)}=\mathbb{E}_{x\sim p}\big[\log p(x)-\log q(x)\big].
$$

## 推导（Gibbs / Jensen）

把对数底固定为 $e$，令 $f(t)=-\log t$，则 $f$ 凸。于是

$$
D_{\mathrm{KL}}(p\|q)=\sum_x p(x)\,f\!\left(\frac{q(x)}{p(x)}\right)\ge f\!\left(\sum_x p(x)\cdot\frac{q(x)}{p(x)}\right)=f\!\left(\sum_x q(x)\right)=f(1)=0.
$$

中间那步就是 Jensen：$\mathbb{E}[f(Z)]\ge f(\mathbb{E}[Z])$，这里 $Z=q/p$、$Z$ 在 $p$ 下取期望。$\sum q=1$ 用了 $q$ 是分布。

等号：严格凸函数的 Jensen 等号当且仅当 $Z$ 几乎处处常数，即 $q/p$ 在 $p$ 的支撑上为常数；再归一化，只能是 $q=p$。

## 立刻能用的推论

1. **不是距离。** $D_{\mathrm{KL}}(p\|q)\neq D_{\mathrm{KL}}(q\|p)$，三角不等式也不成立。要对称就改 JS 或把两个方向都写上。
2. **能当损失。** 非负且 $p=q$ 时为 $0$，最小化它就是在拟合。
3. **支撑。** $p$ 有质量、$q=0$ 的点会让 $\log(p/q)\to+\infty$。这就是 forward KL 对「漏掉 $p$ 的某个 mode」零容忍的根源。
4. **和交叉熵。** $D_{\mathrm{KL}}(p\|q)=H(p,q)-H(p)$。$H(p)$ 与 $q$ 无关，所以「最小 CE」和「最小正向 KL」是同一场优化。

白板我会按这个顺序：定义 → $-\log$ 凸 → Jensen → $\sum q=1$ → 等号条件 → 提一句不对称。不要只背「KL 大于等于 0」。
