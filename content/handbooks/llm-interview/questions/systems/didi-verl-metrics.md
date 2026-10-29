---
id: didi-verl-metrics
section: systems
order: 234
level: A
title: 滴滴一面：用 veRL 做 RL 时，看哪些指标判断训练在走？
quick: >-
  policy loss 说明不了训练在走。我会分三桶看：任务桶看 reward 和正确率；策略桶看到 $\pi_{\mathrm{ref}}$ 的
  KL、熵、clip fraction、回复长度和组内奖励方差；系统桶看引擎有没有在干活。loss 降了但 KL 炸、长度暴涨，多半是在 hacking
  或者数值不对。评测看 holdout Pass@$k$，不看训练组。
tags:
  - Didi
  - VeRL
  - Metrics
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 滴滴RL实习生面经
    url: 'https://www.nowcoder.com/discuss/813460704786202624'
    type: candidate-first-hand
  - title: verl
    url: 'https://github.com/verl-project/verl'
    type: primary
---

## 真题记录

- 公司：滴滴
- 岗位：RL 实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“在用 verl 做 RL 时，你是根据什么指标来查看训练的进度的。”**

我会同时看三桶指标：任务有没有变好、策略有没有漂、引擎有没有在干活，进度最终以 holdout Pass@$k$ 为准，当前训练组的平均 reward 只作参考。只报 policy loss 下降是不够的。PPO/GRPO 里 loss 几乎不能单独当进度看，clip 之后 loss 变小，可能只是 ratio 被卡住了，也可能是在刷长度。

先说任务桶，看是不是真的更会做了。验证器（verifier）正确率、格式合法率、工具成功率，都按难度切片，免得易题把均值拉满。训练组 reward 在涨、holdout 不动，多半是泄漏、overfitting 或者 hacking。GRPO 还要看有效 group 的比例：全对或全错的组没有优势信号，算力等于空转。事实类和代码类任务，要把「能解析但答错」和「格式崩了」分开统计，不然会把崩格式误判成不会做题。veRL 里这些数一般从 reward manager 打出来，别只盯 actor loss 的面板。

策略桶看 KL 到 $\pi_{\mathrm{ref}}$、熵、clip fraction、advantage 标准差和序列长度。几种典型的组合可以直接下判断：KL$\approx 0$ 且 reward 不动，就是没学到东西；KL 陡升、回答越来越长、内容是空话，说明护栏不够或者在刷长度；clipfrac 长期为 0，要查是不是一步就更新完了、ratio 恒为 1，比如 logp 没重算、数据没对上；熵崩了，就回头查 clip、温度，或者 KL 是不是去得太早。veRL 的日志通常带 `actor/`、`critic/`、`timing/` 前缀，汇报时把 reward 和 KL 画成双轴图，比报一个 loss 像真练过。

系统桶看引擎是不是在干活：sampling 轨迹（rollout）的 tokens/s、等工具的时间、重算 logp 的占比、OOM 和 drop-last、GPU idle。长尾 group 会让利用率很差，见 `byte-grpo-rollout-tail-gpu`。系统指标差的时候先修调度，再去解释算法为什么不收敛。

所以一次 standup 我最少带三张图：holdout 正确率、KL 和长度、rollout tokens/s，不会只贴一条 loss 曲线。能讲清这三桶，比背得出 veRL 的配置项更像真的训过。

## 追问

**为什么 loss 不能当主指标？**
优化的目标是期望回报，clipped surrogate 这个标量没有单调的含义。

**KL 多少算健康？**
没有通用阈值，要和 reward、长度一起看趋势；突变比绝对值更危险。

**组内奖励方差为 0 怎么办？**
换难度或者做动态 sampling，否则 GRPO 的更新就是零。见 `tencent-teg-grpo-when-bad`。

**怎么避免被训练 reward 骗？**
固定 holdout，定期人工抽检 hacking 模式，比如超长、重复、空实现。看板上把训练 reward 和 holdout 画在一起，一分叉就停。

相关：`byte-verl-structure`、`pt-grpo-variance`、`meituan-rl-loss-reward-oscillation`
