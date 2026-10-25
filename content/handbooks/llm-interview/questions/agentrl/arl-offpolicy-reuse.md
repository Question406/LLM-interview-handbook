---
id: arl-offpolicy-reuse
section: agentrl
order: 18
level: S
title: 旧 Agent Trajectory 能不能反复拿来训练？什么时候会变成 Off-Policy 问题？
quick: "能用，看怎么用：做监督微调（SFT）、经验回放或离线评估都可以；拿旧策略、旧工具或旧网页状态下的轨迹估当前策略梯度，就变成 off-policy 问题，要处理分布偏移。重要性权重方差可能很大，裁剪更稳但会引入偏差；缺 log-prob 或环境版本时，就当演示用或重新采样。"
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

能用，看怎么用。拿旧轨迹做监督微调（SFT）、经验回放或离线评估都可以；一旦拿旧策略、旧工具、旧网页状态下的轨迹去估当前策略的梯度，就成了 off-policy 问题，要处理分布偏移。重要性权重能校正，但方差可能很大；裁剪能稳住，却会引入偏差。

比如去年一条成功轨迹点了某个页面上的「提交」按钮，今年网页改版，那个按钮已经不存在了。这时候 $\rho$ 校正得再准，也解决不了环境变化。WebArena 一类环境第二天 DOM 就可能变，状态 $s$ 本身就过期了，网页和检索类任务尤其别把「去年的成功点击序列」当今年的强化学习（RL）批次。所以「replay buffer 很大，数据就够」是个常见误区。

行为策略 $\pi_b$ 和要优化的 $\pi$ 不同，还想估 $\pi$ 的回报梯度，就要做 off-policy 校正。Agent 里的偏移更大，除了权重变了，检索索引、网页、工具版本也可能变了。GRPO 默认使用同一批采样轨迹（rollout），混进跨代轨迹要单独论证。

## 重要性采样、陈旧、clip

如果还留着行为对数概率，重要性比 $\rho_t=\pi(a_t|s_t)/\pi_b(a_t|s_t)$ 可以校正，但长轨迹连乘会让方差爆炸，有效样本量（ESS）塌缩。PPO 式的 clip 能压方差，同时引入偏置，被裁掉的步不再忠实代表 $\pi$。没存 log-prob 就别事后瞎补 IS，最多当行为克隆或过滤后的演示。所以采集时就要记下判断数据能否复用的信息：policy/version、温度、action log-prob、工具与页面版本、奖励分数（reward）规则。没有这些，就别假装做了校正。

监控比 buffer 大小重要，要看 $\rho$ 的分布、ESS、clip 比例、按轨迹长度分层的 return。$\rho$ 长期钉在 clip 边界，说明数据已经过期，再训就是在拟合旧世界。公式层面见 `fund-is`、`fund-onoff`，这题多出来的是工具和网页的陈旧。

## 何时 replay 合理

通常没问题的用法有三种：成功轨迹做 SFT / filtered BC，承认有分布偏移，目标是克隆可用行为；近端、同一工具版本的样本做辅助价值或偏好；离线评估时说清楚分数属于 $\pi_b$。要小心的是拿旧轨迹估当前的 policy gradient，或者环境、工具已经换了还当 on-policy。办法是限制 freshness（只吃最近 $k$ 代），对 $\rho$ 做 clip 并监控被裁比例，或者干脆 on-policy 重采样。

决策可以归成一句话：旧轨迹默认当演示或过滤 BC；只有 log-prob、环境版本、reward 规则都还在，freshness 也够，才进带 clip 的 IS/PPO；缺任何一项就重采样。有人说「我们有一百万条历史轨迹，所以 RL 数据够」，先问这三样还在不在，再问 clip 比例是多少。

## 追问

**没有存 log-prob 怎么办？**
别事后用当前 $\pi$ 反算、假装做了 IS，support 对不上。当成过滤后的演示，或者在相似任务上用当前策略重采样。

**SFT 旧成功轨迹算 off-policy 吗？**
算分布偏移，但不走重要性权重。风险是克隆过时的工具和页面用法，要按环境版本过滤，别当成免费的 on-policy 批次。

**$\rho$ 一直钉在 clip 边界怎么办？**
丢掉这批数据，别再加大 buffer。比值公式和 `fund-onoff`、`fund-is` 里一样，Agent 多出来的是工具和网页陈旧。

**GRPO 能直接混历史组吗？**
默认吃的是同批 rollout。跨代轨迹要单独论证 freshness 和 clip；混进去还当 on-policy，方差和偏置都会被藏进组平均里。
