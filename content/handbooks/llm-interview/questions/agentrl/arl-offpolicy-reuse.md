---
id: arl-offpolicy-reuse
section: agentrl
order: 18
level: S
title: 旧 Agent Trajectory 能不能反复拿来训练？什么时候会变成 Off-Policy 问题？
quick: "旧轨迹可以用于监督微调（SFT）、经验回放或离线评估。但如果用旧策略、旧工具或网页状态下的轨迹估计当前策略梯度，就要处理分布偏移。重要性权重可能带来很大方差，裁剪能提高稳定性，却会引入偏差。"
tags:
  - Agent RL
  - Off-Policy
  - Replay
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: WebArena
    url: 'https://arxiv.org/abs/2307.13854'
    type: legacy-reference
  - title: DeepSeekMath / GRPO
    url: 'https://arxiv.org/abs/2402.03300'
    type: legacy-reference
---

常见误区是：「replay buffer 很大所以数据够」。旧轨迹不是不能用，错在把它当成当前 policy 的 on-policy 梯度。行为策略 $\pi_b$ 与待优化 $\pi$ 不同，还想估 $\pi$ 的回报梯度，就必须做 off-policy 校正。Agent 里偏移更大：权重变了，检索索引、网页、工具版本也可能变了。WebArena 一类环境第二天 DOM 就变，$s$ 本身过期；GRPO 默认使用同一批采样轨迹（rollout），混进跨代轨迹要单独论证。

## 重要性采样、陈旧、clip

若仍有行为对数概率，重要性比 $\rho_t=\pi(a_t|s_t)/\pi_b(a_t|s_t)$ 可校正，但长轨迹连乘使方差爆炸，有效样本量（ESS）塌缩。PPO 式 clip 压方差，同时引入偏置：被裁掉的步不再忠实代表 $\pi$。没有存 log-prob 就不要事后瞎补 IS，最多当行为克隆或过滤演示。先记录用于判断数据是否可复用的信息：policy/version、温度、action log-prob、工具与页面版本、奖励分数（reward） 规则。没有这些就别假装校正。

监控比 buffer 大小更重要：$\rho$ 的分布、ESS、clip 比例、按轨迹长度分层的 return。$\rho$ 长期钉在 clip 边界，说明数据已过期，再训是在拟合旧世界。公式层面见 `fund-is`、`fund-onoff`；本题多出来的是工具与网页陈旧。

## 何时 replay 合理

通常 OK：成功轨迹做 监督微调（SFT） / filtered BC（承认这是分布偏移，但目标是克隆可用行为）；近端、同一工具版本的样本做辅助价值或偏好；离线评估时明确分数属于 $\pi_b$。要小心：用旧轨迹估当前 policy gradient；环境或工具已换仍当 on-policy。做法：限制 freshness（只吃最近 $k$ 代）、对 $\rho$ 做 clip 并监控被裁比例、或干脆 on-policy 重采样。SFT 旧成功轨迹也算偏移：风险是模仿过时工具用法，应用环境版本过滤，而不是当免费的 on-policy 数据。

网页与检索类任务尤其不能把「去年的成功点击序列」当今年的 强化学习（RL） 批次。如果按钮已经不存在，仅校正 $\rho$ 也无法解决环境变化。

决策可以压成一句话：旧轨迹默认当演示或过滤 BC；只有 log-prob、环境版本、reward 规则都还在，且 freshness 够，才进带 clip 的 IS/PPO；缺任何一项就重采样。面试里若有人说「我们有一百万条历史轨迹所以 RL 数据够」，先问这三样还在不在，再问 clip 比例是多少。

## 追问

- **没有存 log-prob 怎么办？** 不要事后用当前 $\pi$ 反算假装 IS，support 对不上。当过滤演示，或在相似任务上用当前策略重采样。
- **SFT 旧成功轨迹算 off-policy 吗？** 算分布偏移，但不走重要性权重。风险是克隆过时工具/页面用法，必须按环境版本过滤，不能当免费 on-policy 批次。
- **和 on-policy 题的关系？** 见 `fund-onoff`、`fund-is`：比值公式一样，Agent 多了工具与网页陈旧。$\rho$ 钉在 clip 边界就该丢这批，而不是再加大 buffer。
- **GRPO 能直接混历史组吗？** 默认吃同批 rollout。跨代轨迹要单独论证 freshness 与 clip；混进去却当 on-policy，方差和偏置都会被藏进组平均。
