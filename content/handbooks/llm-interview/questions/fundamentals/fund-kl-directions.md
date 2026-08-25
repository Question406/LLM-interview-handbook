---
id: fund-kl-directions
section: fundamentals
order: 2
level: S
title: Forward KL vs Reverse KL：Mode-Covering / Mode-Seeking 是什么意思？
quick: >-
  正向 $D_{\mathrm{KL}}(p\|q)$ 的期望在 $p$ 上取：$p\gt 0$ 而 $q\approx 0$ 会炸，所以 $q$ 必须覆盖 $p$ 的所有峰（mode-covering）。反向
  $D_{\mathrm{KL}}(q\|p)$ 的期望在 $q$ 上取：可以丢掉 $p$ 的某些峰，但不敢把质量放到 $p\approx 0$ 处（mode-seeking）。
tags:
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
  - title: On-Policy Distillation from Reasoning Models for Real-Time Applications
    url: https://thinkingmachines.ai/blog/on-policy-distillation/
    type: secondary
---

两个方向只差「谁来采样」：

$$
\begin{aligned}
D_{\mathrm{KL}}(p\|q)&=\mathbb{E}_{x\sim p}\Big[\log\frac{p(x)}{q(x)}\Big],\\
D_{\mathrm{KL}}(q\|p)&=\mathbb{E}_{x\sim q}\Big[\log\frac{q(x)}{p(x)}\Big].
\end{aligned}
$$

习惯称前者为正向（数据 / 教师是 $p$，模型是 $q$），后者为反向。

## 为什么一个 covering、一个 seeking

看惩罚在哪爆炸。

- **正向。** 积分 / 求和跟着 $p$ 走。只要 $p(x)\gt 0$，哪怕只是一个小峰，若 $q(x)\approx 0$，则 $\log(p/q)\to+\infty$。模型不敢漏掉 $p$ 的任何 mode，宁可把质量摊开、变「糊」。这叫 mode-covering。SFT / 标准 KD 属于这类。
- **反向。** 积分跟着 $q$ 走。$p$ 有、但 $q$ 根本不去的那些峰，**根本不进期望**。模型可以锁住一个主峰。但若 $q$ 跑到 $p\approx 0$ 的地方，$\log(q/p)$ 一样炸。这叫 mode-seeking。RLHF 对 $\pi_{\mathrm{ref}}$ 的惩罚、OPD（学生自己采样）属于这类。

我会记一句：看 token 从谁采样，不是看公式里谁写在左边。

## 三格数值（建议白板算一遍）

支撑 $\{a,b,c\}$，$p=(0.49,0.49,0.02)$ 两个主峰加一点尾巴。

| $q$ | 含义 | 正向 KL | 反向 KL |
| --- | --- | --- | --- |
| $(0.49,0.49,0.02)$ | 完美拟合 | $0$ | $0$ |
| $(0.98,0.01,0.01)$ | 只锁 $a$ | 大（漏了 $b$，$p(b)/q(b)$ 很大） | 较小（期望几乎只在 $a$ 上） |
| $(1/3,1/3,1/3)$ | 摊均匀 | 中等（覆盖了，但浪费质量） | 较大（在 $c$ 上 $p$ 很小） |

不必背具体数字，要能指出：**正向会因为漏峰而爆，反向会因为漏峰而「假装没看见」。**

## 接到后训练

- SFT / 普通蒸馏：数据或教师采样 → 正向。
- PPO drift、GRPO 的 KL 惩罚、OPD：当前策略采样 → 反向。
- 这是常用直觉，不是对任意参数化的机械定理。支撑、有限样本、温度都会改形状。

追问「PPO 的 KL 改成 CE」：CE 展开是正向 KL 加 $H(p)$，采样分布也反了。见蚂蚁真题卡。
