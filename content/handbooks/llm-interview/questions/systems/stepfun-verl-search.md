---
id: stepfun-verl-search
section: systems
order: 167
level: S
title: 阶跃：用 VeRL 训搜索工具 Agent 时，各类角色怎么设计？
quick: >-
  Actor 产 Thought/Action，环境执行搜索并回 Observation，奖励看检索是否必要、结果是否被用以及最终答案。VeRL
  的 rollout / update 分阶段，logprob 常需用当前权重重算，配置要和搜索延迟解耦。
tags:
  - StepFun
  - VeRL
  - Agent RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阶跃星辰agent算法面经分享
    url: https://www.nowcoder.com/feed/main/detail/d01a17cf25344f4bb73eff2dbbaf6eee
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：Agent 算法
- 届别 / 流程：原帖未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-30
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“介绍一下trl/verl架构，有哪些类，主要参数”**；**“用verl训agent调用搜索工具为例，讲一下每一类大致怎么设计”**

这块容易背源码类名，或把搜索 RTT 和 GPU generate 绑在同一个同步循环里。我会按职责说：谁采样、谁搜、谁打分、谁更新、谁算 KL。搜索延迟远高于纯生成，不异步、不缓存，GPU 会空转。蚂蚁 VeRL 账本卡讲样本数；本题讲角色与搜索耦合，见 `sys-rl-grpo-loop-roles`、`byte-verl-structure`。

## 按职责拆角色

- **Rollout Worker**：调 vLLM / SGLang 产 Thought/Action，解析 tool call。
- **Env / Tool**：标准化 query、top-k、超时，把检索结果写成 Observation。
- **Reward**：最终答对、是否空搜、是否重复搜、结果是否被后续推理用到。
- **Actor Trainer**：组相对或 PPO 更新；observation 段要 `loss_mask`。
- **Reference**：算 KL，权冻住。

不必背类名。要点是 rollout 与 update **分阶段**：先采完（含多轮搜），再在训练图上重算 logp、算优势、backward。搜索失败要有超时和默认 Observation，避免一个慢查询卡住整组。

## 关键参数和延迟解耦

`rollout.n`、温度、搜索 top-k、超时、最大工具步、global batch。搜索 RTT 常是几十到几百毫秒，应用异步并发和缓存（同 query 不重复搜）。配置上让「GPU 在生成」和「CPU/HTTP 在搜」重叠，而不是 `generate → 同步搜 → generate`。多轮还要 session / prefix cache，否则每轮重 prefill。

## 为什么重算 logprob

推理引擎与训练实现的数值、分块、量化可能不一致。off-policy 比 $\rho=\pi_\theta/\pi_{\mathrm{old}}$ 必须基于训练图的 $\log\pi$。工具段通常 mask 掉，只训 Action / 最终答案 token。见 `meituan-verl-recompute-logprob`。

## 追问

- **空搜要不要罚？** 要。否则模型学会乱调搜索刷步数。奖「必要且被使用的检索」，不是奖调用次数。
- **observation 进不进 loss？** 一般不进。那是环境给的 token，mask 掉，否则模型学复读检索结果。
- **搜索超时怎么设计？** 单步超时 + 最大工具步 + 降级 Observation。让整组等一个慢查询会把 batch 墙钟打穿。
- **和 TRL 差在哪？** TRL 偏单进程 PPO；VeRL 用 Ray 把 rollout / env / trainer 拆开，才能把搜索这种高延迟工具放到 rollout 阶段。
