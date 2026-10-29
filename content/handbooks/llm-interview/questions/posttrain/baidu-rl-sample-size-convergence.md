---
id: baidu-rl-sample-size-convergence
section: posttrain
order: 104
level: S
title: 百度实习：RL 样本量如何影响收敛速度，应怎样选择？
quick: >-
  会影响，但没有跨任务的标准条数：样本多通常能降低梯度估计方差，代价是 sampling 更贵，等到更新时 sampling 策略也可能已经过旧。要统计有效
  token、有效组、任务覆盖和奖励信噪比，在固定计算预算下比较学习曲线、成功率、方差和实际耗时，再调组大小、批量大小、更新频率和任务难度。
tags:
  - Baidu
  - RL Training
  - Sample Efficiency
  - Convergence
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 百度大模型算法二面分享 日常实习（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/4a09c3e284c74aad953bb8df4217fb7e'
    type: candidate-first-hand
---

## 真题记录

- 公司：百度
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：日常实习；二面
- 面试时间：原帖未披露；帖子发布于 2026-04-18
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、实习性质、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“RL 的样本量是多少？在 RL 训练中，样本量的选择是否影响到模型的收敛速度？如果有，如何应对？”**

会影响，但没有一个跨任务的标准条数。样本多一般能降低一步梯度的方差、多一些探索，代价是 sampling 周期拉长、策略更容易过期，实际耗时不一定更短。所以我不报某个神奇的 batch，而是在固定计算预算下比学习曲线，再调组大小、batch、更新频率和任务难度。「batch 越大收敛越快」这种说法不成立。

先把样本量拆开数。对 GRPO / 可验证奖励 RL（RLVR），要分别统计：prompt 数、每个提示的组大小 $n$、组内奖励不全相同的有效组比例、有效 token 数、序列长度、奖励方差。比如加了一大批题，模型全都做错，batch 看着变大了，其实多出来的全是重复的零分轨迹，有效数据一点没多。$n=1$ 时 GRPO 的组相对优势没有定义，见 `sys-rl-group-n`，batch 再大也救不了估计器。

为什么大 batch 不一定收敛快？更大的 update batch 通常让一步梯度的方差更低，但 sampling 周期变长：异步 actor-learner 里 policy lag 变大，$\rho=\pi_\theta/\pi_{\mathrm{old}}$ 的方差和 clip fraction 跟着上升。实际耗时往往主要花在逐 token 生成（decode）上，因为一步的轨迹数 $=\text{prompt batch}\times n$，近似线性涨。所以收敛要看每 GPU 小时的 holdout 成功率，别看每一步见了多少条。零方差组 $\hat A=0$，花了算力却没有学习信号；DAPO 的动态 sampling 增加的是有效组，不是名义上的 $n$。

怎么应对，按病因来。信噪比差，可以加 $n$、做 advantage normalization、按难度分层。成功极其稀疏，先调任务难度、冷启动数据和验证器，别无限堆样本。轨迹过期，缩短 collect-to-update，必要时用 CISPO 这类受控 IS，见 `pt-cispo`，把 batch 翻倍只会把过期梯度平均进去。

验证要画两条曲线。保持总模型调用或总 token 可比，同时画学习曲线和 wall-clock 曲线，看 holdout success、回报方差、反向 $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$、熵和单位成功成本，见 `fund-kl-directions`。合适的参数范围要靠可复现的 ablation study 来定。数学题的 $n$ 常见 8 到 16：从 8 加到 16 常能多抓到对错混合；从 16 加到 64，边际上多半是重复模式，耗时却按 decode 涨。所以先看日志里非零优势组的占比，再决定加 $n$ 还是加题数。「我把 global batch 开到 4k」不算做过 RL，要先报有效组、平均长度、一步的实际耗时和 stale 比例。同一项目里要是还有 DPO，样本按 pair 覆盖了哪些失败模式来算，别和 GRPO 的轨迹横着比条数。

## 追问

**$n$ 和 `train_batch_size` 先加哪个？**
有效组比例低，先加 $n$、升温或降难度、开动态 sampling；有效组够了、更新还噪，再加题数。别两个一起拧。

**样本越多收敛越快吗？**
按步数看方差会降，按实际耗时看常常更慢，因为 decode 和 staleness 都涨了。

**DPO 的样本怎么数？**
数 pair 覆盖了哪些失败，别和 GRPO 的 $n$ 条轨迹比谁的数据多。

**全零分的轨迹要不要留着凑 batch？**
不用。GRPO 里它们是零梯度，RS 里是空集，都该改难度或者过滤，加学习率没用。

**异步大 batch，第一步先做什么？**
缩短队列和最大 policy age，盯着 ratio。CISPO 用来校正旧策略 sampling 的偏差，不能拿它无限放宽对轨迹新鲜度的要求，见 `pt-cispo`。
