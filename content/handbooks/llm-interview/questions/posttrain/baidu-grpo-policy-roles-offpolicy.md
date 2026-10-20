---
id: baidu-grpo-policy-roles-offpolicy
section: posttrain
order: 102
level: S
title: 百度文心后训练：GRPO 的 $\pi_\theta$、$\pi_{\mathrm{old}}$、$\pi_{\mathrm{rollout}}$ 是谁？大 batch 怎么缓解 off-policy？
quick: >-
  $\pi_{\mathrm{rollout}}$ 是采样行为策略，$\pi_{\mathrm{old}}$ 是固定在一次 update / batch 上用于 ratio 的旧策略，$\pi_\theta$ 是当前待优化策略。实现可让前两者同源，
  但它们的时间角色不同。大 batch / 异步队列会拉大行为与训练策略差距，应控制 freshness、丢弃过期样本或受控校正。
tags:
  - Baidu
  - ERNIE
  - Post-training
  - GRPO
  - Policy Lag
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百度 - 大模型后训练实习生 二面（候选人原帖）
    url: https://www.nowcoder.com/discuss/864605093486682112
    type: candidate-first-hand
---

## 真题记录

- 公司：百度
- 团队 / 岗位：文心一言后训练
- 届别 / 流程：实习；二面
- 面试时间：2026-03-20
- 来源类型与可信度：牛客候选人原帖，A（公司、面试时间、岗位、轮次与业务方向明确）
- 原始措辞：**“GRPO里的 $\pi_\theta$, $\pi_{\theta_{\mathrm{old}}}$, $\pi_{\theta_{\mathrm{rollout}}}$”**；追问：**“GRPO里是off-poliy/on-policy，当batch_size非常大时，如何缓解off-poliy的问题？”**

这块容易按名字死记三个 $\pi$，或者说「同步实现里它们是同一个检查点，所以不用区分」。按时间轴拆角色：谁产生轨迹、谁当 importance ratio 的分母、谁被梯度更新。实现可以让前两者同源，时间角色仍然不同。大 batch、异步队列、多 epoch 复用会拉大行为策略与训练策略的差距，这是 freshness 问题，不是把 `batch_size` 再加大能修的。KL 方向仍是当前 $\pi_\theta$ 对冻结 $\pi_{\mathrm{ref}}$，见 `fund-kl-directions`；把 ref 当成 old，clip 的对象就错了。

## 三个 $\pi$，三个时刻

$\pi_{\mathrm{rollout}}$ 是推理引擎上的行为策略，负责 逐 token 生成（decode），产出轨迹以及采样当时的 token log-prob。$\pi_{\mathrm{old}}$ 在一个 optimization window 内冻结，作为

$$
\rho_t=\frac{\pi_\theta(o_t\mid q,o_{\lt t})}{\pi_{\mathrm{old}}(o_t\mid q,o_{\lt t})}
$$

的分母。$\pi_\theta$ 是该 window 内被更新的当前策略，训练图必须重算 log-prob，不能直接相信引擎里的数值。同步实现可以让 采样轨迹（rollout） 与 old 来自同一版本，仍不能把「采样那一瞬间」和「已经 step 过的当前」混为一谈。同一批轨迹做多个 epoch 时，$\pi_\theta$ 已走远，$\rho$ 的方差和 clip fraction 会明显上升。组优势仍然用这批 $n$ 条的奖励来算，见 `sys-rl-group-n`；变得 off-policy 的是策略比，不是优势的定义。$n$ 条必须仍在同一 window 里估均值，组被拆开比 stale 更致命。

## 大 batch 如何缓解 stale

batch 过大、actor-learner 异步、队列里堆着旧 rollout，都会使 $\pi_{\mathrm{rollout}}$ 远离 $\pi_\theta$。实务上缩短 rollout queue、限制每批更新次数和最大 policy age、按版本丢弃或分组统计样本，并持续监控 ratio 分布、KL、clip fraction、奖励分数（reward） 和 holdout。不要只用更大的 batch 把 stale 平均掉，平均的是过期梯度。PPO / GRPO 的 clip 在有利方向越界时把 token 梯度打成 0；CISPO 把 IS 权重截断后 detach，梯度仍走 $\log\pi$，更适合受控复用，见 `pt-cispo`。两者都是校正，不能据此无限复用旧轨迹。过期样本该丢还是该降权，要看 policy age 的直方图，不要看平均 reward。

## 追问

- **$\pi_{\mathrm{ref}}$ 是第四个吗？** 是，但只进 KL，不进 $\rho$。把 ref 当 old，信任域约束的就不是「相对采样时策略」。
- **能不能用引擎 logp 当 $\pi_{\mathrm{old}}$？** 数值常和训练图不一致（精度、温度、停止符）。应在训练图重算 old。
- **丢弃过期和加大 clip $\varepsilon$ 哪个先？** 丢弃保 on-policy；加大 $\varepsilon$ 只是让更离轨的 token 还留梯度，方差更大。先丢再谈 clip。
- **GRPO 算 on-policy 吗？** 理想同步、一步更新、不复用，是近似 on-policy；大 batch / 多 epoch / 异步就是 off-policy，要当问题管。
- **staleness 和零方差组一起出现？** 先看有效组，见 `sys-rl-group-n`；有效组足够但 ratio 出现极端值，再查 freshness。两本账不要混。
