---
id: pt-rloo-vs-grpo
section: posttrain
order: 25
level: A
title: RLOO 和 GRPO 都不用 Critic，它们的 baseline 有什么关键区别？
quick: >-
  两者都用同 prompt 的多条 rollout 降方差。RLOO 给每条样本用“其余样本 reward 的均值”作 leave-one-out
  baseline；GRPO 常用组均值并再按组标准差归一化，后者会改变 advantage 的尺度与统计性质。
tags:
  - RLOO
  - GRPO
  - RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: DeepSeekMath / GRPO
    url: 'https://arxiv.org/abs/2402.03300'
    type: legacy-reference
  - title: GRPO calibration analysis
    url: 'https://arxiv.org/abs/2508.11800'
    type: legacy-reference
---

两者的共同点是：不训练 learned value model，而是让同 prompt 的多次采样彼此充当 baseline。差别不在「有没有 critic」——都没有——而在 baseline 是否包含当前样本、以及是否再做 group-std normalization。把所有「无 critic RL」混为一谈，下一问标准差归一化会答空。面试要说清具体实现：leave-one-out 还是组均值、除不除 $\sigma$、全同组怎么处理，而不是背「都是组内相对优势」。两者都不能代替 critic 去做逐步信用分配；长轨迹逐步奖仍可能需要 GAE。适用场景也类似：可验证奖励、能付得起 group rollout。全对或全错时，两条算法都会失去方向，这是结构问题，不是实现 bug。

## 共同点：同 prompt 多样本降方差

设同一 $x$ 采 $G$ 条 rollout，奖励 $r_1,\ldots,r_G$。REINFORCE 的高方差来自「一条轨迹自己当自己的参照」。同题多采样后，别人的分数可以当对照，不必再训 $V(s)$。这要求组内真有相对好坏：全对或全错时，两条算法都会失去方向。省 critic 的代价是必须付 group 的生成成本，并接受「同一 prompt 的多样本足够构成对比」这一假设。逐步过程奖、单条轨迹很长时，这个假设会破，要过程分或回到价值函数。

## RLOO：leave-one-out，当前样本不进 baseline

对第 $i$ 条，baseline 是其余 $G-1$ 条的均值：

$$
b_i=\frac{1}{G-1}\sum_{j\neq i}r_j,\qquad \hat A_i=r_i-b_i.
$$

当前 reward 不会「抵消自己」，是 REINFORCE control variate 的直接构造。$G=2$ 时差异尤其明显：GRPO 的组均值把两条都往中间拉，RLOO 则用对方当 baseline，优势是两条之差。RLOO 通常不做组标准差缩放，优势仍带着原始 reward 尺度，跨题幅度不可比，但不会因为低方差题被放大而改变题目权重。要保持 reward 原尺度、强调无偏 control variate，偏 RLOO。

## GRPO：组均值中心化，再按组标准差缩放

GRPO 常用

$$
\hat A_i=\frac{r_i-\bar r}{\sigma_r+\varepsilon},\qquad \bar r=\frac{1}{G}\sum_i r_i.
$$

$\bar r$ 含当前样本，中心化后组内优势和为零。再除 $\sigma_r$ 会改变不同题目的权重：方差小的题（差不多都对、只差一点点）优势被放大，方差大的题被压扁。这不是纯数值技巧，对随机结果上的 calibration 也可能有影响——文献里对 GRPO 标准化的批评，指的就是这一层。全对 / 全错时 $\sigma_r=0$，优势为 0，没有相对信号。$G$ 大时 $\bar r$ 与 leave-one-out 接近，差别主要剩 std；$G$ 小时「是否含自身」和是否除 std 都会显出来。

## 选哪一个：尺度、权重、实现

要保持 reward 原尺度、强调无偏 control variate，偏 RLOO。要跨题统一优势幅度、和 DeepSeekMath 实现对齐，偏 GRPO。汇报时写明 $G$、是否含自身、是否除 std，避免「我们用了无 critic RL」这种空句。两者遇到空组都要过滤或动态采样，换名字解决不了零梯度。和 PPO critic 比：critic 估跨状态基线，能处理单条轨迹；这里假设同 prompt 多样本足够构成对比。现场用 $G=2$ 走一遍数值，最容易把「含不含自身」讲清楚。

## 追问

- **含不含自身差多少？** $G$ 大时 $\bar r$ 与 leave-one-out 接近；$G$ 小时 RLOO 更「不自抵消」。$G=2$ 时差得最明显，适合白板。
- **为什么 std 会改权重？** 低方差题的微小分差被放大，等于提高这些题的学习率；高方差难题被压扁。这会改 calibration，不是单纯防数值炸。
- **全组同分怎么办？** 两条都零梯度。过滤空组或动态采样，不是换名字能解决。难题长期全错，要冷启动而不是再降 lr。
- **和 PPO critic 比？** critic 估跨状态基线，能处理单条轨迹与逐步奖；这里假设同 prompt 多样本足够构成对比。长 horizon 过程奖时，无 critic 两条都可能不够。
