---
id: pdd-ppo-clip-then-min
section: posttrain
order: 127
level: S
title: 拼多多：PPO clip 之后为什么仍然需要 min？
quick: >-
  clip 只截断过大的重要性采样比，min 在未截断目标与截断目标之间取更悲观的一个，避免「看起来能涨但其实越界」的更新。没有
  min，优势为正时可能无约束放大未 clip 项，PPO 的保守更新不成立。
tags:
  - PDD
  - PPO
  - Clip
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 拼多多 - 大模型算法 秋招一面
    url: https://www.nowcoder.com/discuss/906953010406772736
    type: candidate-first-hand
  - title: PPO
    url: https://arxiv.org/abs/1707.06347
    type: primary-paper
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：搜广推部门大模型算法岗
- 届别 / 流程：秋招；一面
- 面试时间：2026-07-15
- 来源类型与可信度：牛客候选人原帖，A（公司、部门、岗位、日期与轮次明确）
- 原始措辞：**“PPO优化算法中为什么clip之后仍然需要min操作？”**

常见错答是「clip 已经把 ratio 夹住了，min 只是实现细节」。clip 只构造了另一条被截断的目标，**min 才在两条目标里选更悲观的一条**，PPO 的保守更新才成立。没有 min，优化器仍可能沿着未截断的 $r\hat A$ 走，clip 变成装饰。这是 maximize 形式下的 pessimistic bound，不是多写一层函数。白板先写 $L^{\mathrm{CLIP}}$，再分 $\hat A$ 正负两边画哪一条更小，比背「PPO 要 clip」更不容易被追问打穿。实现里对负优势还要小心符号，并和 value clip、KL 惩罚一起看，不要把 PPO 说成「只是把 ratio 夹一下」。

## 公式：clip 截的是比率，不是目标

记重要性采样比 $r_t(\theta)=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{\mathrm{old}}}(a_t\mid s_t)}$。PPO 的代理目标是

$$
L^{\mathrm{CLIP}}=\mathbb{E}\big[\min\big(r_t\hat A_t,\ \mathrm{clip}(r_t,1-\epsilon,1+\epsilon)\hat A_t\big)\big].
$$

clip 把 $r_t$ 限制在 $[1-\epsilon,1+\epsilon]$，防止单步把策略拉得太远。它单独并不决定「这条样本该不该继续加概率」——那取决于 $\hat A$ 的符号，以及未截断项和截断项谁更保守。外层在 maximize $L$，所以对两条 surrogate 取 min，等于只承认更差的那条增长。这和「先把 $r$ 夹住再乘 $A$」不是同一回事：后者在负优势下会把符号搞反，现场最容易写错。

Trust-region 的直觉是：一步更新后，新策略相对旧策略的重要性权重不能飞。clip 给出越界时的替代目标；min 保证我们不会为了更高的未截断目标而忽略这条替代。两条都在，保守才闭合。

## min：正负优势两侧都取悲观

$\hat A\gt 0$ 时，想提高该动作概率。若 $r$ 已经 $\gt 1+\epsilon$，截断项 $=(1+\epsilon)\hat A$ 更小，min 选它，于是不再奖励继续增大该动作概率——高优势样本不能靠把 $\rho$ 拉飞来无限加分。$r$ 还在区间内时，两条一样或未截断更小，正常走未截断梯度。

$\hat A\lt 0$ 时，想压低该动作。若 $r$ 已经 $\lt 1-\epsilon$，未截断的 $r\hat A$ 因为 $r$ 更小、$\hat A$ 为负而变得更大（不那么负）。若取这条，优化器会通过把比率推得更极端来「做对」惩罚，信任域被反向撕开。min 会选更负的截断项，把惩罚钉在 $(1-\epsilon)\hat A$ 上。实现时必须先形成两条已乘过 $A$ 的 surrogate 再 min，而不是先 clip 比率再乘 $A$。

## 没有 min，保守更新不成立

如果只 clip 比率、却最大化未截断的 $r\hat A$，优势为正且 $r$ 很大时，梯度仍按大比率走，信任域被绕开。clip 只出现在另一条没被选中的分支上，日志里你还能看到「做过 clip」，loss 却不是 PPO。面试补一句：这是 surrogate 的 lower bound——我们 maximize 的是两条里较差的那条，保证「看起来能涨」的更新不会越出 clip 带。value clip、对 $\pi_{\mathrm{ref}}$ 的 KL 是另一层约束，管的是价值估计和长期漂移，不能代替 min。GRPO 的 clipped surrogate 与此同构：没有 critic 不等于可以去掉 min。

## 追问

- **为什么是 min 不是 max？** 因为外层在 maximize $L$。对目标取 min 等于取 pessimistic bound；若取 max 会选更乐观的一侧，clip 失效，高优势样本会继续拉飞 $\rho$。
- **和 GRPO 的 clip 一样吗？** 同构：都是 $\min(\rho A,\mathrm{clip}(\rho)A)$。没有 critic 不等于可以去掉 min。组内优势很大时，缺 min 一样一步毁掉格式。
- **$\epsilon$ 调大能否代替 min？** 不能。$\epsilon$ 只管带宽，min 管选哪一条目标。带宽再宽，没有 min 仍可能走未截断项。
- **负优势实现踩坑？** 先 clip 比率再乘 $A$，负号会让「更极端」变成「看起来更好」。按论文写成两条 surrogate 再 min，并在单元测试里放一条 $\hat A\lt 0,\,r\lt 1-\epsilon$ 的例子。
