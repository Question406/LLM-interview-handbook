---
id: tencent-grpo-continuous-reward
section: posttrain
order: 103
level: S
title: 腾讯 26 校招：GRPO 的 rollout 如何设定？为什么不直接用连续奖励？
quick: "group size 要根据同题回答的差异、采样成本和估计方差选择。GRPO 可以使用连续奖励，关键是评分可靠、可比较并经过校准。如果连续奖励模型（RM）的分数漂移，或能被策略钻空子，反而比可验证的离散评分更危险。"
tags:
  - Tencent
  - 2026 Campus Recruiting
  - GRPO
  - Reward Design
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯-26校招-大模型算法二面 1h（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/905343c9a3834f8d9d9bdc3790a59687
    type: candidate-first-hand
---

## 真题记录

- 公司：腾讯
- 团队 / 岗位：大模型算法
- 届别 / 流程：26 届校招；二面（1 小时）
- 面试时间：原帖未披露；帖子发布于 2026-03-23
- 来源类型与可信度：牛客候选人原帖，A（公司、届别、岗位和轮次明确）
- 原始措辞：**“grpo的rollout是多少，为什么不用连续的奖励”**

原帖未说明「是多少」指固定 group size 还是该候选人项目的配置，因此不能伪造一个唯一数字。把「连续奖励 GRPO 不能用」也说成定理，是常见失分点。GRPO 吃的是组内可比较的标量；连续或离散都能标准化成相对优势。真正要答的是：group size 怎么在差异、成本和方差之间取舍，以及连续 奖励模型（RM） 为何往往比可验证离散 oracle 更危险。

## Rollout / group size：调参，不是魔法数

同一输入提示 采 $G$ 条。$G$ 太小：相对优势方差大，容易全同分（全对全错），有效组少。$G$ 太大：生成成本、等待长尾、样本相关（温度不够时几条几乎一样）。应按 输入提示（prompt） 难度、可用并行度、奖励方差和**有效组比例**做 sweep，汇报时带有效组而不是只报 $G=8$。

「rollout 是多少」若问的是每步新鲜度：还要说 policy 多旧才更新、是否 on-policy 重采样。Group size 和 freshness 是两件事，不要用一个数字糊弄。

## 连续奖励不是不能用

组内标准化后，连续 $r$ 照样形成 $\hat A_i=(r_i-\bar r)/(\sigma_r+\varepsilon)$。数学部分分、长度惩罚、RM 分数都可以进这个公式。GRPO 没有「只接受 0/1」的限制。离散 oracle 受欢迎，是因为它可审计、尺度稳、更难被空话劫持，不是因为算法禁连续。

## 取舍：可信、可比较、校准

数学或 API outcome 优先用离散且可审计的 oracle。连续 RM 能表达细粒度偏好，但必须看 calibration、漂移、长度偏置和 钻奖励规则的空子：分数漂了，组标准化会把噪声放大成方向；更长就更高分时，模型会灌水。混合使用可以：可验证项用离散，风格项用校准过的连续分，并分别监控。把「不用连续」说成项目选择（RM 不可信），而不是 GRPO 的定义。

## 追问

- **有没有标准 $G$？** 没有。看有效组比例和成本，常见从 4-16 扫起，但不要背成唯一答案。
- **连续 RM 怎样才敢用？** 先校准、看长度偏置、冻结评测对照；漂移就回退到 oracle。
- **全连续、无 验证器（verifier）？** 可以跑，但更像 RM-RLHF，hack 风险回到 PPO 那一套。
- **和「为什么选 GRPO」怎么衔接？** 有可验证标量、能成组采样才是主因；连续与否是奖励设计，不是算法门槛。
