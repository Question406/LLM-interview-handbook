---
id: pdd-ppo-clip-then-min
section: posttrain
order: 127
level: S
title: 拼多多：PPO clip 之后为什么仍然需要 min？
quick: >-
  clip 只是另造了一条把 importance sampling 比截断的目标，min
  在未截断和截断两条目标里取更悲观的一条，才挡住「看起来能涨、其实越界」的更新。没有 min，优势为正时优化器仍会沿未 clip 的项无约束放大比率，PPO
  的保守更新就不成立。
tags:
  - PDD
  - PPO
  - Clip
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 拼多多 - 大模型算法 秋招一面
    url: 'https://www.nowcoder.com/discuss/906953010406772736'
    type: candidate-first-hand
  - title: PPO
    url: 'https://arxiv.org/abs/1707.06347'
    type: primary-paper
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：搜广推部门大模型算法岗
- 届别 / 流程：秋招；一面
- 面试时间：2026-07-15
- 来源类型与可信度：牛客候选人原帖，A（公司、部门、岗位、日期与轮次明确）
- 原始措辞：**“PPO 优化算法中为什么 clip 之后仍然需要 min 操作？”**

因为 clip 只构造了另一条被截断的目标，min 才在两条目标里选更悲观的那条，PPO 的保守更新靠的是这一步。没有 min，优化器仍然可以沿着未截断的 $r\hat A$ 走，clip 就成了摆设。这是 maximize 形式下的 pessimistic bound，min 也算不上多写的一层函数。答「clip 已经把 ratio 夹住了，min 只是实现细节」会被追问。白板上我会先写 $L^{\mathrm{CLIP}}$，再按 $\hat A$ 的正负两边分别画哪一条更小，这样比背「PPO 要 clip」更容易说清更新什么时候停。

先看公式。记 importance sampling 比 $r_t(\theta)=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{\mathrm{old}}}(a_t\mid s_t)}$，PPO 的代理目标是

$$
L^{\mathrm{CLIP}}=\mathbb{E}\big[\min\big(r_t\hat A_t,\ \mathrm{clip}(r_t,1-\epsilon,1+\epsilon)\hat A_t\big)\big].
$$

clip 把 $r_t$ 限在 $[1-\epsilon,1+\epsilon]$，防止一步把策略拉得太远。可它自己决定不了「这条样本该不该继续加概率」，那要看 $\hat A$ 的符号，以及未截断项和截断项哪个更保守。外层在 maximize $L$，对两条 surrogate 取 min，就等于只承认更差的那条的增长。这和「先把 $r$ 夹住再乘 $A$」是两回事：后者在负优势下会把符号弄反，现场最容易写错。

背后的直觉是 trust-region：一步更新之后，新策略相对旧策略的重要性权重不能变化太大。clip 给出越界时的替代目标，min 保证优化器不会为了更高的未截断目标把这条替代忽略掉。两步合起来，才是保守的代理目标。

然后分正负优势看 min 在做什么。$\hat A\gt 0$ 时我们想提高这个动作的概率。如果 $r$ 已经 $\gt 1+\epsilon$，截断项 $=(1+\epsilon)\hat A$ 更小，min 选它，于是继续增大这个动作的概率不再有奖励，高优势样本没法靠无限增大 $\rho$ 来抬高目标值。$r$ 还在区间内时，两条相同或者未截断那条更小，正常走未截断的梯度。

$\hat A\lt 0$ 时我们想压低这个动作。如果 $r$ 已经 $\lt 1-\epsilon$，未截断的 $r\hat A$ 因为 $r$ 更小、$\hat A$ 为负，会变得更大，也就是没那么负。要是取这一条，优化器会把比率推得更极端来「完成」惩罚，更新就跑出了信任域。min 会选更负的截断项，把惩罚钉在 $(1-\epsilon)\hat A$ 上。所以实现时必须先算出两条已经乘过 $A$ 的 surrogate 再取 min，先 clip 比率再乘 $A$ 是错的。

反过来想，如果只 clip 比率、却去最大化未截断的 $r\hat A$，优势为正且 $r$ 很大时，梯度仍然按大比率走，信任域被绕开了。clip 只出现在另一条没被选中的分支上，日志里还能看到「做过 clip」，loss 却已经不是 PPO 的裁剪目标。min 给出的是 surrogate 的 lower bound：maximize 的是两条里较差的那条，保证「看起来能涨」的更新不会跑出 clip 带。value clip 和对 $\pi_{\mathrm{ref}}$ 的 KL 是另一层约束，管的是价值估计和长期漂移，替代不了 min。

## 追问

**为什么是 min 不是 max？**
因为外层在 maximize $L$，对目标取 min 等于取 pessimistic bound。取 max 会选更乐观的一侧，clip 就失效了，高优势样本会继续增大 $\rho$。

**和 GRPO 的 clip 一样吗？**
同构，都是 $\min(\rho A,\mathrm{clip}(\rho)A)$。没有价值评估模型（critic）不等于可以去掉 min；组内优势很大时，缺了 min 一样一步毁掉格式。

**把 $\epsilon$ 调大能不能代替 min？**
不能。$\epsilon$ 只管带宽，min 管选哪条目标。带宽再宽，没有 min 仍然可能走未截断项。

**负优势的实现有什么坑？**
先 clip 比率再乘 $A$，负号会让「更极端」变成「看起来更好」。按论文写成两条 surrogate 再取 min，并在单元测试里放一条 $\hat A\lt 0,\,r\lt 1-\epsilon$ 的例子。实现里还要把 value clip、KL 惩罚一起看，别把 PPO 说成「只是把 ratio 夹一下」。
