---
id: fund-kl-k1-k2-k3
section: fundamentals
order: 144
level: S
title: Schulman 的 $k_1/k_2/k_3$ 各估什么？数值无偏和梯度正确是一回事吗？
quick: "$r=p/q$ 时，$k_1=-\\log r$ 无偏但方差大，$k_2=\\frac12(\\log r)^2$ 有偏，$k_3=r-1-\\log r$ 无偏且非负。数值无偏不等于梯度对：$k_3$ 直接当 loss 反传，梯度不是反向 KL 的梯度。"
tags:
  - KL
  - GRPO
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Approximating KL Divergence
    url: http://joschu.net/blog/kl-approx.html
    type: primary
  - title: 蚂蚁大模型一面（被问懵版）
    url: https://www.nowcoder.com/feed/main/detail/1a1a229b1d9f4a5bbfcb6ea6c9857339
    type: candidate-first-hand
  - title: RL 中的 KL 估计器选型
    url: https://xihuai18.github.io/reinforcement-learning/2025/12/01/kl-estimators-zh.html
    type: secondary
---

蚂蚁一面原话：「GRPO 的 KL 和 PPO 的 KL 区别？K1 K2 K3 估计区别？」先把符号明确固定下来，再把「无偏」两个字拆开。估的是反向

$$
D_{\mathrm{KL}}(q\|p)=\mathbb{E}_{x\sim q}\Big[\log\frac{q(x)}{p(x)}\Big],
$$

样本来自 $q$（当前策略 $\pi_\theta$），$p$ 是冻结参考 $\pi_{\mathrm{ref}}$，比率

$$
r=\frac{p}{q}=\frac{\pi_{\mathrm{ref}}}{\pi_\theta}.
$$

于是 $\log(q/p)=-\log r$。Schulman 的三个标量是同一条 KL 的不同估计，不是三种散度。

$$
k_1=-\log r,\qquad k_2=\tfrac12(\log r)^2,\qquad k_3=(r-1)-\log r.
$$

## 1. 三个估计分别具有什么性质

- $k_1$。$\mathbb{E}_q[k_1]=D_{\mathrm{KL}}(q\|p)$，朴素无偏。$r\gt 1$ 时为负，单次采样可以报「负 KL」，方差大，日志难看，但作为随机量期望是对的。
- $k_2$。$x\mapsto\frac12(\log x)^2$ 是 $r\approx 1$ 处 KL 的二阶近似，恒非负、平滑、方差小，期望一般不等于 KL（有偏）。适合画曲线，不适合当无偏目标。
- $k_3$：对 $k_1$ 用 $r-1$ 做控制变量：$\mathbb{E}_q[r-1]=0$，故 $\mathbb{E}_q[k_3]$ 仍是 KL。又因 $x-\ln x-1\ge 0$（$x\gt 0$），样本几乎总是非负，方差通常小于 $k_1$。因此它既保证单个样本值非负，也保持期望等于 KL。

白板可以补一句：$f(x)=x-1-\log x$ 在 $x=1$ 取 $0$，二阶导 $1/x^2$，与 KL 在 $r=1$ 的曲率一致，所以 $k_3$ 既无偏又比 $k_1$ 稳。

## 2. PPO 扣 奖励分数（reward），GRPO 挂 损失（loss）：梯度不是同一条

实现分叉，蚂蚁要的是这一层。

PPO 典型是 $k_1$ in reward：算完 $\hat{k}_1$ 后 stop-gradient，写入

$$
r_t\leftarrow r_\phi-\beta\,\mathrm{sg}(\hat{k}_1),
$$

再走 score function $\nabla\log\pi_\theta\cdot(\cdots)$。对期望回报减 $\beta\,\mathrm{KL}(q\|p)$ 求导，得到的是反向 KL 对 $\theta$ 的策略梯度（mode-seeking drift）。无偏的是奖励里的标量，梯度正确是因为没对 $r(\theta)$ 反传，只用 $\nabla\log\pi$。

GRPO 论文把 $\beta k_3$ 当成 loss 一项加在策略目标上。$k_3$ 作为标量仍无偏估计 KL，日志比 $k_1$ 稳。但 $r=\pi_{\mathrm{ref}}/\pi_\theta$ 依赖 $\theta$：若对 $k_3(\theta)$ 直接反传，链式法则多出 $\partial k_3/\partial r\cdot\partial r/\partial\theta$，这条梯度一般不是 $\nabla_\theta D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 的 score-function 形式。Off-policy 复用旧轨迹时，若再不乘 $\pi_\theta/\pi_{\mathrm{old}}$，连期望都偏。

因此说「$k_3$ 无偏所以一定对」会被追问：无偏的是标量估计，不是参数梯度。要梯度对齐反向 KL，应 stop-grad 估计量、把它当 reward shaping，或显式写出 $\mathbb{E}_q[\nabla\log\pi\,(\log q-\log p)]$ 并配 IS。要的是稳的监控数字，用 $k_3$ 或 $k_2$ 记录即可，不必反传。

## 3. 和「两种 KL」不要搅在一起

PPO clip / TRPO 管的是相对 $\pi_{\mathrm{old}}$ 的信任域；这里 $k_1/k_2/k_3$ 估的是相对 $\pi_{\mathrm{ref}}$ 的 drift。估计器选错，不会把 trust-region 变成 drift，只会影响惩罚是否无偏、是否可反传。

## 追问

- **为什么 $k_1$ 能是负的？** 单点 $-\log(\pi_{\mathrm{ref}}/\pi_\theta)$ 可负；KL 非负是对期望说的。用负样本当「KL 坏了」是误读。
- **GRPO 把 $k_3$ 当 loss 错了吗？** 作为正则启发式、为了数值稳定，工程上常见；若声称「因此我们在优化无偏反向 KL 梯度」，那是把标量性质安到了梯度上。
- **$k_2$ 能当 loss 吗？** 能当平滑惩罚，但是有偏近似，且对 $\theta$ 反传同样不是标准 KL 梯度。更常见是只用于 logging。
