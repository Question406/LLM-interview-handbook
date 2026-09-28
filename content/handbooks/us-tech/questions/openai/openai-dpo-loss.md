---
id: openai-dpo-loss
section: openai
order: 10
level: S
title: OpenAI：DPO 相对 PPO 少了什么，implicit reward 怎么说
quick: >-
  DPO 把「RM + 反向 KL 约束」解析掉，实现上不再训奖励模型、不再 on-policy rollout、没有 critic 和 PPO
  clip。隐式奖励是 $r(x,y)=\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$。少的是 RL 套件，不是少了 KL 先验。
tags:
  - OpenAI
  - DPO
  - RLHF
  - Preference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题怎么来的

OpenAI 公开对齐主线是 InstructGPT 的 PPO-RLHF。DPO 不是 OpenAI 的论文，但 Research / 对齐岗会拿它当对照：「既然 KL 约束的最优策略有闭式，为什么还要 RL」。我会按 DPO 原文把 implicit reward 写出来，再对照 `openai-instructgpt-kl` 和 `openai-ppo-clip`。不要假装自己在某次 onsite 抽到了这道原题。

## PPO 环里有什么，DPO 砍掉什么

InstructGPT 式 PPO 要：偏好数据 $\to$ 奖励模型 $r_\phi$ $\to$ 当前策略采样 $\to$ 减 ref KL 的奖励 $\to$ GAE / value $\to$ clip 更新。在线、贵、脆，ratio 还可能炸。

KL 约束的 RLHF 目标是

$$
\max_\pi\ \mathbb{E}_{y\sim\pi}[r(x,y)]-\beta D_{\mathrm{KL}}(\pi\|\pi_{\mathrm{ref}}).
$$

最优策略满足 $r(x,y)=\beta\log(\pi^*(y\mid x)/\pi_{\mathrm{ref}}(y\mid x))+Z(x)$。DPO 把这个 $r$ 反代回 Bradley-Terry：

$$
p(y_w\succ y_l\mid x)=\sigma\big(r(x,y_w)-r(x,y_l)\big),
$$

$Z(x)$ 消掉，得到

$$
\mathcal{L}_{\mathrm{DPO}}=-\log\sigma\Big(\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\Big).
$$

所以相对 PPO 少了：显式 RM、on-policy 采样循环、value / GAE、PPO clip。没少：偏好对、冻结的 $\pi_{\mathrm{ref}}$、$\beta$ 这颗温度。说「DPO 没有 KL」是错的；KL 进了最优策略的解析式，代码里变成对 ref 的 log 比。

隐式奖励怎么说：不是又训了一个打分头。它是「当前策略相对 SFT 愿意把多少 log-mass 分给这句话」。$\beta$ 大，策略不敢离开 ref；$\beta$ 小，偏好对的间隔被放大，容易过拟合那批 chosen/rejected。

## 我会主动报的失败模式

- **off-policy。** 偏好数据若来自旧策略，而 $\pi_\theta$ 已经走远，BT 在隐式 $r$ 上的假设变差。PPO 至少在当前 $\pi$ 上采样。DPO 要定期换数据，或拿 online / iterative DPO。
- **长度。** log 比沿 token 加，长回答容易赢。可以归一化长度，或在数据里控制 chosen/rejected 长度。
- **ref 必须冻。** 把 $\pi_{\mathrm{ref}}$ 跟着 $\theta$ 跑，隐式 KL 锚就没了。
- **没有 RM 不等于没有 hacking。** 模型可以刷标注员偏好里的表面特征。CAI 那条人写原则的对照见 `anthropic-constitutional-ai`。

实现：loss 在 log 空间算 $\Delta$，`logsigmoid`；不要先 exp 再减。评测仍要一套不在偏好集里的 eval，见 `openai-eval-harness`。

## 追问

- **还要 PPO clip 吗？** 标准 DPO 不要。$\beta$ 和 ref 已经在管步长。有人加 DPOP / hinge，那是变体。
- **implicit reward 能当 RM 用吗？** 能打偏好对的分数差，但不保证绝对尺度，也不能直接当 best-of-n 的黄金 RM。
- **和 InstructGPT 三阶段？** DPO 通常接在 SFT 后，替换 RM+PPO。SFT 还在，否则 $\pi_{\mathrm{ref}}$ 太弱。
- **为什么面试还要会 PPO？** 因为 OpenAI 原设定、在线探索、过程奖励、工具调用 RL，DPO 闭式罩不住。
