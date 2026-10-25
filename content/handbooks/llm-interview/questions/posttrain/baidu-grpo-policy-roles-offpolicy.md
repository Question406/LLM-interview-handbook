---
id: baidu-grpo-policy-roles-offpolicy
section: posttrain
order: 102
level: S
title: 百度文心后训练：GRPO 的 $\pi_\theta$、$\pi_{\mathrm{old}}$、$\pi_{\mathrm{rollout}}$ 是谁？大 batch 怎么缓解 off-policy？
quick: "$\\pi_{\\mathrm{rollout}}$ 是推理引擎上产生轨迹的行为策略，$\\pi_{\\mathrm{old}}$ 是固定在一次 update / batch 上、当 ratio 分母的旧策略，$\\pi_\\theta$ 是当前待优化的策略；实现上前两者可以同源，但时间角色不同。大 batch / 异步队列会拉大行为策略和训练策略的差距，要控制 freshness、丢弃过期样本或做受控校正。"
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

按时间轴分：$\pi_{\mathrm{rollout}}$ 是推理引擎上产生轨迹的行为策略，$\pi_{\mathrm{old}}$ 在一个 optimization window 里冻结、当 importance ratio 的分母，$\pi_\theta$ 是这个窗口里正在被梯度更新的当前策略。大 batch 带来的 off-policy 是 freshness 问题，办法是缩短队列、限制策略年龄、丢弃或校正过期样本，把 `batch_size` 再加大修不了。

三个 $\pi$ 别按名字死记，要按「谁产生轨迹、谁当分母、谁被更新」来拆。$\pi_{\mathrm{rollout}}$ 负责逐 token 生成（decode），产出轨迹以及采样当时每个 token 的 log-prob。$\pi_{\mathrm{old}}$ 是

$$
\rho_t=\frac{\pi_\theta(o_t\mid q,o_{\lt t})}{\pi_{\mathrm{old}}(o_t\mid q,o_{\lt t})}
$$

的分母。$\pi_\theta$ 的 log-prob 必须在训练图里重算，引擎里的数值不能直接信。有人会说「同步实现里它们是同一个检查点，所以不用区分」。同步实现确实可以让采样轨迹（rollout）和 old 来自同一个版本，可「采样的那一瞬间」和「已经 step 过的当前策略」仍是两个时刻。比如同一批轨迹训好几个 epoch，到后面 $\pi_\theta$ 已经走远了，$\rho$ 的方差和 clip fraction 都会明显上升。组优势还是用这批 $n$ 条的奖励来算，见 `sys-rl-group-n`，变得 off-policy 的是策略比，优势的定义没变。这 $n$ 条必须在同一个 window 里估均值，组被拆开比样本过期还要命。另外还有 $\pi_{\mathrm{ref}}$：KL 的方向是当前 $\pi_\theta$ 对冻结的 $\pi_{\mathrm{ref}}$，见 `fund-kl-directions`；把 ref 当成 old，clip 的对象就错了。

再说大 batch。batch 太大、actor-learner 异步、队列里堆着旧 rollout，都会让 $\pi_{\mathrm{rollout}}$ 离 $\pi_\theta$ 越来越远。实际做法是缩短 rollout 队列，限制每批的更新次数和最大 policy age，按版本丢弃样本或者分组统计，同时持续监控 ratio 分布、KL、clip fraction、奖励分数（reward）和 holdout。用更大的 batch 把过期样本平均掉没用，平均的还是过期梯度。PPO / GRPO 的 clip 在有利方向越界时会把 token 梯度打成 0；CISPO 把 IS 权重截断后 detach，梯度仍走 $\log\pi$，更适合受控复用，见 `pt-cispo`。两者都只是校正，不能据此无限复用旧轨迹。过期样本该丢还是该降权，看 policy age 的直方图，别看平均 reward。

## 追问

**$\pi_{\mathrm{ref}}$ 算第四个吗？**
算，但它只进 KL，不进 $\rho$。把 ref 当 old，信任域约束的就不再是「相对采样时的策略」。

**能不能直接用引擎的 logp 当 $\pi_{\mathrm{old}}$？**
不建议。引擎的数值常和训练图不一致，精度、温度、停止符都会带来差异，应该在训练图里重算 old。

**丢弃过期样本和加大 clip $\varepsilon$，先做哪个？**
先丢。丢弃保住 on-policy；加大 $\varepsilon$ 只是让更离轨的 token 还留着梯度，方差更大。

**GRPO 算 on-policy 吗？**
理想情况下同步、一步更新、不复用，算近似 on-policy；大 batch、多 epoch、异步就是 off-policy，要当问题来管。

**staleness 和零方差组同时出现怎么办？**
先看有效组，见 `sys-rl-group-n`；有效组够了、ratio 还出现极端值，再查 freshness。两本账别混。
