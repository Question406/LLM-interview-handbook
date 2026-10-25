---
id: stepfun-grpo-group-advantage
section: posttrain
order: 132
level: S
title: 阶跃星辰：GRPO 的优势值怎么算，baseline 是什么？
quick: "对同一输入提示采 $n$ 条输出，优势就是每条的奖励减去组内均值、再除以组内标准差；baseline 就是这组的经验均值，不用另训 value。全组奖励相同时优势为 0；GAE 那边是用学出来的 Critic 估基线。"
tags:
  - StepFun
  - GRPO
  - Advantage
  - GAE
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阶跃星辰大模型算法实习面经
    url: https://www.nowcoder.com/feed/main/detail/933afb27edd84b438682fd5bba95fbb3
    type: candidate-first-hand
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary-paper
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；轮次未披露
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“GRPO的优势值是什么？怎么算？baseline是什么？”**

GRPO 的 baseline 就是同一输入提示下这组采样轨迹（rollout）的经验均值，优势是每条奖励相对这个均值的标准化残差。没有价值评估模型（critic），不代表没有 baseline。答成「优势就是奖励」会出问题：全组奖励相同时优势是 0，后面那类「on-policy 采不出正确答案」的题，根子就在这里。

## 公式：组均值当 baseline，再除标准差

同一输入提示采 $n$ 条 completion，奖励是 $r_1,\ldots,r_n$。组均值 $\bar r=\frac{1}{n}\sum_i r_i$ 就是 baseline，第 $i$ 条的优势常写成

$$
\hat A_i=\frac{r_i-\bar r}{\sigma_r+\varepsilon},
$$

$\sigma_r$ 是组内标准差，$\varepsilon$ 防止除零。比均值高的样本拿正优势，比均值低的拿负优势，然后进 clipped policy gradient。比如一组里有的答对得 1、有的答错得 0，答对的优势为正，答错的为负。token 级实现里，一条 completion 的所有 token 通常共享同一个 $\hat A_i$，没有逐步的 GAE。奖励尺度的变化会被标准化吸收一部分，但还是要盯有效组的比例：很多组 $\sigma_r\approx 0$ 时，曲线再好看也没有更新方向。

## 全组相同时梯度为零

全对或全错时所有 $r_i$ 相同，$\hat A_i=0$，这一步没有方向。这是组内相对优势的结构性质，跟实现 bug 无关。难题上策略几乎采不到对的，就会长期零梯度，这时要靠冷启动监督微调（SFT）、降难度、加大 $n$ 或动态采样来解决，光降 lr 没用。RLOO 的 leave-one-out 在全组相同时同样为零，只是 $n$ 较小时，「算不算自己」会让数值略有不同。

## 和 GAE 的区别

GAE 用学出来的 $V(s)$ 做跨状态的基线，能处理长轨迹上的逐步奖励。GRPO 假设同一个 prompt 的多个样本就足够构成对比，省掉了 critic，也省掉了逐步的信用分配。如果有逐步的过程奖励、单条轨迹又很长，组均值可能不够用，要上过程分或回到价值函数。还有一件容易混进来的事：强化学习（RL）训 MoE 时的路由漂移是另一个问题，GSPO 把 token 级 ratio 改成序列级 ratio，管的是重要性权重的稳定性，没有改优势的定义。

## 追问

**baseline 到底是谁？**
就是这组的经验均值，既不是单独的 value 网络，也不是全局的移动平均。

**为什么还要除以 $\sigma$？**
为了统一不同题之间的优势尺度。副作用是低方差的题会被放大。

**每个 token 的优势不一样吗？**
常见实现里共享同一个 $\hat A_i$。要逐步不同，得另加过程奖励。

**这和「采不出正确答案」有什么关系？**
全错的组优势为 0，on-policy 训练会卡住，要先补冷启动或课程。
