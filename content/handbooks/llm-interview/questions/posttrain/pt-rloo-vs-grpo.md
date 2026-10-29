---
id: pt-rloo-vs-grpo
section: posttrain
order: 25
level: A
title: RLOO 和 GRPO 都不用 Critic，它们的 baseline 有什么关键区别？
quick: "两者都用同一道题的多条轨迹互相当 baseline。RLOO 用其余样本的平均奖励（leave-one-out），保留原始奖励尺度；GRPO 用包含自身的组均值，再除以组标准差，这会改变优势的尺度和不同题目的训练权重。"
tags:
  - RLOO
  - GRPO
  - RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeekMath / GRPO
    url: 'https://arxiv.org/abs/2402.03300'
    type: legacy-reference
  - title: GRPO calibration analysis
    url: 'https://arxiv.org/abs/2508.11800'
    type: legacy-reference
---

关键区别有两个：baseline 包不包含当前样本，以及要不要再除组标准差。RLOO 用其余 $G-1$ 条的平均当 baseline，通常不做 std 缩放；GRPO 用包含自己的组均值，再除以组内 $\sigma$。两者都不训 learned value model，所以「都是无 critic RL」这句话说明不了什么，下一问问到标准差 normalization 就会答空。

共同的出发点是同一 prompt 多样本降方差。设同一 $x$ 采 $G$ 条 rollout，奖励 $r_1,\ldots,r_G$。REINFORCE 方差高，是因为一条轨迹自己当自己的参照；同题多 sampling 后，别人的分数可以当对照，就不必再训 $V(s)$。代价是要付 group 的生成成本，并且假设同一 prompt 的多个样本足以构成对比。逐步过程奖励、单条轨迹很长时这个假设会破，要么上过程分，要么回到 value function 和 GAE。两者都替代不了价值评估模型（critic）做逐步 credit assignment。

RLOO 对第 $i$ 条的 baseline 是其余 $G-1$ 条的均值：

$$
b_i=\frac{1}{G-1}\sum_{j\neq i}r_j,\qquad \hat A_i=r_i-b_i.
$$

当前样本的奖励分数（reward）不会「抵消自己」，这是 REINFORCE control variate 的直接构造。它通常不做组标准差缩放，优势带着原始奖励尺度，跨题的幅度不可比，但也不会因为低方差题被放大而改变题目权重。

GRPO 常用

$$
\hat A_i=\frac{r_i-\bar r}{\sigma_r+\varepsilon},\qquad \bar r=\frac{1}{G}\sum_i r_i.
$$

$\bar r$ 含当前样本，中心化后组内优势和为零。再除以 $\sigma_r$，不同题目的权重就变了：方差小的题（差不多都对、只差一点点）优势被放大，方差大的题被压扁。这会影响随机结果上的 calibration，文献里对 GRPO standardization 的批评指的就是这一层，它不只是一个数值技巧。

用 $G=2$ 走一遍最清楚。两条的奖励是 1 和 0：GRPO 的组均值是 0.5，两条都被往中间拉，再除以 std；RLOO 用对方当 baseline，优势就是两条之差。$G$ 大时 $\bar r$ 和 leave-one-out 很接近，差别主要剩 std 这一项；$G$ 小时「含不含自身」和「除不除 std」都会显出来。

怎么选：要保持 reward 原尺度、强调无偏的 control variate，偏 RLOO；要跨题统一优势幅度、和 DeepSeekMath 的实现对齐，偏 GRPO。汇报时写明 $G$、是否含自身、是否除 std，别用「我们用了无 critic RL」这种空句。全对或全错时两种算法都没有相对信号，GRPO 那边 $\sigma_r=0$、优势为 0，RLOO 那边优势也全是 0，都要靠过滤空组或动态 sampling。这是结构问题，换个算法名字解决不了。

## 追问

**含不含自身差多少？**
$G$ 大时差不多；$G$ 小时 RLOO 更「不自抵消」，$G=2$ 时差得最明显，适合白板。

**为什么除 std 会改权重？**
低方差题的微小分差被放大，相当于提高了这些题的学习率，高方差的难题被压扁。这会改 calibration，不只是防数值炸。

**全组同分怎么办？**
两种都是零梯度。过滤空组或动态 sampling；难题长期全错，要做冷启动，再降 lr 没用。

**和 PPO 的 critic 比呢？**
critic 估的是跨状态的基线，能处理单条轨迹和逐步奖励；这两种都假设同一 prompt 的多样本足以构成对比。长 horizon 的过程奖励下，两种都可能不够。
