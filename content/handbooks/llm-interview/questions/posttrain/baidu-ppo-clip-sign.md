---
id: baidu-ppo-clip-sign
section: posttrain
order: 203
level: S
title: 百度文心 RL 后训练：PPO clip 在优势为正/负时分别限制哪一侧？
quick: "$A>0$ 时限制概率比不要过大（上界），避免一步把好动作推得太猛；$A<0$ 时限制概率比不要过小（下界），避免把坏动作打压过头。两边都靠 $\\mathrm{clip}(\\rho,1-\\varepsilon,1+\\varepsilon)$ 加 $\\min$ 选出保守的一侧；朝安全方向走时 clip 不激活，梯度照常保留。"
tags:
  - Baidu
  - PPO
  - Clip
  - "2026"
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百度 大模型后训练 一面（候选人原帖）
    url: https://www.nowcoder.com/discuss/863890669662674944
    type: candidate-first-hand
---

## 真题记录

- 公司：百度 · 文心一言
- 岗位：大模型 强化学习（RL） 后训练
- 面试时间：2026-03-18
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“PPO的clip在优势A 正/负时 限制上/下届，A为正限制上届，A为负限制下届”**

$A$ 为正时限制上界，$A$ 为负时限制下界。这个口诀是对的，关键是要能在白板上把 $\rho$ 增大、减小代进去，说明 $\min(\rho A,\mathrm{clip}(\rho)A)$ 为什么总是选出保守的那一侧。

$$
L=\mathbb{E}\big[\min\big(\rho_t A_t,\;\mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)\,A_t\big)\big],\quad
\rho_t=\frac{\pi_\theta}{\pi_{\mathrm{old}}}.
$$

先看 $A_t\gt 0$，这时希望增大这个动作的概率。没 clip 的 $\rho A$ 随 $\rho$ 增大而增大，$\min$ 取两者里较小的，所以 $\rho\gt 1+\varepsilon$ 之后目标就锁在 $(1+\varepsilon)A$，这就是限制上界，一步不能把有正优势的 token 推得太猛。再看 $A_t\lt 0$，这时希望减小概率。$\rho$ 变得很小（$\rho\lt 1-\varepsilon$）时，$\rho A$ 负得更少，数值变大；$\min$ 同样选更小、更保守的那一侧，锁在 $(1-\varepsilon)A$，这就是限制下界，防止把坏 token 打压过头。口诀成立，是因为 $A$ 的符号把「有利方向」翻到了 $\rho$ 的同一侧。面试时我会现场挑两个数代进去演一遍。

反过来，离开有利方向时 clip 不激活，梯度还在。这是 PPO 故意留的口子：朝安全方向可以多走，好动作的概率被压低、坏动作的概率被抬高时，它不拦。

失败模式在被扔掉的 token 上。$\rho$ 越出 $[1-\varepsilon,1+\varepsilon]$ 且处在有利方向时，这一项对 $\theta$ 的梯度是 0，这个 token 本轮就被扔掉了。长思维链（CoT）、异步 reuse 时，低概率但关键的推理 token 更容易被 clip 掉，熵和探索会塌。DAPO 的 clip-higher 放宽了正向上界，给稀有的好 token 留出上升空间；CISPO 改成截断 IS 权重并 detach，梯度始终走 $\log\pi$，见 `pt-cispo`。所以要盯 clip fraction：长期接近 0，说明 $\varepsilon$ 太松或者步子太小；长期很高，说明 policy stale 或者学习率过大。

clip 是信任域的工程近似，要和 KL、clip fraction、策略熵一起看，单靠它当护栏不够。反向 KL 是另一根锚，管的是相对 $\pi_{\mathrm{ref}}$ 的累积偏离，见 `fund-kl-directions`，和一步的 $\rho$ 不是一回事。GRPO 复用同一套 surrogate，只是把 $A$ 换成组相对优势，见 `sys-rl-group-n`；CISPO 改的是 clip 的对象，和这道符号题无关。

## 追问

**为什么用 $\min$，不用 $\max$？**
目标是最大化期望优势，取更悲观的一侧才构成信任域。写成 $\max$，有利方向上就放开了，clip 失效。

**$A=0$ 呢？**
整项为 0，和 GRPO 整组同奖励是同一个病：没有方向，clip 设计得再精致也没用。

**和 KL 重复吗？**
不重复。clip 管相对 $\pi_{\mathrm{old}}$ 的一步 $\rho$，KL 管相对冻结 $\pi_{\mathrm{ref}}$ 的累积偏离。两根锚，采样都在 $\pi$ 上。

**手写一下？**
`min(ratio * A, ratio.clamp(1-eps, 1+eps) * A)`，乘上 response mask，再按你声明的 reduction 平均。

**负优势那边也要 clip-higher 吗？**
不用。clip-higher 放的是正向的 $\varepsilon_{\mathrm{high}}$，负侧仍用较紧的下界，两边不对称是有意的。
