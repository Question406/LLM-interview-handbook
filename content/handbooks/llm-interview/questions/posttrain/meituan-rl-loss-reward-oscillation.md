---
id: meituan-rl-loss-reward-oscillation
section: posttrain
order: 103
level: S
title: 美团：RL 过程中的 reward 或 loss 震荡严重，如何排查？
quick: "先分清是 reward 在跳还是 loss 在跳，再从数据、reward、策略、系统四层看任务成功率、奖励分布与方差、KL、熵、梯度范数、有效 token 数、策略版本滞后和 NaN。用固定种子在小规模环境复现，每次只改一个因素；平滑曲线和盲目降学习率都只会把问题盖住。"
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

我会先问两件事：震荡的是 reward 还是 loss，它有没有伤到最终 success。然后分层监控、单变量复现。很多「震荡」来自组间难度不齐或者 parser 偶尔出错，对曲线做滑动平均会把坏问题盖住，把学习率砍半也只是碰运气。GRPO 里优势要除以组内 $\sigma$，loss 比 reward 更抖是正常的，判断好坏要看 holdout success，别看 $L$。

监控按采样轨迹（rollout）版本、任务桶和长度来记：奖励均值和方差、有效组比例、pass@k、KL、entropy、clip fraction、advantage 标准差、梯度范数、NaN / overflow、actor 和 rollout 之间的 policy lag、有效 token 数。少一项，就不能说「已经排查过」。

接着定位是哪一层在跳。Reward 跳，常见原因是 parser 或验证器（verifier）不稳定（同一条轨迹重打分结果不一样）、数据混进了别的东西、长度分布变了，或者偶尔出现全对全错的组让 $\sigma$ 起伏。Loss 跳，常见原因是奖励尺度没对齐、长尾 token、学习率、batch 太小、分布式 all-reduce 的数值问题、$\rho$ 极端，或者 advantage whitening 在小 $G$ 上很噪。公式

$$
\hat{A}_i=\frac{r_i-\mu}{\sigma+\epsilon}
$$

会把「偶尔多一个对的」放大成巨大的优势，所以先确认 $r$ 的定义稳定，再去碰优化器。举个例子，reward 在跳、holdout 却很稳，可能只是 batch 的组成变了；loss 在跳还冒 NaN，那才是数值上的紧急情况。

复现时一次只关一个变量。固定输入提示（prompt）、seed、模型快照，在单机小 batch 上先把现象重现出来，然后逐项排：冻结数据和 verifier、固定温度、检查归一化 / whitening、缩小更新步长或加大有效 token batch、调 KL / clip / entropy、截断极端的 advantage。最后放回异步 pipeline，看 policy lag 会不会再次把稳定性打破。在异步大集群上同时改五个超参，永远不知道是哪个修好的。只有复现确认是更新步长过大，才去降 lr，否则降 lr 只是让崩溃来得慢一点。

系统层最容易被忽略。rollout 和 learner 版本不一致，logprob 和采样策略对不上，$\rho$ 就会乱跳，所以先对齐版本，再调算法。有效 token 太少时，token-mean 和 seq-mean 一切换，loss 尺度也会跳一档，看起来像震荡。

也有震荡是可以接受的。组难度本来就是混合的，每批有效组比例在变，训练 reward 本来就会抖。可接受的标准是：holdout success 单调或缓慢上升、格式和安全不掉、NaN 为零、clip fraction 没有长期打满、熵没崩、lag 没有持续变大。光做移动平均会把后面这几项盖住。我会把「可以接受的抖」和「必须停的崩」写成门禁，不追求一条光滑的曲线。

## 追问

**Advantage whitening 会不会制造震荡？**
会。小 $G$ 上 $\sigma$ 很噪，可以改成跨 batch 的滑动 $\sigma$，或者过滤零方差组。

**先修 reward 还是先修 loss？**
先确认同一条轨迹重打分一致，再谈优化器。尺子本身在抖，策略梯度就没有意义。

**和学习率是什么关系？**
复现确认步长过大再降，否则先查 verifier、lag 和归一化。

**DAPO / 动态采样能治震荡吗？**
能减少零方差组造成的假梯度，治不了 parser 不稳和版本 lag。对上症状再换算法。
