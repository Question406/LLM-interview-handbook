---
id: dt-onpolicy-pref
section: labs
order: 17
level: S
title: Tulu 3 / 迭代 DPO：离线偏好对过期了怎么办？
quick: "用当前模型重新采样。可验证任务在线生成回答、用规则奖励评分；主观偏好定期用当前策略重采，由人或校准过的 judge 标注。原因是旧偏好对来自旧策略，覆盖不到模型现在会写的回答。直接下载 UltraFeedback 这类现成偏好集来训，监督的是别的模型的回答分布。"
companies:
  - apple
tags:
  - AllenAI
  - DPO
  - Preference
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Tulu 3: Pushing Frontiers in Open Language Model Post-Training"
    url: https://arxiv.org/abs/2411.15124
    type: primary
  - title: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

离线偏好对过期了，就用当前模型重新采。具体是用当前 checkpoint，或上一轮 SFT 模型，对同一批 prompt 各生成 $k$ 个回答，再重新比较好坏。DPO 虽然没有显式奖励模型，同样有这个问题：用两年前的教师回答训练今天的模型，一样会遇到数据过期。

## 为什么离线对会过期

离线对来自旧策略 $\mu$。$\pi_\theta$ 训练几步之后，梯度还在拉大这些旧 $y_w,y_l$ 之间的间隔，而它现在实际会写出来的 $y$ 却没有得到监督。隐式奖励 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$ 在数据没有覆盖的区域也没有校准。`dt-reward-pref` 提过离线对和线上分布错位，这张卡把它展开成具体的数据动作。

## 怎么做 on-policy 迭代

1. **重采。** 用当前策略对同一批 prompt 各生成 $k$ 个回答。
2. **打分。** 能验证的任务按规则比较好坏；主观任务由人或校准过的 judge 评分。
3. **训练。** 这一轮 DPO 的 $\pi_{\mathrm{ref}}$ 固定为本轮开始时的策略，进入下一轮再换 ref。
4. **停止。** 冻结人评和产品切片上的边际 $\Delta$ 走平，或者长度、套话开始上升，就停。造了多少对说明不了模型有没有变好。

Tulu 3 是公开的参照：用当前的 Tulu-3-SFT 和其他模型对同一输入提示生成回答，GPT-4o 按有用、指令跟随、诚实、真实四项打 1 到 5 分，共约 35.4 万条偏好，8B 的公开 mix 约 27.3 万对；训练用长度归一的 DPO，最后再接基于可验证奖励的强化学习（RLVR）。Tulu 混了一部分 off-policy 数据（其他模型的回答），混进来的价值在于多样性，替代不了 on-policy。公开消融也显示，chosen 质量本身低的话，再混 on-policy 几乎不涨。他们优先做长度归一，没有改上 PPO，见 `dt-length-hack-data`。35 万是论文里的数，换任务要按自己的评测定规模。

## 实践中的变化

可验证任务和主观任务的刷新方式不一样。数学、代码这类有规则奖励的任务本身就是在线的：当前策略采样，执行后给出 $r$。AFM 2025 报告公开的做法也是这样，用人偏好训奖励模型（RM）再做 RLOO，数学和视觉 STEM 用规则奖励。摘要这类主观任务没有自动的在线信号，需要定期用当前策略重采，再由人来标。

## 追问

- **只刷新 rejected，chosen 仍用教师的回答行不行？** 能缓解一点暴露偏差。但 chosen 也过期时，模型是在学「模仿一个它写不出来的老师」。
- **和拒绝采样什么关系？** 拒绝采样留下的是做 SFT 的正例；这题留下的是同一输入提示上回答之间的排序。两者可以共用一次采样。
