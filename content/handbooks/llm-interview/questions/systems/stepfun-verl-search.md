---
id: stepfun-verl-search
section: systems
order: 167
level: S
title: 阶跃：用 VeRL 训搜索工具 Agent 时，各类角色怎么设计？
quick: >-
  把生成、工具执行、判分、更新和 reference 分开：Actor 产 Thought/Action，环境执行搜索返回
  Observation，Reward 检查必要性、使用情况与最终答案。VeRL 分阶段做 rollout 和
  update，用异步并发、缓存与超时隔离搜索延迟，再在训练图上重算 logp。
tags:
  - StepFun
  - VeRL
  - Agent RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阶跃星辰agent算法面经分享
    url: 'https://www.nowcoder.com/feed/main/detail/d01a17cf25344f4bb73eff2dbbaf6eee'
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：Agent 算法
- 届别 / 流程：原帖未披露
- 面试时间：原帖未披露；帖子发布于 2026-03-30
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“介绍一下 trl/verl 架构，有哪些类，主要参数”**；**“用 verl 训 agent 调用搜索工具为例，讲一下每一类大致怎么设计”**

用 VeRL 训练搜索 Agent，我会按生成、工具执行、判分、更新和 reference 拆职责，让搜索请求和 GPU 生成异步重叠。否则同步等待搜索 RTT 时，GPU 就会空转。这里重点是角色如何配合，样本账本与架构可对照 `sys-rl-grpo-loop-roles`、`byte-verl-structure`。

- Rollout Worker：调 vLLM / SGLang 产 Thought/Action，解析 工具调用。
- Env / Tool：standardization query、top-k、超时，把检索结果写成 Observation。
- Reward：最终答对、是否空搜、是否重复搜、结果是否被后续推理用到。
- Actor Trainer：组相对或 PPO 更新；observation 段要 `loss_mask`。
- Reference：算 KL，权冻住。

这些角色先完成包含多轮搜索的 sampling 轨迹（rollout），再进入 update：在训练图上重算 logp、计算优势，然后 backward。搜索失败要有超时和默认 Observation，避免一个慢查询卡住整组。

配置时要一起看 `rollout.n`、温度、搜索 top-k、超时、最大工具步和 global batch。搜索 RTT 常是几十到几百毫秒，应用异步并发和缓存（同 query 不重复搜）。配置上让「GPU 在生成」和「CPU/HTTP 在搜」重叠，而不是 `generate → 同步搜 → generate`。多轮还要 session / prefix cache，否则每轮重 输入 prefill。

推理引擎与训练实现的数值、分块、量化可能不一致。off-policy 比 $\rho=\pi_\theta/\pi_{\mathrm{old}}$ 必须基于训练图的 $\log\pi$。工具段通常 mask 掉，只训 Action / 最终答案 token。见 `meituan-verl-recompute-logprob`。

## 追问

**空搜要不要罚？**
要。否则模型学会乱调搜索刷步数。奖「必要且被使用的检索」，不是奖调用次数。
**observation 进不进 损失（loss）？**
一般不进。那是环境给的 token，mask 掉，否则模型学复读检索结果。
**搜索超时怎么设计？**
单步超时 + 最大工具步 + 降级 Observation。让整组等一个慢查询会明显增加整个 batch 的耗时。
**和 TRL 差在哪？**
TRL 偏单进程 PPO；VeRL 用 Ray 把 rollout / env / trainer 拆开，才能把搜索这种高延迟工具放到 rollout 阶段。
