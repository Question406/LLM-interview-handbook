---
id: ali-grpo-vs-sft
section: alibaba
order: 2
level: S
title: 阿里国际算法面：为什么选 GRPO 而不是继续 SFT / 蒸馏？
quick: SFT 适合教格式与示范轨迹；蒸馏适合逼近 teacher 分布；GRPO 适合有可验证/可打分目标、需要探索与相对优势更新时。选型看信号类型，不是谁更新。
tags:
  - Alibaba
  - GRPO
  - SFT
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
---

陷阱是按「谁更新」站队：GRPO 更新、SFT 落伍。阿里国际算法面开场常问技术选型：**看信号类型**。SFT 适合教格式与示范轨迹；蒸馏适合逼近 teacher 分布；GRPO 适合有可验证/可打分目标、需要探索与相对优势时。没有 verifier 硬上 GRPO，空组和 hacking 会一起出现。流水线背景见 `ali-sft-then-posttrain`，三者对比见 `ali-ppo-dpo-grpo-ask`。

## 三种信号，三种算法

- **继续 SFT：** 有高质量示范、格式/工具协议要稳定、需要快速对齐行为分布时优先。局限是缺乏探索，容易模仿 teacher 的平均行为，难突破上限。工具调用不正确时，有干净轨迹应先 SFT（`ali-tool-call-error-sft-rl`）。
- **蒸馏：** 有强 teacher、希望小模型逼近其输出分布；仍是监督学习，突破 teacher 上限更难。常用正向 KL 去拟合 teacher，和 RLHF 的反向 KL 不是同一个方向。
- **GRPO：** 同 prompt 多样本、组内相对优势，适合数学/代码/可验证任务，或有明确 reward/verifier 的 Agent 场景；能做 on-policy 探索。代价是 rollout 贵、空 group、credit 粗。

面试先问：奖励是否可验证、数据是否成对 preference、是否需要探索；再落到项目里为何选这条线。只有偏好对、没有环境奖励，DPO 往往更稳（`ali-multineg-then-grpo`）。

## 常见串行，而不是三选一

流水线经常是 SFT 打底 → DPO/偏好对齐 → on-policy GRPO 做 reasoning/工具成功率；蒸馏穿插在压缩或部署模型阶段。DPO 后分布可能变尖，接 GRPO 前要确认组内还能分开（`pt-dpo-to-grpo`）。Agent 写操作还要把过程分和 Guardrail 设计进去，否则 RL 会学到越权捷径。

选型口诀：示范轨迹 → SFT；偏好对 → DPO；可验证标量 → GRPO/PPO。信号不够就补数据或校验器，不要靠把学习率开大「逼它探索」。

阿里国际面要能落到项目：例如工具协议不稳时先 SFT 把 schema 学住；有单测/规则校验后再 GRPO 刷成功率。蒸馏解决的是部署体积，不是探索。继续 SFT 堆示范会把模型锁在 annotator 平均行为上，数学/代码这类可验证任务用组内相对优势更合适。空组和 credit 粗是 GRPO 的代价，要主动讲监控，而不是只说「能探索所以更好」。

## 追问

- **什么时候三者可以串行？** SFT 打底 → DPO/偏好对齐 → on-policy GRPO；蒸馏放压缩/部署。
- **没有 verifier 能 GRPO 吗？** 能用模型打分，但那是 RM，hack 风险回到 PPO/RLHF。优先规则/单测/schema。
- **蒸馏小模型再 GRPO？** 可以，但小模型组方差可能更差，先确认 `pass@k - pass@1` 仍大于 $0$。
