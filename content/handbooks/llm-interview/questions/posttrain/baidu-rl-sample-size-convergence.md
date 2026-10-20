---
id: baidu-rl-sample-size-convergence
section: posttrain
order: 104
level: S
title: 百度实习：RL 样本量如何影响收敛速度，应怎样选择？
quick: "更多样本通常能降低梯度估计方差，但会增加采样成本；等到更新时，采样策略也可能已经过旧。要统计有效 token、有效组、任务覆盖和奖励信噪比。在固定计算预算下比较学习曲线、成功率、方差和实际耗时，再调整组大小、批量大小、更新频率和任务难度。"
tags:
  - Baidu
  - RL Training
  - Sample Efficiency
  - Convergence
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百度大模型算法二面分享 日常实习（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/4a09c3e284c74aad953bb8df4217fb7e
    type: candidate-first-hand
---

## 真题记录

- 公司：百度
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：日常实习；二面
- 面试时间：原帖未披露；帖子发布于 2026-04-18
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、实习性质、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“强化学习的样本量是多少？在强化学习训练中，样本量的选择是否影响到模型的收敛速度？如果有，如何应对？”**

这块容易报一个固定条数，或者说「batch 越大收敛越快」。样本量影响梯度方差和探索，但没有跨任务标准答案。对 GRPO / 可验证奖励强化学习（RLVR），必须分别统计：输入提示数、每个提示的组大小 $n$、组内奖励不全相同的有效组比例、有效 token 数、序列长度、奖励方差。只增加大量重复的零分轨迹，不等于增加有效数据。$n=1$ 时 GRPO 的组相对优势未定义，见 `sys-rl-group-n`，再大的 batch 也救不了估计器。我会说「用固定计算预算比过 learning curve」，不背某个神奇 batch。

## 条数、有效组、staleness 三本账

较大的 update batch 通常降低一步梯度的方差，却拉长采样周期：异步 actor-learner 里 policy lag 变大，$\rho=\pi_\theta/\pi_{\mathrm{old}}$ 的方差和 clip fraction 上升。实际耗时往往主要花在逐 token 生成（decode）上，因为一步轨迹数 $=\text{prompt batch}\times n$，近似线性涨。收敛应看每 GPU 小时的 holdout 成功，不是每步看见多少条。零方差组 $\hat A=0$，消耗算力却没有学习信号；DAPO 动态采样增加的是有效组，不是名义 $n$。信噪比差时可以加 $n$、做 advantage normalization、按难度分层；成功极其稀疏时，先调整任务难度、冷启动数据和验证器，不要无限堆样本。轨迹过期时缩短 collect-to-update，必要时用 CISPO 一类受控 IS，见 `pt-cispo`，而不是把 batch 再翻倍把过期梯度平均掉。

## 固定预算画两条曲线

保持总模型调用或总 token 可比，同时画学习曲线和 wall-clock 曲线：holdout success、回报方差、反向 $D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}})$、熵、单位成功成本，见 `fund-kl-directions`。合适的参数范围要用可复现的消融实验确定。数学题 $n$ 常见 8 到 16：从 8 到 16 常能多抓到对错混合；从 16 到 64 边际上多半是重复模式，实际耗时按 decode 涨。先看日志里非零优势组占比，再决定加 $n$ 还是加题数。不要把「我把 global batch 开到 4k」当成做过 RL，先报有效组、平均长度、一步实际耗时和 stale 比例。DPO 若出现在同一项目里，样本按 pair 覆盖的失败模式计，不要和 GRPO 轨迹横比条数。

## 追问

- **$n$ 和 `train_batch_size` 哪个先加？** 有效组比例低，先加 $n$、升温或降难度、开动态采样；有效组已经够、更新仍噪，再加题数。不要两个一起拧。
- **样本越多越快收敛吗？** 步数上看方差会降，实际耗时上常常更慢，因为 decode 和 staleness 涨了。
- **DPO 怎么数样本？** 数 pair 覆盖了哪些失败，不是和 GRPO 的 $n$ 条轨迹比「谁数据多」。
- **全零分要不要留着凑 batch？** GRPO 里它们是零梯度，RS 里是空集。都该改难度或过滤，不是加学习率。
- **异步大 batch 的第一手段？** 缩短队列和最大 policy age，监控 ratio；CISPO 用于校正旧策略采样的偏差，不能无限放宽轨迹的新鲜度要求，见 `pt-cispo`。
