---
id: meituan-rl-loss-reward-oscillation
section: posttrain
order: 103
level: S
title: 美团：RL 过程中的 reward 或 loss 震荡严重，如何排查？
quick: >-
  先按数据、reward、policy 与系统四层拆监控：成功率、reward 分布/方差、KL、entropy、梯度范数、有效 token、
  版本滞后和 NaN。用固定种子与小规模复现实验逐个关掉变量；不能只靠平滑曲线或盲目调低学习率。
tags:
  - Meituan
  - RL Training
  - Debugging
  - Stability
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 大模型算法 美团面经分享（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/c6573225622842c290a00496c58db386
    type: candidate-first-hand
---
## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法；具体团队原帖未披露
- 届别 / 流程：原帖未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-18
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位与发帖时间明确，届别和轮次未披露）
- 原始措辞：**“RL 过程中 reward 或者 loss 震荡严重，怎么办？”**

错法：只对曲线做滑动平均，或盲目把学习率砍半。先明确震荡的是 reward 还是 loss，以及它是否伤害最终 success。很多「震荡」来自组间难度不齐或 parser 偶发，平滑会把坏问题盖住。GRPO 里优势要除以组内 $\sigma$，loss 比 reward 更抖是预期，要用 holdout success 判决，不要用 $L$ 判决。排查要分层监控、单变量复现，别只背「把 lr 改小」。

## 1. 四层监控，先定位哪一层在跳

按 rollout 版本、任务桶和长度记录：reward 均值 / 方差、有效组比例、pass@k、KL、entropy、clip fraction、advantage 标准差、梯度范数、NaN / overflow、actor-rollout policy lag、有效 token 数。缺一项就不能说「已经排查过」。

- **Reward 跳**：parser / verifier 不稳定（同一轨迹重打分不一致）、数据混入、长度分布变、偶发全对全错组让 $\sigma$ 起伏；
- **Loss 跳**：reward 尺度没对齐、长尾 token、学习率、batch 过小、分布式 all-reduce 数值问题、$\rho$ 极端、advantage whitening 在小 $G$ 上很噪。

公式

$$
\hat{A}_i=\frac{r_i-\mu}{\sigma+\epsilon}
$$

会把「偶尔多一个对的」放大成巨大优势。所以先确认 $r$ 定义稳定，再谈优化器。Reward 跳而 holdout 稳，可能只是 batch 组成变了；Loss 跳且 NaN，才是数值紧急。

## 2. 复现实验：一次只关一个变量

固定 prompt、seed、模型快照和单机小 batch 重现，再逐项：冻结数据和 verifier、固定温度、检查归一化 / whitening、缩小更新步长或增大有效 token batch、调 KL / clip / entropy、对极端 advantage 截断。最后放回异步 pipeline，看 policy lag 是否把已复现的稳定又打回去。失败：在异步大集群上同时改五个超参，永远不知道是谁修好的。只在复现确认是更新步长过大之后再降 lr；否则降 lr 只是把崩溃变慢。

系统层常被忽略：rollout 与 learner 版本不一致，logprob 和采样政策对不上，$\rho$ 会疯。先对齐版本再调算法。有效 token 过少时，token-mean 和 seq-mean 的切换也会让 loss 尺度跳一档，看起来像震荡。

## 3. 什么时候震荡可以接受

组难度 mixed、每批有效组比例在变，训练 reward 本来就会抖。可接受的判据是 holdout success 单调或缓慢升、格式和安全不掉、NaN 为零、clip fraction 不长期打满、熵不崩、lag 不持续增大。仅移动平均会掩盖后者。我会把「可接受的抖」和「要停的崩」写成门禁，不追求光滑曲线。

## 追问

- **Advantage whitening 会不会制造震荡？** 会。小 $G$ 上 $\sigma$ 很噪，可改成跨 batch 滑动 $\sigma$，或过滤零方差组。
- **先修 reward 还是先修 loss？** 先确认同一轨迹重打分一致，再谈优化器。尺子在抖，政策梯度没有意义。
- **和学习率的关系？** 复现确认步长过大再降；否则先查 verifier、lag、归一化。
- **DAPO / 动态采样能治震荡吗？** 能减少零方差组造成的假梯度，但治不了 parser 不稳和版本 lag。对症才换算法。
