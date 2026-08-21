---
id: ali-ppo-dpo-grpo-ask
section: alibaba
order: 15
level: S
title: PPO 和 DPO 的主要区别？DPO 注意点？用过 GRPO 吗？
quick: >-
  DPO 用偏好对直接优化策略，无显式 RM/RL loop；PPO 先 RM 再 on-policy 优化，表达力强但复杂。DPO
  怕噪声偏好与分布过尖；GRPO 用组内相对奖励做 on-policy 更新。
tags:
  - Alibaba
  - DPO
  - GRPO
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

陷阱是把三者背成互不相关的名词，或宣称「DPO 已经替代 PPO」。差别在监督信号与是否 on-policy。DPO 用偏好对直接优化策略，无显式 RM / RL loop；PPO 先训 RM 再 on-policy 优化，表达力强但复杂；GRPO 用同题组内相对奖励做 on-policy 更新，省掉 critic。白板推导见 `pt-pg-to-ppo-to-grpo`，DPO 后再接 GRPO 见 `ali-multineg-then-grpo`。

## 三条路差在监督信号

| | DPO | PPO / RLHF | GRPO |
| --- | --- | --- | --- |
| 数据 | preference pairs | 偏好 → RM + rollout | 同题多样本 + reward / verifier |
| 复杂度 | 低 | 高（策略、参考、RM、常还有 critic） | 中（无 critic，要采样） |
| 风险 | 噪声敏感、缺探索 | RM hacking、不稳 | 空 group、credit 粗 |

DPO 把 Bradley-Terry 偏好写成对 $\pi_\theta$ 与 $\pi_{\mathrm{ref}}$ 的分类目标，离线、稳定、省采样。PPO 能拟合更复杂的标量奖励（多目标加权、过程分），但要管 $\rho_t$ clip、KL、value 漂移。GRPO 把 baseline 换成组均值，适合序列末才出分、同 prompt 可多采样的 LLM 设定。Loss 展开见 `ali-grpo-loss`。

## DPO 的注意点

数据质量第一：标注者不一致、长度偏置、只靠「更礼貌」的假偏好，都会让策略学错。$\beta$ 太大把分布贴死在 chosen 上，太小则几乎不更新。要检查是否真提升 chosen 的**有用性**，而不只是压低 rejected 的概率。Length bias 很常见：更长的回答更容易赢人评，模型学会灌水。离线对与线上分布错位后，DPO 会在旧对比上拉新策略，收益衰减。

## GRPO 补的是探索

「用过 GRPO 吗」不要只复述公式。讲：同题采 $G$ 条，组内标准化 advantage，无 value model；空 group（全对 / 全错）梯度为 0；可验证任务比纯 RM 更合适。DPO 缺探索、PPO 重、GRPO 在中间——按信号选型，不是按论文新旧堆 buzzword。阶段仍建议 SFT → 偏好 → 可验证 RL，见 `ali-sft-then-posttrain`。

## 追问

- **没有 RM 的 DPO 更安全吗？** 偏好噪声会直接进策略；没有 RM 不等于没有 hacking，只是 hacking 发生在标注与长度上。
- **GRPO 能替代 PPO 吗？** 在 LLM 可验证奖励、组采样便宜时常常更简单；需要逐步 credit 或稠密过程分时，critic / PPO 仍有位置。
- **$\beta$ 怎么调？** 看 chosen/rejected margin、熵、下游任务，而不是固定抄 0.1。
- **为何先 DPO 再 GRPO？** 先用离线偏好压住格式与安全，再在 verifier 上探索；反过来 DPO 可能拉回旧分布。
