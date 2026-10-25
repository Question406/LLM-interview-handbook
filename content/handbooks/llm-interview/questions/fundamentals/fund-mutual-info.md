---
id: fund-mutual-info
section: fundamentals
order: 3
level: A
title: 条件熵和互信息怎么从熵推出来？和 KL 是什么关系？
quick: >-
  拆联合分布 $p(x,y)=p(x)p(y\mid x)$ 就得到 $H(X,Y)=H(X)+H(Y\mid X)$；互信息 $I(X;Y)=H(X)-H(X\mid Y)=D_{\mathrm{KL}}(p(x,y)\,\|\,p(x)p(y))$，是联合分布相对「独立乘积」多付的码长。独立时为 $0$，一方确定另一方时等于 $H(X)$。
tags:
  - Math
  - Entropy
  - Mutual Information
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Mutual information
    url: https://en.wikipedia.org/wiki/Mutual_information
    type: primary
  - title: Conditional entropy
    url: https://en.wikipedia.org/wiki/Conditional_entropy
    type: reference
---
两者都从联合熵拆出来：把 $p(x,y)$ 拆成 $p(x)p(y\mid x)$，联合熵就变成 $H(X)$ 加条件熵；互信息是知道 $Y$ 以后 $X$ 少掉的不确定性，写开来正好是联合分布对「假装独立的乘积分布」的 KL。比如 $X$ 是天气、$Y$ 是有没有人带伞：两者完全无关时 $I=0$；带不带伞就能完全确定下没下雨时，$I$ 等于天气本身的熵。

联合熵把 $(X,Y)$ 当成一个随机变量：

$$
H(X,Y)=-\sum_{x,y}p(x,y)\log p(x,y).
$$

拆开 $p(x,y)=p(x)p(y\mid x)$：

$$
\begin{aligned}
H(X,Y)
&=-\sum_{x,y}p(x,y)\big(\log p(x)+\log p(y\mid x)\big)\\
&=-\sum_x p(x)\log p(x)-\sum_x p(x)\sum_y p(y\mid x)\log p(y\mid x)\\
&=H(X)+H(Y\mid X).
\end{aligned}
$$

第二项就是条件熵：先对每个 $x$ 算 $Y\mid X=x$ 的熵，再按 $p(x)$ 平均。对称地也有 $H(X,Y)=H(Y)+H(X\mid Y)$。

## 互信息

知道 $Y$ 之后，$X$ 还剩多少不确定性：

$$
I(X;Y)=H(X)-H(X\mid Y)=H(Y)-H(Y\mid X)=H(X)+H(Y)-H(X,Y).
$$

再写成 KL，这步最好能手推：

$$
\begin{aligned}
I(X;Y)
&=\sum_{x,y}p(x,y)\log\frac{p(x,y)}{p(x)p(y)}\\
&=D_{\mathrm{KL}}\big(p(x,y)\,\|\,p(x)p(y)\big)\ge 0.
\end{aligned}
$$

所以 $I=0$ 当且仅当 $X\perp Y$，$I(X;X)=H(X)$，链式法则是 $I(X;Y,Z)=I(X;Y)+I(X;Z\mid Y)$。

## 接到模型

下一 token 的交叉熵是在估 $H(x_t\mid x_{\lt t})$ 的上界，模型越好，条件熵越低。

Attention 或表征里说的「token 之间的依赖」，可以粗略说成互信息，但别把点积注意力直接写成 $I(Q;K)$。

信息瓶颈、对比学习都在最大化某种 $I(\text{repr};\text{target})$，实现上仍常落到交叉熵损失（CE）或 InfoNCE，而 InfoNCE 是互信息的变分下界。

白板上我会先画 $H(X)$、$H(Y)$、$H(X,Y)$ 三个圈，交叠的部分就是 $I$，再写那条 KL。
