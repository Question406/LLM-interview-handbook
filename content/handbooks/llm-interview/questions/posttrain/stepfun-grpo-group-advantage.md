---
id: stepfun-grpo-group-advantage
section: posttrain
order: 132
level: S
title: 阶跃星辰：GRPO 的优势值怎么算，baseline 是什么？
quick: >-
  对同一 prompt 采 $n$ 条输出，优势是组内奖励减均值（再除标准差），baseline 就是该组经验均值，不另训 value。全组奖励相同则优势为
  0；这与 GAE 用学习 critic 估计基线不同。
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

没有 critic 不等于没有 baseline。GRPO 的 baseline 就是**同一 prompt 下这组 rollout 的经验均值**，优势是相对它的标准化残差。别答「优势就是奖励」，全组奖励相同则优势为 0，这正是后续「on-policy 采不出正确答案」类题的根源。也不要把 GSPO 的序列级 ratio 和优势定义混为一谈。

## 公式：组均值作 baseline，再除标准差

设同一 prompt 采样 $n$ 条 completion，奖励 $r_1,\ldots,r_n$。组均值 $\bar r=\frac{1}{n}\sum_i r_i$ 就是 baseline。第 $i$ 条优势常写成

$$
\hat A_i=\frac{r_i-\bar r}{\sigma_r+\varepsilon},
$$

其中 $\sigma_r$ 是组内标准差，$\varepsilon$ 防除零。相对均值高的样本得正优势，低的得负优势，再进入 clipped policy gradient。token 级实现往往让一条 completion 的所有 token **共享**同一 $\hat A_i$，没有逐步 GAE。reward 尺度变化会被标准化部分吸收，但仍要监控有效组比例：很多组 $\sigma_r\approx 0$ 时，曲线再好看也没有更新方向。

## 全同组：零梯度，不是实现 bug

全对或全错时 $r_i$ 相同，$\hat A_i=0$，这步没有方向。这是组内相对优势的结构性质。难题上策略几乎采不到对的，就会长期零梯度，要靠冷启动 SFT、降难度、加大 $n$ 或动态采样，而不是再降 lr。对比 RLOO：leave-one-out 同样在全同时为零，但 $n$ 较小时「是否含自身」会让数值略有不同。

## 对比 GAE：跨状态价值 vs 同题对照

GAE 用学习到的 $V(s)$ 做跨状态基线，能处理长轨迹逐步奖励。GRPO 假设「同一 prompt 的多样本足够构成对比」，省 critic、省逐步信用分配。逐步过程奖、单条轨迹很长时，组均值可能不够，要过程分或回到价值函数。RL 训 MoE 时路由漂移是另一问题，GSPO 从 token 比改到序列比，管的是重要性权重稳定性，不是改优势定义。

## 追问

- **baseline 是谁？** 该组经验均值，不是单独的 value 网络，也不是全局移动平均。
- **为什么还要除 $\sigma$？** 统一不同题的优势尺度；副作用是低方差题被放大。
- **token 级优势不同吗？** 常见实现共享同一 $\hat A_i$。逐步不同要另加过程奖励。
- **和「采不出正确答案」的关系？** 全错组优势为 0，on-policy 会卡住，先补冷启动或课程。
