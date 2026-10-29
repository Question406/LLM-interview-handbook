---
id: align-agent-rl
section: alignment
order: 21
level: S
title: 对齐：多智能体 / 工具 RL 的稀疏奖励与 credit assignment
quick: >-
  工具 RL 只在终点得到 0/1 时，要分清训练奖励落在
  token、工具调用还是整条轨迹上。组内成功与失败对照能降低方差，但整组全零仍没有信号；可用课程、中间态重置和可检查的子目标增加可学习的比较。
tags:
  - OpenAI
  - DeepMind
  - Agent
  - RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: WebArena — A Realistic Web Environment for Building Autonomous Agents
    url: 'https://arxiv.org/abs/2307.13854'
    type: primary
  - title: >-
      DeepSeek-R1 — Incentivizing Reasoning Capability in LLMs via Reinforcement
      Learning
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
---

长工具轨迹的 RL，要先明确哪些动作得到信用，以及终局奖励能提供多少信息。同一个成功回报乘到所有 token，虽然能训练，却仍分不清哪次探索或哪次提交促成了成功。

例如 WebArena 用页面最终功能状态检查成功，中间点击可以全是 0。一次 episode 包括模型 token、工具调用和环境观察，典型奖励是 $r_t=0$（$t\lt T$），终局 $r_T\in\{0,1\}$，如单测通过或表单提交成功。Monte Carlo 回报为：

$$
G_t=\gamma^{T-t}r_T.
$$

同一个 $\hat A$ 回放到所有 response token，会把必要探索与最后一次幸运提交一起鼓励。Token 级更新只能作用在模型生成的动作上，工具返回观察不是动作，必须 mask 掉。Turn / tool 级可以给完整调用，包括名字、参数、宿主是否执行，一个优势，便于对应点错按钮等错误；episode 级只给整条轨迹 $r_T$，实现简单但更稀疏。

成功率接近 0 或 1 时，组内经常全平，GRPO 的 $\hat A=0$，见 `align-grpo`。折现 $\gamma\lt 1$ 会偏向短轨迹，$\gamma=1$ 更公平但方差大。可验证任务可先用 $\gamma=1$ 和组 standardization，再从课程、温度、演示或重置到“差一步”的状态增加成功失败对照，调 LR 无法从全零回报中制造信号。

下面只是把终局回报传回每步，仍没有解决动作间的 credit assignment：

```python
def episode_adv(r_T, T, gamma=1.0):
    # 同一终局标量回放到每一步；真正的 credit 还要靠分组 / 过程信号
    gs = [(gamma ** (T - t)) * r_T for t in range(T)]
    return gs
```

## 多 agent 怎样分清贡献

执行与检查两个助手若只共享一个最终标量，可能减少自己的探索、让对方承担风险。可以借鉴 counterfactual / difference reward：固定其他人的动作，只替换自己的 $a^i$，看全局 $r$ 的变化。LLM 工程中很难对其他 agent 真正积分，常退到可检查的子目标，如检索是否命中 ACL、补丁是否通过单测，再保留全局成功 threshold。

过程信号要来自环境事件，避免靠阅读 CoT 主观打合作分，见 `align-process-reward`。无限计划、工具失败后反复重试打满下游、只刷调用痕迹却不推进任务，都是奖励可能被利用的方式，见 `align-reward-hack`。reverse KL 仍用于约束偏离 reference policy，见 `align-rlhf-kl`，它不负责识别哪次点击有功。

可验证、可重置的环境，可以以 outcome 加组相对奖励或 RFT grader 为主，见 `align-rft`；开放网页难复现时，先冻结评测环境，见 `design-eval-agent`。单循环的预算、trace、确认机制还不稳，就先把它做好再增加 agent，见 `design-agent-harness`。这道题按公开 agent post-training 概念整理，相关工具 RL 见 `align-tool-rl`。

## 追问

**共享优势就解决 credit 了吗？**
没有，它主要降低方差。区分动作贡献还要过程信号或反事实比较。

**成功率 2% 能直接 GRPO 吗？**
组内会经常全 0，先用课程、演示或中间态重置，让组里更容易出现对照。

**观察 token 要进 policy gradient 吗？**
不要，只保留模型 token 与工具调用动作，环境观察要 mask。

**过程奖励和 credit assignment 是什么关系？**
过程奖增加更密的 $r$，credit assignment 决定给定 $r$ 如何回传给动作，可以分别设计。
