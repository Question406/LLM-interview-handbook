---
id: dt-onpolicy-pref
section: labs
order: 17
level: S
title: Tulu 3 / 迭代 DPO：离线 preference pairs 过期了怎么办？
quick: >-
  用当前模型重新 sampling，再重新比较好坏。旧 preference pairs 来自 old policy，模型现在会写的回答没人监督；直接拿
  UltraFeedback 这类现成偏好集来训，监督的是别的模型的回答分布。可验证任务在线 sampling、用 rule-based reward
  评分，主观偏好定期用 current policy 重采，交给人或 经过 calibration 的 judge 标。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'Tulu 3: Pushing Frontiers in Open Language Model Post-Training'
    url: 'https://arxiv.org/abs/2411.15124'
    type: primary
  - title: >-
      Direct Preference Optimization: Your Language Model is Secretly a Reward
      Model
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

离线 preference pairs 过期了，就用当前模型重新采：拿当前 checkpoint 或上一轮 SFT 模型，对同一批 prompt 各生成 $k$ 个回答，再重新比较好坏。DPO 没有显式 reward model，也躲不开这个问题，用两年前的 teacher 回答训练今天的模型，数据一样是过期的。

比如偏好集里的 chosen 和 rejected 都是一个旧模型写的，当前模型训了几轮后已经换了一种写法，新写法在数据里一条都没有，好不好也就没人告诉它。说得严格一点，离线对来自 old policy $\mu$，$\pi_\theta$ 训几步之后，gradient 还在拉大这些旧 $y_w,y_l$ 之间的间隔，它现在实际会写出来的 $y$ 却得不到监督。隐式奖励 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$ 在数据没覆盖的区域也没 calibration 过。`dt-reward-pref` 讲过离线对和线上分布错位，这张卡讲落到数据上具体怎么做。

做法是一轮一轮来。每一轮先用 current policy 对同一批 prompt 重采 $k$ 个回答，能验证的任务按规则比较好坏，主观任务交给人或 经过 calibration 的 judge 打分。训练时，这一轮 DPO 的 $\pi_{\mathrm{ref}}$ 固定成本轮开始时的策略，进下一轮再换 ref。什么时候停，看冻结 human evaluation 和产品 evaluation slices 上的边际 $\Delta$：走平了，或者长度、套话开始往上走，就停。造了多少对说明不了模型有没有变好。

Tulu 3 是现成的公开参照。他们用当前的 Tulu-3-SFT 和其他模型对同一输入生成回答，GPT-4o 按有用、instruction following、诚实、真实四项打 1 到 5 分，一共约 35.4 万条偏好，8B 的公开 mix 约 27.3 万对；训练用长度归一的 DPO，最后再接基于 verifiable reward 的 RL（RLVR）。35 万是论文里的数，换个任务要按自己的评测来定规模。

## 追问

**Tulu 3 也混了别的模型的回答，off-policy 数据还要不要？**
可以混，混进来的价值在多样性，替代不了 on-policy。公开 ablation study 还显示，chosen 本身质量低的话，再混 on-policy 几乎不涨。

**Tulu 3 为什么用长度归一的 DPO，没改上 PPO？**
他们优先做了长度归一，没有换成 PPO。长度怎么在数据侧控制，见 `dt-length-hack-data`。

**数学、代码这类任务也要定期重采吗？**
不用专门安排，它们本来就是在线的：current policy sampling，执行后给出 $r$。AFM 2025 报告公开的做法也是这样，用人偏好训 reward model（RM）再做 RLOO，数学和视觉 STEM 用 rule-based reward。摘要这类主观任务没有自动的在线信号，才需要定期用 current policy 重采，再请人来标。

**只刷新 rejected，chosen 还用 teacher 的回答行不行？**
能缓解一点 exposure bias。可 chosen 也过期了的话，模型是在学着模仿一个它写不出来的老师。

**这和 rejection sampling 是什么关系？**
rejection sampling 留下的是做 SFT 的正例，这里留下的是同一输入上几个回答之间的排序。两者可以共用一次 sampling。
