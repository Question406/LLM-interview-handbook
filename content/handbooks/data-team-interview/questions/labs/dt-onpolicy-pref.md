---
id: dt-onpolicy-pref
section: labs
order: 17
level: S
title: Tulu 3 / 迭代 DPO：离线偏好对过期了怎么办？
quick: "可验证任务用当前模型在线生成回答，再用规则奖励评分。主观偏好也要定期重新生成，由人或校准过的 judge 标注。旧偏好对可能已不能覆盖模型现在的回答；不能下载 UltraFeedback 就直接拿来训练，也不能默认使用用户线上改写。"
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

用当前 checkpoint，或上一轮 SFT 模型，对同一批 prompt 各生成 $k$ 个回答。能验证的任务按规则比较好坏，主观任务由人或校准过的 judge 评分。这一轮 直接偏好优化（DPO） 的 $\pi_{\mathrm{ref}}$ 钉在这一轮开始的策略，换轮再换 ref。停的条件是冻结人评和产品切片的边际 $\Delta$ 平了，或长度 / 套话升了，不要按「又造了多少对」停。

不这么选的理由：用两年前的教师回答训练今天的模型，同样会遇到数据过期；DPO 不使用显式奖励模型，并不能消除这个问题。离线对来自旧策略 $\mu$。$\pi_\theta$ 训练几步之后，梯度还在拉宽这些旧 $y_w,y_l$ 的间隔，对它现在会写的 $y$ 没有监督。隐式奖励 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$ 在数据没覆盖的区域没有校准。`dt-reward-pref` 提过 offline 对和线上分布错位，这张卡把它展开成数据动作。

接到苹果：AFM 公开是人偏好训 奖励模型（RM），再 RLOO；数学 / 视觉 STEM 走规则奖励。规则奖励本身就是在线的：当前策略采样，执行给 $r$。主观摘要、通知口吻没有这条，要定期用当前端侧 / PCC 策略重采，人标。用户线上改写默认不能当 on-policy 对，见 `dt-userlog-contrast`。Tulu 混了一部分 off-policy（别的模型的回答），混的价值是多样，替代不了 on-policy。低质 chosen 上再混 on-policy，公开消融几乎不涨。长度归一他们优先于上 PPO，见 `dt-length-hack-data`。Tulu 的 35 万是论文数，不是内部配额。

公开锚点：Tulu 3 用当前 Tulu-3-SFT 和别的模型对同一输入提示 出回答，GPT-4o 按有用 / 指令跟随 / 诚实 / 真实打 1 到 5；约 35.4 万条偏好，8B 公开 mix 约 27.3 万对，长度归一 DPO，最后再上 基于可验证奖励的强化学习（RLVR）。

## 追问

- **只刷新 rejected、chosen 仍用教师？** 能缓解一点暴露偏差。chosen 也过期时，模型在学「模仿一个它写不出来的老师」。
- **几轮停？** 冻结人评和产品切片的边际 $\Delta$ 平了，或长度 / 套话升了。不要按「又造了多少对」停。
- **和拒绝采样什么关系？** 拒绝采样留的是正例 SFT。本题留的是同一输入提示 上的序。两条可以共用一次采样。
