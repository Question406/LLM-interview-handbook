---
id: ant-why-dpo-under-resource
section: posttrain
order: 123
level: A
title: 蚂蚁日常实习：资源受限时为何选用 DPO？
quick: >-
  假设已有一批可靠的 chosen/rejected pairs，但训练预算有限。DPO 可以直接使用这些离线比较，通常比搭建完整在线 rollout 与
  RM 训练流程更容易起步。
tags:
  - Ant Group
  - DPO
  - Resource Constraints
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 蚂蚁大模型llm算法日常实习面经
    url: 'https://www.nowcoder.com/feed/main/detail/c6aadaf60f9c431bbe0738e0c802dfd7'
    type: candidate-first-hand
---

## 回答思路

> **问题与场景：** 假设已有一批可靠的 chosen/rejected pairs，但训练预算有限。
>
> **做法与原因：** 如果模型更新后会遇到离线数据没覆盖的回答，或者任务有可交互环境，在线 RL 更容易收集当前策略的经验，但要承担生成、评分与稳定训练的成本。
>
> **检查与取舍：** 我会先比较数据条件与反馈来源，再做匹配预算实验。

## 可以这样回答

假设已有一批可靠的 chosen/rejected pairs，但训练预算有限。DPO 可以直接使用这些离线比较，通常比搭建完整在线 rollout 与 RM 训练流程更容易起步。

如果模型更新后会遇到离线数据没覆盖的回答，或者任务有可交互环境，在线 RL 更容易收集当前策略的经验，但要承担生成、评分与稳定训练的成本。

我会先比较数据条件与反馈来源，再做匹配预算实验。DPO 不保证永远不需要新数据，PPO 也不会自动修好不可靠的 reward。

## 技术备查

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型 LLM 算法日常实习
- 届别 / 流程：日常实习；轮次未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-31
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“场景下为什么选用 DPO，卡和资源环境”**

资源受限时选 DPO，是因为它把对齐变成了离线 preference learning，省掉了整个在线 sampling 环，训练图里主要只有一个可训策略和一个冻结参考。前提是手里有可靠的偏好对，而且任务不需要探索新的推理或工具路径。

回答时我会先报资源账，再谈算法，只说「DPO 更简单、更好训」讲不出省在哪。PPO 通常要同时驻留 actor、reference、reward model（RM）（或者验证器（verifier）服务）和价值评估模型（critic），外加大量 online sampling 轨迹（rollout）。GRPO 可以弱化 critic，但仍然吃每题 $n\gt 1$ 的 sampling 和 verifier 的 QPS，见 `sys-rl-group-n`。实习或业务试点常见的约束是少量 GPU、排队长、不能长时间占推理集群，这时候 DPO 的性价比才说得清。所以我会点名卡型号、单卡 batch、能不能开 vLLM rollout 或推理引擎，再下结论。

DPO 损失只含冻结的 $\pi_{\mathrm{ref}}$ 和可训的 $\pi_\theta$：

$$
\mathcal{L}=-\mathbb{E}\log\sigma\Big(\beta\big(\log\tfrac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\log\tfrac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)}\big)\Big).
$$

没有 online sampling，没有 GAE，没有组 standardization，也就没有「有效组比例」这本账。显存和调度都简单，迭代也快：改完偏好对就能再训一晚，不用排推理集群。目标是风格、安全、拒答，或者「在已有正确答案里挑更好的」，又能构造出 $(y_w,y_l)$ 时，它通常比硬上 RLHF 好。省掉的是 sampling 环，数学没变：它仍来自 reverse KL 约束的闭式解，见 `fund-kl-directions`，不是「没有正则的 pairwise CE」。$\beta$ 是偏离 ref 的温度，不是学习率，也不是省算力的旋钮。

限制要自己讲出来，有三条。一是偏好对的质量，数据覆盖不到的失败不会自己冒出来。二是长度 bias，总 logp 差偏向更长的 chosen。三是离线分布漂移，线上用户一变，训练时的间隔再漂亮也没用。如果卡其实够、verifier 可靠、任务又需要没见过的推理链或工具路径，就该升级到 GRPO；要价值估计或连续权衡再上 PPO。CISPO 这类 Clip / IS 变体解决的是 rollout 之后的 off-policy 权重，见 `pt-cispo`，根本没有 sampling 预算的时候它帮不上。

## 追问

**卡够了还用 DPO 吗？**
有稳定偏好、不需要探索时仍然可以用。一旦有了 verifier，就该在 holdout 上和 GRPO 比一比，别因为惯性停在离线。

**为什么不先做 rejection sampling？**
RS 也要生成 $n$ 条再过滤，推理预算可能比离线 DPO 还贵，而且负例被扔掉了。

**$\beta$ 能当省算力的旋钮吗？**
不能。$\beta$ 管贴 ref 的幅度，不管 GPU 小时。省算力靠去掉 sampling 环，拧 $\beta$ 没用。

**一条偏好对算多少有效样本？**
一条 pair 对应一次间隔更新。别拿它和 GRPO 的 $n$ 条轨迹横着比条数。

**没有 pair，只有规则呢？**
那就不是 DPO 的场景了。有规则就走 verifier + GRPO，或者先用规则造 pair，同时承认这是弱监督。
