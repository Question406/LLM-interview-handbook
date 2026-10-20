---
id: pt-dpo-implicit-reward-hack
section: posttrain
order: 250
level: S
title: DPO 的隐式奖励是什么？还会 reward hacking 吗？
quick: "DPO 的隐式奖励是 $\\beta\\log(\\pi_\\theta/\\pi_{\\mathrm{ref}})$，只约束 chosen 相对 rejected 的间隔。没有显式 RM 也会 hacking，长度和套话都能抬高间隔。"
tags:
  - DPO
  - Reward Hacking
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: SimPO
    url: https://arxiv.org/abs/2405.14734
    type: primary
---

推导链见 `pt-dpo-derive`。本题只钉两件事：**奖励函数写出来是什么**，以及**关掉 奖励模型（RM） 头之后还会不会黑奖**。把 直接偏好优化（DPO） 说成「没有奖励所以不会 hacking」，下一问长度膨胀就会空。

## 隐式奖励从哪来

KL 约束 强化学习（RL） 的最优策略满足 $\pi^\star\propto\pi_{\mathrm{ref}}e^{r/\beta}$。反过来，任意策略 $\pi_\theta$ 都对应一个隐式奖励

$$
r_\theta(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}+Z(x).
$$

$Z(x)$ 对同一输入提示 的两条回复相同，在 Bradley-Terry 里消掉。于是偏好损失只看间隔

$$
r_\theta(x,y_w)-r_\theta(x,y_l)=\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}.
$$

现场口令：DPO 的 reward 就是 $\beta$ 倍的 $\log\pi-\log\pi_{\mathrm{ref}}$，不是 RM 打出来的标量。$\beta$ 同时管间隔尺度和离参考的远近，见 `pt-dpo-beta`。

## 没有 RM 头，仍会 hacking

优化的是偏好数据定义的间隔，不是「人类想要的」。典型捷径：

- **长度。** token 级 log-ratio 可加，更长的 chosen 更容易拉开间隔。长度归一化或 SimPO 就是冲这个，见 `baidu-simpo-vs-dpo-length`。
- **风格 / 套话。** 标注员或偏好模型喜欢的致谢、emoji、安全套话，会进 $y_w$。
- **chosen 绝对概率下降。** 只要 rejected 掉得更多，loss 仍降，见 `pt-dpo-chosen`。这不是 bug，但看起来像「模型在学」，实际在挤相对间隔。

怎么发现：held-out 人工 / 下游掉、长度直方图右移、对 $\pi_{\mathrm{ref}}$ 的 KL 飙、模板 n-gram。通用诊断见 `ali-reward-hacking`。缓解：更好的 pair、长度归一、适当 $\beta$、可验证任务别硬套 DPO。

## 追问

- **和 PPO 里 RM 打的 $r$ 是一个东西吗？** 不是。PPO 的 $r$ 是外部分数；DPO 的 $r_\theta$ 是当前策略相对参考的对数比。DPO 结束后可以把 $r_\theta$ 当 RM 用，但训练时没有单独打分头。
- **$Z(x)$ 要不要估？** 标准 DPO 不用。估配分函数是另一类方法，面试先别往 IPO / KTO 滑，除非对方点名。
- **为什么还要 $\pi_{\mathrm{ref}}$？** 没有参考，隐式奖励不 identifiability，策略会漂到高似然废话。参考是锚，不是可选项。
