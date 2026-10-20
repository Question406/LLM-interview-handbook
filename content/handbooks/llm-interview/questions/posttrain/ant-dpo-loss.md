---
id: ant-dpo-loss
section: posttrain
order: 141
level: A
title: 蚂蚁：DPO 的 loss 怎么写？
quick: "把 KL 约束最优策略反解出的奖励代入 Bradley-Terry，得到 $-\\log\\sigma(\\beta[\\Delta_w-\\Delta_l])$，其中 $\\Delta=\\log\\pi_\\theta(y\\mid x)-\\log\\pi_{\\mathrm{ref}}(y\\mid x)$。"
tags:
  - Ant Group
  - DPO
  - Preference
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 蚂蚁大模型面经
    url: https://www.nowcoder.com/feed/main/detail/2b27dfe1f1ab4efa87eb0aea70ffdc20
    type: candidate-first-hand
  - title: DPO
    url: https://arxiv.org/abs/2305.18290
    type: primary-paper
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“讲一下 DPO , PPO , GRPO 的原理和区别，写一下 DPO loss 函数”**

常见误区是：「再做一次 pairwise 交叉熵」，或者把 $\beta$ 说成学习率。DPO 从反向 KL 约束下强化学习目标的闭式最优策略反解奖励，再代入 Bradley-Terry，不是凭空发明的分类损失。方向写反，最优策略对不上，后续推导也会出错，见 `fund-kl-directions`。我会主动写出三样：冻结的 $\pi_{\mathrm{ref}}$、完成序列上的 $\log\pi$ 求和，以及优化的是 chosen 相对 rejected 的间隔，不是正例绝对似然。这些条件都需要在推导中说明。

## 从最优策略反解到分类损失

带 KL 约束的对齐目标写成

$$
\max_\pi\ \mathbb{E}_{y\sim\pi}[r(x,y)]-\beta\,D_{\mathrm{KL}}\big(\pi(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)\big).
$$

期望在当前策略上取，所以是反向、mode-seeking：可以丢掉参考里不想要的峰，但不能靠进入 $\pi_{\mathrm{ref}}\approx 0$ 的区域利用奖励漏洞。闭式最优解是

$$
\pi^*(y\mid x)\propto\pi_{\mathrm{ref}}(y\mid x)\exp\big(r(x,y)/\beta\big),
$$

反解奖励 $r(x,y)=\beta\log\frac{\pi^*(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}+Z(x)$。$Z(x)$ 只依赖输入提示，Bradley-Terry 做差时相消，于是奖励差变成策略对数比的差，得到只含 $\pi_\theta$ 与冻结 $\pi_{\mathrm{ref}}$ 的分类损失：

$$
\mathcal{L}_{\mathrm{DPO}}=-\mathbb{E}\log\sigma\Big(\beta\big(\log\tfrac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\log\tfrac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\big)\Big).
$$

现场顺序必须是：先写约束目标 $\to$ 再写 $\pi^*$ $\to$ 再反解 $r$ $\to$ 最后写 $\sigma$。跳过反解，最常见的事故是把 $\beta$ 乘在 $\sigma$ 外面，或者漏掉 ref 只写 $\log\pi(y_w)-\log\pi(y_l)$。那就退化成没有锚的偏好交叉熵损失（CE），最优策略不再对应原来的 RL 目标。

## 白板符号与失败模式

$y_w/y_l$ 是 chosen / rejected；$\log\pi$ 对回答序列的 token求和，prompt 要 mask 掉；$\pi_{\mathrm{ref}}$ 全程冻结，通常使用监督微调（SFT）后的权重。$\beta$ 大则更贴 ref、间隔难拉开；$\beta$ 小则偏好信号强，但策略容易漂出参考支撑。梯度推的是 **margin**，不是 SFT 那种「正例似然单调上升」：chosen 与 rejected 的绝对 $\log\pi$ 可以双降，只要相对间隔在涨、下游胜率在涨，这仍可能是健康曲线，见 `baidu-dpo-chosen-curve`。

失败模式我会主动报。长 chosen 天然占总 logprob 优势，模型学会啰嗦但偏好赢，需要长度归一、SimPO 或标注时控长。DPO 不在线采样，也没有显式奖励模型，因此偏好标签出错后，无法通过新采样自动纠正。离线数据与线上用户需求不同，即使训练中的偏好间隔变大，实际表现仍可能下降。过拟合噪声 pair 会出现 offline 赢、online 崩。这些都不是「再加学习率」能修的。和 PPO / GRPO 我会差一句：DPO 离线吃 pair；PPO 使用奖励模型、价值评估模型（critic）和裁剪目标；GRPO 用组相对优势，组大小必须 $n\gt 1$，见 `sys-rl-group-n`。

## 追问

- **和 PPO / GRPO 差一句？** DPO 无 online rollout 与显式 RM，直接拉策略比；PPO 用奖励加 GAE 再 clip；GRPO 用同题组内相对奖励当 baseline，省 critic，但 $n=1$ 优势未定义。
- **$\beta$ 是学习率吗？** 不是。它是原 RL 目标里的 KL 系数，控制偏离 ref 的温度。学习率管步长，$\beta$ 管目标本身。
- **ref 用当前 $\pi$ 行吗？** 不行。ref 一动，反解出来的 $r$ 零点跟着漂，间隔失去锚，等于每步换奖励函数。
- **长度怎么办？** 平均 logp、SimPO、显式长度惩罚或标注说明「短而对优于长而对」。只加 $\beta$ 治不好长度 bias，因为 $\beta$ 不区分 token 数。
- **正例概率一定升吗？** 不一定。优化的是 $\Delta$，不是 $\log\pi(y_w)$。双降但 margin 升是常见现象，要同时看 KL 与 holdout 胜率。
