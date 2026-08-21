---
id: didi-verl-metrics
section: systems
order: 234
level: A
title: 滴滴一面：用 veRL 做 RL 时，看哪些指标判断训练在走？
quick: >-
  不要只看 policy loss。一组最低配：reward / 正确率、KL 到 $\pi_{\mathrm{ref}}$、熵、clip
  fraction、回复长度、组内奖励方差。loss 降而 KL 炸、长度暴涨，多半在 hacking 或数值不对。评测用 holdout
  Pass@$k$，不看训练组。
tags:
  - Didi
  - VeRL
  - Metrics
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 滴滴RL实习生面经
    url: https://www.nowcoder.com/discuss/813460704786202624
    type: candidate-first-hand
  - title: verl
    url: https://github.com/verl-project/verl
    type: primary
---

## 真题记录

- 公司：滴滴
- 岗位：RL 实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“在用verl做强化学习时，你是根据什么指标来查看训练的进度的。”**

滴滴 RL 实习一面这题，最容易只报 policy loss 下降。Loss 在 PPO/GRPO 里几乎不能单独当进度：clip 之后 loss 变小可能只是 ratio 被卡住，或在刷长度。最低配要同时看任务有没有变好、策略有没有漂、引擎有没有在干活。评测用 holdout Pass@$k$，不要看当前训练组的平均 reward。相关卡：`byte-verl-structure`、`pt-grpo-variance`、`meituan-rl-loss-reward-oscillation`。会看这三桶，比会背 veRL 配置项更像真的训过。

## 任务桶：是不是真的更会做

verifier 正确率、格式合法率、工具成功率；按难度切片，避免易题把均值拉满。训练组 reward 涨而 holdout 不动，多半泄漏、过拟合或 hacking。GRPO 还要看有效 group 比例：全对全错组没有优势，算力打在空转上。事实 / 代码任务把「可解析但错」和「格式崩」分开，否则会把崩格式当成不会做题。veRL 里这些数通常从 reward manager 打出来，不要只盯 actor loss 面板。

## 策略桶：KL、熵、clip、长度

KL 到 $\pi_{\mathrm{ref}}$、熵、clip fraction、advantage 标准差、序列长度。KL$\approx 0$ 且 reward 不动 = 没学到；KL 陡升 + 变长空话 = 护栏不够或在刷长度。clipfrac 长期为 0 要查是不是一步就更新完、ratio 恒为 1（logp 没重算、数据没对上）。熵崩要回到 clip / 温度 / 去 KL 是否过早。veRL 日志常带 `actor/`、`critic/`、`timing/` 前缀；汇报画 reward 与 KL 双轴，比报一个 loss 像练过。

## 系统桶：引擎是否在干活

rollout tokens/s、等待工具时间、重算 logp 占比、OOM / drop-last、GPU idle。长尾 group 会让利用率很差，见 `byte-grpo-rollout-tail-gpu`。系统指标差时先修调度，再解释算法不收敛。一次 standup 最少带三张图：holdout 正确率、KL 与长度、rollout tokens/s，避免只贴 loss 曲线。

## 追问

- **为什么 loss 不能当主指标？** 目标是期望回报；clipped surrogate 的标量没有单调含义。
- **KL 多少算健康？** 没有通用阈值，要和 reward、长度一起看趋势；突变比绝对值更危险。
- **组内奖励方差为 0 怎么办？** 换难度或动态采样，否则 GRPO 更新为零。见 `tencent-teg-grpo-when-bad`。
- **如何避免被训练 reward 骗？** 固定 holdout、定期人工抽检 hacking 模式（超长、重复、空实现）。指标看板要把训练 reward 和 holdout 画在一起，分叉立刻停。
