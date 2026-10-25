---
id: ant-dpo-loss
section: posttrain
order: 141
level: A
title: 蚂蚁：DPO 的 loss 怎么写？
quick: "DPO 的 loss 是 $-\\log\\sigma(\\beta[\\Delta_w-\\Delta_l])$，其中 $\\Delta=\\log\\pi_\\theta(y\\mid x)-\\log\\pi_{\\mathrm{ref}}(y\\mid x)$。它来自把 KL 约束下的最优策略反解成奖励、再代入 Bradley-Terry，优化的是 chosen 相对 rejected 的间隔，$\\beta$ 是 KL 系数。"
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

DPO 的 loss 是 $-\log\sigma$ 套在 $\beta$ 乘「chosen 的对数比减 rejected 的对数比」上，对数比指当前策略相对冻结参考模型的 $\log\pi_\theta-\log\pi_{\mathrm{ref}}$。它是从带反向 KL 约束的强化学习目标推出来的：先求闭式最优策略，反解出奖励，再代入 Bradley-Terry。常见的误区是把它说成「再做一次 pairwise 交叉熵」，或者把 $\beta$ 说成学习率。

现场我会按推导的顺序写，面试官要看的就是这条链。先写带 KL 约束的对齐目标：

$$
\max_\pi\ \mathbb{E}_{y\sim\pi}[r(x,y)]-\beta\,D_{\mathrm{KL}}\big(\pi(\cdot\mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot\mid x)\big).
$$

期望在当前策略上取，所以这是反向 KL，mode-seeking：策略可以丢掉参考里不想要的峰，但不能跑进 $\pi_{\mathrm{ref}}\approx 0$ 的区域去利用奖励漏洞。方向写反，最优策略就对不上，后面的推导也跟着错，见 `fund-kl-directions`。这个目标有闭式最优解：

$$
\pi^*(y\mid x)\propto\pi_{\mathrm{ref}}(y\mid x)\exp\big(r(x,y)/\beta\big),
$$

反解得到奖励 $r(x,y)=\beta\log\frac{\pi^*(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}+Z(x)$。$Z(x)$ 只依赖输入提示，Bradley-Terry 对两个回答做差时正好消掉，奖励差就变成了策略对数比的差。于是得到一个只含 $\pi_\theta$ 和冻结 $\pi_{\mathrm{ref}}$ 的分类损失：

$$
\mathcal{L}_{\mathrm{DPO}}=-\mathbb{E}\log\sigma\Big(\beta\big(\log\tfrac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\log\tfrac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\big)\Big).
$$

所以顺序是先写约束目标 $\to$ 再写 $\pi^*$ $\to$ 再反解 $r$ $\to$ 最后写 $\sigma$。跳过反解，最常见的事故有两种：把 $\beta$ 乘在 $\sigma$ 外面，或者漏掉 ref，只写 $\log\pi(y_w)-\log\pi(y_l)$。后一种就退化成没有锚的偏好交叉熵损失（CE），最优策略不再对应原来的 RL 目标。

符号要交代清楚。$y_w/y_l$ 是 chosen / rejected；$\log\pi$ 是对回答序列的 token 求和，prompt 要 mask 掉；$\pi_{\mathrm{ref}}$ 全程冻结，通常用监督微调（SFT）后的权重。$\beta$ 大，策略更贴 ref，间隔难拉开；$\beta$ 小，偏好信号强，但策略容易漂出参考的支撑。梯度推的是 **margin**，和 SFT 那种「正例似然单调上升」不一样：chosen 和 rejected 的绝对 $\log\pi$ 可以一起降，只要相对间隔在涨、下游胜率在涨，这仍可能是健康曲线，见 `baidu-dpo-chosen-curve`。

失败模式我会主动讲。比如标注者偏爱长回答，长 chosen 天然占总 logprob 优势，模型就学会了啰嗦，偏好照样赢，这要靠长度归一、SimPO 或标注时控长来治。DPO 不在线采样，也没有显式奖励模型，偏好标签错了，没法靠新采样自己纠正。离线数据和线上用户需求不同，训练里的偏好间隔拉得再大，实际表现也可能下降；过拟合噪声 pair，会出现 offline 赢、online 崩。这些都不是「再加学习率」能修的。

## 追问

**和 PPO、GRPO 各差在哪？**
DPO 离线吃 pair，没有 online rollout，也没有显式 RM，直接拉策略比。PPO 用奖励模型和价值评估模型（critic），奖励加 GAE 算优势，再用裁剪目标更新。GRPO 用同题组内的相对奖励当 baseline，省掉 critic，但组大小必须 $n\gt 1$，$n=1$ 时优势没有定义，见 `sys-rl-group-n`。

**$\beta$ 是学习率吗？**
不是。它是原 RL 目标里的 KL 系数，控制偏离 ref 的温度。学习率管步长，$\beta$ 管目标本身。

**ref 用当前 $\pi$ 行不行？**
不行。ref 一动，反解出来的 $r$ 零点跟着漂，间隔就没了锚，等于每一步都在换奖励函数。

**长度偏差怎么处理？**
用平均 logp、SimPO、显式长度惩罚，或者在标注说明里写「短而对优于长而对」。只加 $\beta$ 治不好长度 bias，因为 $\beta$ 不区分 token 数。

**正例概率一定会升吗？**
不一定。优化的是 $\Delta$，不是 $\log\pi(y_w)$。两边一起降、margin 在升是常见现象，要同时看 KL 和 holdout 胜率。
