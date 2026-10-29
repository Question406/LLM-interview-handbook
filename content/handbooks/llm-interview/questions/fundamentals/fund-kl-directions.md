---
id: fund-kl-directions
section: fundamentals
order: 2
level: S
title: Forward KL vs Reverse KL：Mode-Covering / Mode-Seeking 是什么意思？
quick: >-
  区别在谁来 sampling。forward KL 在 $p$ 上取期望，漏掉 $p$ 的任何峰都重罚，所以 $q$
  会铺开覆盖（mode-covering）；reverse KL 在 $q$ 上取期望，没采到的峰不计入，$q$
  倾向锁住一个峰（mode-seeking）。SFT / 普通 distillation 是正向，PPO 的 KL 惩罚和 OPD 是反向。
tags:
  - KL
  - Probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Kullback–Leibler divergence
    url: 'https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence'
    type: primary
  - title: On-Policy Distillation from Reasoning Models for Real-Time Applications
    url: 'https://thinkingmachines.ai/blog/on-policy-distillation/'
    type: secondary
---
两个方向只差「期望在谁身上取」：forward KL 跟着 $p$ 走，漏掉 $p$ 的峰会被重罚，模型只好铺开去覆盖所有峰；reverse KL 跟着 $q$ 走，$q$ 不去的峰根本不进期望，模型可以只锁住一个主峰。我会记一句：看 token 从哪个分布 sampling，别看公式里谁写在左边。

$$
\begin{aligned}
D_{\mathrm{KL}}(p\|q)&=\mathbb{E}_{x\sim p}\Big[\log\frac{p(x)}{q(x)}\Big],\\
D_{\mathrm{KL}}(q\|p)&=\mathbb{E}_{x\sim q}\Big[\log\frac{q(x)}{p(x)}\Big].
\end{aligned}
$$

习惯上把前者叫正向（数据 / 教师是 $p$，模型是 $q$），后者叫反向。

## 为什么一个 covering、一个 seeking

看哪些情况会被重罚就明白了。forward KL 的求和跟着 $p$ 走，只要 $p(x)\gt 0$，哪怕只是一个小峰，$q(x)\approx 0$ 时 $\log(p/q)\to+\infty$。模型不敢漏掉 $p$ 的任何 mode，宁可把概率铺得更宽，这就是 mode-covering，SFT 和标准 KD 属于这类。

reverse KL 的求和跟着 $q$ 走，$p$ 有、$q$ 根本不去的那些峰不进期望，模型可以锁住一个主峰；但 $q$ 要是跑到 $p\approx 0$ 的地方，$\log(q/p)$ 同样会变得很大。这就是 mode-seeking，RLHF 对 $\pi_{\mathrm{ref}}$ 的惩罚、OPD（学生自己 sampling）属于这类。

## 三格数值，建议白板算一遍

支撑是 $\{a,b,c\}$，$p=(0.49,0.49,0.02)$，两个主峰加一点尾巴。

| $q$ | 含义 | forward KL | reverse KL |
| --- | --- | --- | --- |
| $(0.49,0.49,0.02)$ | 完美拟合 | $0$ | $0$ |
| $(0.98,0.01,0.01)$ | 只锁 $a$ | 大（漏了 $b$，$p(b)/q(b)$ 很大） | 较小（期望几乎只在 $a$ 上） |
| $(1/3,1/3,1/3)$ | 摊均匀 | 中等（覆盖了，但浪费质量） | 较大（在 $c$ 上 $p$ 很小） |

具体数字不用背，要能指出：正向会狠罚漏掉的峰，反向对 $q$ 没采到的峰不计入期望。

## 接到后训练

SFT 和普通 distillation 是数据或教师 sampling，属于正向。PPO 的 drift、GRPO 的 KL 惩罚、OPD 都是当前策略 sampling，属于反向。这是常用的直觉，不能当成对任意参数化都机械成立的定理，支撑、有限样本、温度都会改变分布的形状。

被追问「PPO 的 KL 能不能改成 CE」时：cross entropy loss（CE）展开是 forward KL 加 $H(p)$，sampling 分布也反了，所以不能直接换，见蚂蚁真题卡。
