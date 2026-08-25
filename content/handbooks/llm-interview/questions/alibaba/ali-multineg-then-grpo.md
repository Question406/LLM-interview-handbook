---
id: ali-multineg-then-grpo
section: alibaba
order: 8
level: S
title: 淘天面经：单正多负 DPO 后，能否再接 GRPO？分类场景为何 DPO 常更稳？
quick: >-
  多负 DPO 主要学“正优于各负”，不保证学全负样本两两排序。DPO 压尖后可接 GRPO 做 on-policy
  探索，但要防分布过尖导致采样退化。分类/偏好清晰时 DPO 往往更稳、更省。
tags:
  - Alibaba
  - DPO
  - GRPO
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---

这块容易直接答成两句口号：「多负 DPO 已经学全排序，不必再 RL」或「DPO 后熵一定崩，不能接 GRPO」。多负 DPO 主要学「正优于各负」，不保证 rejected 之间的精细序。DPO 压尖后可以接 GRPO 做 on-policy 探索，但要先确认组内还能采出可被奖励分开的差异。分类 / 偏好清晰时 DPO 往往更稳、更省。接续诊断见 `pt-dpo-to-grpo`，三者对比见 `ali-ppo-dpo-grpo-ask`。

## 多负 DPO 学的是什么

单正多负通常把一条 chosen 对多条 rejected 做成多个 pair，或写成 listwise 变体。Bradley-Terry 目标拉高 $\pi_\theta(y_w\mid x)$、压低各 $y_l$，并不自动得到 $y_l$ 之间的序。若业务要「错误 A 比错误 B 更可接受」，需要更完整的 ranking 标注或额外约束，而不是假设多负已经给出全序。DPO 还可能把分布变尖：$\beta$ 大、负例太易、过拟合都会让采样多样性下降。这不是定理，要用 rollout 验证，不要口头断言熵。

## 接 GRPO 的条件

可以接，用来在可验证奖励上恢复探索。GRPO 吃的是同题组内相对优势

$$
\hat{A}_i=\frac{r_i-\mu}{\sigma+\epsilon}.
$$

若 DPO 后同题采样几乎相同，或一组全对 / 全错，则 $\sigma\approx 0$，相对信号消失。此时应先调温度 / 熵、减小学习率，或回退部分 SFT 数据，而不是加大步长硬推。组内 advantage 细节见 `ali-grpo-advantage`。Reference 锚点要说清：用 DPO checkpoint 还是更早的 SFT，KL 系数跟着变。

## 分类场景为何 DPO 更稳

标签边界清晰、偏好噪声低（意图分类、是否拒答、格式对错）时，离线偏好对通常比 on-policy RL 更稳、成本更低。GRPO 更吃 verifier 与采样质量：分类往往没有「多种正确轨迹」可探索，组方差天然小，RL 容易空转或刷格式。可验证的工具成功率、数学、代码才更配 GRPO。阶段顺序仍是 SFT 学协议，再 DPO 学偏好，需要探索再 RL，见 `ali-sft-then-posttrain`。

## 追问

- **多负等于 listwise 吗？** 不等于。多个 pair 只约束「正优于各负」，负例之间无直接梯度。
- **DPO 后一定不能 GRPO？** 不一定。看 `pass@k-pass@1` 与组内 reward std，不是看熵口号。
- **分类为何不用 GRPO？** 边界清晰时离线对更省；组内常全对或全错，相对优势没了。
- **负例怎么造？** 要 hard negative（近义错类），随机负例只会让模型学「别说废话」，学不到边界。
