---
id: ali-ppo-dpo-grpo-ask
section: posttrain
order: 15
level: S
title: PPO 和 DPO 的主要区别？DPO 注意点？用过 GRPO 吗？
quick: "DPO 直接用偏好对更新策略，不需要显式 RM 和在线采样循环；PPO 通常先训 RM 再用当前策略采样优化，能用更复杂的奖励，系统成本也更高。DPO 要注意偏好噪声和分布过度集中；GRPO 用同一道题多个回答的相对得分更新策略，省掉了 Critic。"
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
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

主要差在监督信号，以及是不是 on-policy。直接偏好优化（DPO）拿偏好对直接优化策略，没有显式的奖励模型（RM）和强化学习（RL）循环；PPO 先训 RM 再 on-policy 优化，表达力强，但系统复杂；GRPO 用同一道题的组内相对奖励做 on-policy 更新，省掉了 Critic。三者各有适用的信号，「DPO 已经替代 PPO」这种说法站不住，也别把它们背成互不相关的名词。

| | DPO | PPO / 基于人类反馈的强化学习（RLHF） | GRPO |
| --- | --- | --- | --- |
| 数据 | preference pairs | 偏好 → RM + 采样轨迹（rollout） | 同题多样本 + 奖励分数（reward） / 验证器（verifier） |
| 复杂度 | 低 | 高（策略、参考、RM、常还有 critic） | 中（无 critic，要采样） |
| 风险 | 噪声敏感、缺探索 | 钻奖励模型的空子、不稳 | 空 group、credit 粗 |

DPO 把 Bradley-Terry 偏好写成关于 $\pi_\theta$ 和 $\pi_{\mathrm{ref}}$ 的分类目标，离线、稳定、省采样。PPO 能拟合更复杂的标量奖励，比如多目标加权、过程分，但要管 $\rho_t$ 的 clip、KL 和 value 漂移。GRPO 把 baseline 换成组均值，适合序列末尾才出分、同一输入提示能多次采样的 LLM 设定。白板推导见 `pt-pg-to-ppo-to-grpo`，Loss 展开见 `ali-grpo-loss`。

DPO 最该注意的是数据质量。标注者不一致、长度偏置、只因为「更礼貌」就判为更好的假偏好，都会让策略学错。Length bias 很常见，更长的回答更容易赢人评，模型就学会灌水。$\beta$ 太大会把分布贴死在 chosen 上，太小几乎不更新。还要检查 chosen 的有用性是不是真的提升了，光把 rejected 的概率压低不算数。离线对和线上分布错开以后，DPO 是在旧对比上拉新策略，收益会衰减。

被问「用过 GRPO 吗」，别只复述公式，要讲清楚：同一道题采 $G$ 条，组内标准化 advantage，没有 value model；空 group（全对 / 全错）梯度为 0；可验证任务比纯 RM 更合适。DPO 缺探索，PPO 重，GRPO 在中间，按信号选型，别按论文新旧堆 buzzword。阶段上仍然建议监督微调（SFT）→ 偏好 → 可验证 RL，见 `ali-sft-then-posttrain`；DPO 之后再接 GRPO 见 `ali-multineg-then-grpo`。

## 追问

**没有 RM 的 DPO 更安全吗？**
不见得。偏好噪声会直接进策略；没有 RM 不等于没有 hacking，只是 hacking 发生在标注和长度上。

**GRPO 能替代 PPO 吗？**
在 LLM 可验证奖励、组采样便宜的场景下常常更简单；需要逐步 credit 或稠密过程分时，critic / PPO 仍然有位置。

**DPO 的 $\beta$ 怎么调？**
看 chosen / rejected 的 margin、熵和下游任务，别固定抄 0.1。

**为什么先 DPO 再 GRPO？**
先用离线偏好压住格式和安全，再在 verifier 上探索。顺序反过来，DPO 可能把策略拉回旧分布。
