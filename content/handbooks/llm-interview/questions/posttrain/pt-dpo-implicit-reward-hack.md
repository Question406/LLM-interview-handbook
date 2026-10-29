---
id: pt-dpo-implicit-reward-hack
section: posttrain
order: 250
level: S
title: DPO 的隐式奖励是什么？还会 reward hacking 吗？
quick: "DPO 的隐式奖励是 $\\beta\\log(\\pi_\\theta/\\pi_{\\mathrm{ref}})$，只约束 chosen 相对 rejected 的间隔。没有显式 RM 照样会 hacking，长度、套话都能把间隔拉大，要靠长度直方图、KL 和 held-out 评测去发现。"
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

DPO 的隐式奖励就是 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$，也就是策略相对 reference model 的对数比乘上 $\beta$。它照样会 reward hacking：DPO 优化的是偏好数据定义的间隔，长度和套话都能把这个间隔拉大。把 DPO 说成「没有奖励所以不会 hacking」，下一问问到长度膨胀就接不住了。完整推导见 `pt-dpo-derive`，这里只讲奖励写出来是什么，以及关掉 reward model（RM） 头之后为什么还会黑奖。

## 隐式奖励从哪来

KL 约束 RL 的最优策略满足 $\pi^\star\propto\pi_{\mathrm{ref}}e^{r/\beta}$。倒过来看，任何一个策略 $\pi_\theta$ 都对应一个隐式奖励

$$
r_\theta(x,y)=\beta\log\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{ref}}(y\mid x)}+Z(x).
$$

$Z(x)$ 对同一个 prompt 的两条回复是一样的，在 Bradley-Terry 里会消掉，所以偏好损失只看间隔：

$$
r_\theta(x,y_w)-r_\theta(x,y_l)=\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}.
$$

也就是说，DPO 的 reward 是 $\beta$ 倍的 $\log\pi-\log\pi_{\mathrm{ref}}$，没有哪个 RM 给它打标量分。$\beta$ 同时管着间隔的尺度和离参考有多远，见 `pt-dpo-beta`。

## 没有 RM 头，为什么还会 hacking

举个例子，偏好数据里 chosen 往往比 rejected 长一些。token 级的 log-ratio 是可加的，回答越长越容易把间隔拉开，模型就学会了写长。长度 normalization 和 SimPO 针对的就是这一点，见 `baidu-simpo-vs-dpo-length`。风格也一样，标注员或偏好模型喜欢的致谢、emoji、安全套话会进到 $y_w$ 里，模型跟着学。还有一种情况是 chosen 的绝对概率在下降，只要 rejected 掉得更多，loss 照样在降，见 `pt-dpo-chosen`。这算不上 bug，但看起来像「模型在学」，其实是在挤相对间隔。

发现它的办法是看 held-out 人评或下游指标有没有掉、长度直方图有没有右移、对 $\pi_{\mathrm{ref}}$ 的 KL 有没有飙、有没有模板化的 n-gram，通用的诊断方法见 `ali-reward-hacking`。缓解手段是做更好的 pair、做长度归一、选合适的 $\beta$；可验证任务就别硬套 DPO。

## 追问

**它和 PPO 里 RM 打的 $r$ 是一个东西吗？**
不是一个东西。PPO 的 $r$ 是外部给的分数；DPO 的 $r_\theta$ 是当前策略相对参考的对数比。DPO 训完以后可以把 $r_\theta$ 拿来当 RM 用，但训练时没有单独的打分头。

**$Z(x)$ 要不要估？**
标准 DPO 不用。估配分函数是另一类方法，面试时除非对方点名，先别往 IPO / KTO 上扯。

**为什么一定要有 $\pi_{\mathrm{ref}}$？**
没有参考，隐式奖励就不可辨识（identifiability），策略会漂到高似然的废话上。参考是锚，必须有。
