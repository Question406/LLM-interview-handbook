---
id: fund-adv-norm-bias
section: fundamentals
order: 151
level: S
title: Advantage 减均值、除标准差、按长度归一化，分别改了什么目标？
quick: "三步改的东西不一样。减均值（常数或 state baseline）不改策略梯度期望，只降方差；除 $\\sigma$ 会放大低方差的题，等于按题重新加权，改了目标；按回复长度平均让每条序列等权，全局 token 平均让每个 token 等权。Dr.GRPO / DAPO 争的就是后两层，没有脱离目标的「正确归一化」。"
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
这三步要分开看：减均值是合法的 baseline，只降方差；除标准差和 loss 按什么单位平均，都在改不同样本对目标的权重。OpenRLHF / veRL 里默认的 `adv = (adv - mean) / std` 常被当成「标准无偏预处理」，其实只有前一半是。Dr.GRPO 的价值就在于指出 normalization 本身就是目标的一部分，见 `pt-drgrpo`。

举个例子，一道题 8 条回答里 7 条对、1 条错，奖励差别很小，$\sigma$ 也很小；另一道难题对错各半，$\sigma$ 大。除完 $\sigma$ 以后，前一道题里那点微小差别被放大到和难题差不多的幅度，模型在「差不多都会」的题上学得更用力。这就是下面要拆的事。

## 减均值：合法 baseline，或者「相对这个 batch」

只依赖 state / 输入提示（prompt）的均值，比如同题组均值或价值评估模型（critic）的 $V(s)$，属于 `fund-pg-baseline`，期望不变。有限样本里组均值含自身，会带来 $O(1/G)$ 的收缩，见 `fund-finite-sample-baseline`。

全局 batch 减一个数，就是常数 baseline，仍然无偏。代价是同一条高分回答放进「全是高分的 batch」里优势会变小，训练稳了，但跨实验的 advantage 曲线就不能比绝对值。

如果对已经是 $A=Q-V$ 的量再减一次均值：$A$ 已经在 state 上 centered 的话，这一步几乎只影响数值；如果不同输入提示混在一起减，等于把题与题之间的绝对难度又抹掉一层。

PPO 实现里常见对当前 mini-batch 的 advantage 做 whitening。减均值这一半问题不大，危险在紧接着的除 $\sigma$。

## 除 $\sigma$：改的是题目和 batch 的权重

$$
\hat A_i=\frac{r_i-\bar r}{\sigma_r+\varepsilon}.
$$

$\sigma$ 小的组（差不多都对、只差一点点）优势被放大，相当于给这些题提高了有效学习率；$\sigma$ 大的难题被压扁。所以它的作用是 question-level reweighting，跟防 overflow 没关系。全对组 $\sigma=0$，加 $\varepsilon$ 只能避免 NaN，变不出信号。

Dr.GRPO 去掉这一层，让优势保持奖励分数（reward）的原尺度，估计更接近它定义的无偏 PG。REINFORCE++ 把 $\sigma$ 换成全局 batch 的：不再按题放大，但 batch 配方一变尺度就跟着变，见 `fund-reinforce-pp`。

被问「为什么还要除 std」，光答「为了稳定」不够。想跨题统一幅度、和 DeepSeekMath 对齐，就除；想保持无偏的 control variate、避免低方差题主导，就只减均值。两种都要监控，除了 $\sigma$ 之后，曲线反映的是相对排序，看不出绝对回报。

## 长度：每条回复等权，还是每个 token 等权

Vanilla GRPO 常先对每条回复做 $(1/|o_i|)\sum_t$，再对组平均。这样每条 response 的总权重相同，长回答里单个 token 的权重被摊薄。DAPO / Dr.GRPO 讨论改成全局 token 平均：

$$
\frac{1}{\sum_i|o_i|}\sum_{i,t}(\cdots).
$$

这样每个 token 等权，长的无关输出对梯度影响更大，长而正确的推理也不会被长度稀释。这里没有唯一正确答案：想要「每道题一张票」就用序列平均；想惩罚长套话、让长推理里的关键 token 拿到足够权重，就用 token 平均。slime 的 `--calculate-per-token-loss`、veRL 的 `loss_agg_mode` 就是这个开关，见 `pt-dapo`、`baidu-grpo-loss-agg`。

按长度去除奖励又是另一层：它削弱了「长而对」相对「短而对」的权重，根据符号不同，可能鼓励早停，也可能鼓励注水。经典条件下只有 potential-based shaping 能保持最优策略，见 `fund-shaping`，随 batch 变化的 normalization 不属于那一类。

## 追问

**Whitening 会让训练震荡吗？**
会。小 $G$ 上 $\sigma$ 本身就很噪，每一步尺度都在变。可以改成跨 batch 的滑动 $\sigma$，或者丢掉零方差组，见 `meituan-rl-loss-reward-oscillation`。

**只减均值、不除 std，还要 clip 吗？**
要。Baseline 和信任域是两条独立的轴。advantage 尺度变大时，同样的 $\varepsilon$ 会更早触发 clip。

**组内 $A$ 加起来等于 0，是不是说明无偏？**
只说明做了中心化。无偏问的是 $\mathbb{E}[\nabla\log\pi\cdot\hat A]$ 是否等于 $\nabla J$，跟组内和是不是 0 无关。

**长度归一化能消掉 length bias 吗？**
消不掉，它只是定义了另一种 length weighting。先写清楚自己要的目标，再选归约方式。
