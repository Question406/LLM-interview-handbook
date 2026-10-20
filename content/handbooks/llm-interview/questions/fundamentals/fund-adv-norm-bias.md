---
id: fund-adv-norm-bias
section: fundamentals
order: 151
level: S
title: Advantage 减均值、除标准差、按长度归一化，分别改了什么目标？
quick: "减均值（常数 / state baseline）不改策略梯度期望，只降方差。除 $\\sigma$ 按切片重加权：低方差题被放大，这是改目标，不是数值稳定。按回复长度平均让每条序列等权，全局 token 平均让每个 token 等权。Dr.GRPO / DAPO 争的就是这一层，没有脱离目标的「正确归一化」。"
tags:
  - Advantage
  - GRPO
  - Bias-Variance
  - Dr.GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Understanding R1-Zero-Like Training — A Critical Perspective (Dr.GRPO)
    url: https://arxiv.org/abs/2503.20783
    type: primary
  - title: DAPO — Decoupled Clip and Dynamic sAmpling Policy Optimization
    url: https://arxiv.org/abs/2503.14476
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: secondary
---

常见误区是：OpenRLHF / veRL 里默认的 `adv = (adv - mean) / std` 是「标准无偏预处理」。要分别看减均值、除标准差，以及 loss 按什么单位平均。减均值通常用于降低方差；后两项则会改变不同样本对优化目标的权重。Dr.GRPO 的价值就是指出 normalization 本身是目标，见 `pt-drgrpo`。

## 减均值：合法 baseline，或「相对这个 batch」

- 只依赖 state / 输入提示（prompt） 的均值：同题组均值、或 价值评估模型（critic） $V(s)$，属于 `fund-pg-baseline`。期望不变。有限样本含自身会有 $O(1/G)$ 收缩，见 `fund-finite-sample-baseline`。
- 全局 batch 减一个数：这是常数 baseline，仍无偏。同一条高分回答在「全是高分的 batch」里优势变小，稳，但跨实验的 advantage 曲线不能比绝对值。
- 对已经是 $A=Q-V$ 的量再减均值：若 $A$ 已在 state 上 centered，再减全局均值几乎只是数值；若不同一输入提示 混在一起，等于把题与题的绝对难度再抹一层。

PPO 实现里常见「对当前 mini-batch 的 advantage 做 whitening」。减均值这一半问题不大；危险的是紧接着除 $\sigma$。

## 除 $\sigma$：改的是题目 / batch 权重

$$
\hat A_i=\frac{r_i-\bar r}{\sigma_r+\varepsilon}.
$$

$\sigma$ 小的组（差不多都对、只差一点点）优势被放大，等于提高这些题的有效学习率；$\sigma$ 大的难题被压扁。这不是防 overflow，是 question-level reweighting。全对组 $\sigma=0$，再加 $\varepsilon$ 只能避免 NaN，变不出信号。Dr.GRPO 去掉这层，让优势保持 奖励分数（reward） 原尺度，估计更接近它定义的无偏 PG。REINFORCE++ 把 $\sigma$ 改到全局 batch：不再按题放大，但 batch 配方一变尺度就变，见 `fund-reinforce-pp`。

被问「为什么还要除 std」，不要只答稳定。想跨题统一幅度、和 DeepSeekMath 对齐，才除；想保持无偏 control variate、避免低方差题主导，就只减均值。两边都要监控：除 $\sigma$ 之后看的是相对排序，不是绝对回报。

## 长度：每条回复等权，还是每个 token 等权

Vanilla GRPO 常先 $(1/|o_i|)\sum_t$ 再对组平均：每条 response 总权重相同，长回答里单 token 被摊薄。DAPO / Dr.GRPO 讨论改成全局

$$
\frac{1}{\sum_i|o_i|}\sum_{i,t}(\cdots).
$$

每个 token 等权，长的无关输出对梯度影响更大，长而正确的推理也不会被除长度稀释。没有唯一正确答案：要「每道题一张票」用序列平均；要惩罚长套话、让长推理过程中的关键 token 得到足够权重，用 token 平均。slime `--calculate-per-token-loss`、veRL `loss_agg_mode` 就是这个开关，见 `pt-dapo`、`baidu-grpo-loss-agg`。

按长度除奖励又是另一层：削弱「长而对」相对「短而对」，可能鼓励早停或注水，取决于符号。Potential-based shaping 才在经典条件下保持最优策略，见 `fund-shaping`；随 batch 变的 normalization 不在那一类。

## 追问

- **Whitening 会震荡吗？** 会。小 $G$ 上 $\sigma$ 本身很噪，一步一个尺度。可改成跨 batch 滑动 $\sigma$，或丢掉零方差组，见 `meituan-rl-loss-reward-oscillation`。
- **只减均值、不除 std，还要 clip 吗？** 要。Baseline 和信任域是两轴。advantage 尺度变大时，同样的 $\varepsilon$ 会更早 clip。
- **组内 $A$ 和为 0 说明无偏吗？** 只说明中心化了。无偏问的是 $\mathbb{E}[\nabla\log\pi\cdot\hat A]$ 是否等于 $\nabla J$，不是组和是否为 0。
- **长度归一化能消 length bias 吗？** 它定义了另一种 length weighting，并不能「消除」偏差。先写你要的目标，再选归约。
