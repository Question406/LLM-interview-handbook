---
id: pt-rejection-sampling-vs-rl
section: posttrain
order: 33
level: S
title: 什么时候应先做 rejection-sampling fine-tuning，什么时候必须进入 on-policy RL？
quick: 先看 base policy 的正确候选覆盖率。若较小 K 已能产出足够多高质量样本，RS 简洁稳定；若正确轨迹稀少、需跨多步探索或 reward 依赖当前策略状态，RS 会 support 收缩，应转向 on-policy RL 或先改善 seed / verifier。
tags:
  - Rejection Sampling
  - RL
  - Data Selection
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Llama 2 Technical Report
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
---

Rejection sampling（RS）对每个 prompt 采 $K$ 个回答，用 reward、规则或人工过滤，再把成功样本当 SFT 数据。它计算简单、可离线审计，Llama 2 等配方用它回收高质量对话；R1 类流水线也用它在 RL 前后沉淀成功轨迹。这块容易把 RS 叫成「离线 RL」，或反过来觉得不上 on-policy 就不算做推理。分界线是 base policy 的正确候选覆盖率，以及 reward 是否依赖当前策略走到的状态。`pt-cold-start-to-multistage-rl` 讲多阶段怎么排；本题讲何时该从 RS 切到 RL。

## RS 在学什么

RS 学习的是「现有政策已经会生成的成功子集」。过滤后做 MLE，相当于在高 reward 区域上做行为克隆。它适合：格式 / 风格对齐、已有高覆盖的可验证任务、需要人审的离线数据。优点是稳定、可复现、失败样本不会直接进梯度。

它不适合：正确轨迹极稀、需要连续多步探索才能到达可验证状态、或 reward 必须在当前政策的 state distribution 上估（过程分、工具环境）。这时筛出来的数据少且窄，重复 RS 会把政策锁死在少数题型上，即 support 收缩。

## 诊断：先画 $K$-success 曲线

关键图是覆盖率随 $K$ 的变化，以及过滤后的有效条数、题型熵。若较小 $K$ 已有足够多样的高质量样本，RS 通常是正确的第一步。若只有极大 $K$ 才偶尔成功，继续 RS 会过拟合那几条幸运轨迹；应先改善 seed / teacher / verifier（`pt-reasoning-seed-data-quality`），或进入 on-policy RL，在当前政策附近持续采样、用相对奖励更新。

On-policy RL 的代价是 rollout 成本、staleness（`pt-online-freshness`）和 reward hacking。没有可信 reward，上 RL 只是把 hacking 自动化。切换应由 held-out coverage、reward 可信度和总算力决定，不是由「现在都在讲 GRPO」决定。

也可以把决策写成阈值：设 $C(K)$ 为过滤后有效且去重后的轨迹数。$C(K)$ 已够覆盖目标题型，且过程抽检干净，就 RS；$C(K)$ 随 $K$ 几乎不涨，或有效轨迹高度重复，就不要再烧采样，转改善 seed（`pt-reasoning-seed-data-quality`）或上 on-policy。RS 重复多轮时，每一轮的 support 都是上一轮政策的成功子集，会越滤越窄。这是和 on-policy 最关键的差别。

实践上常 RS 冷启动或回收稳定样本，再 RL 扩展边界；RL 后再 RS 一次，把验证过的成功轨迹冻成 SFT，降低线上方差。这是流水线，不是二选一教条。`pt-cold-start-to-multistage-rl` 里的 RS 正是这个「沉淀」角色。

## 白板对照

同一道竞赛填空：base 在不大的 $K$ 就常出对，RS 能快速抬 `pass@1` 且格式干净。另一道需要多轮工具、中途状态会变的题：过滤集几乎为空，或全是同一条幸运路径。这时 RS 只会教「背这一条」，必须 on-policy 探索或先改环境 / seed。

还要防 RS 特有的偏差：filter 偏爱长答案、某一种解题模板、或与训练 checker 同漏洞的假成功。进 SFT 前做过程抽检，和 `pt-rlvr-reasoning-eval` 同一原则。有强 teacher 时，先考虑 `pt-on-policy-distillation`：监督比「自己采自己滤」稠密，而且状态对学生相关。没有 teacher、有 verifier，才在 RS 与 RL 之间排期。

先看 $C(K)$ 和过程抽检；够且干净则 RS；窄或重复则补 seed / teacher；需要状态上的相对奖励再上 on-policy。不要从算法潮流反推。

## 追问

- **RS 算不算 RL？** 不算。它没有用当前政策的 on-policy 梯度去优化期望奖励，只是在过滤集上做监督。把它叫「离线 RL」会掩盖 support 收缩这个核心风险。
- **覆盖率高就永远不用 RL 吗？** 不一定。要跨多步、reward 依赖状态、或想把长尾成功变成默认行为时，RL 仍更合适。覆盖率高只说明 RS 值得先做，不说明它是终点。
- **覆盖率低能不能硬 RS？** 能跑，但数据窄、易过拟合。优先补 seed / teacher，而不是把 $K$ 加到不经济。重复多轮 RS 会越滤越窄，比一轮失败更隐蔽。
- **和 distillation 怎么选？** 有强 teacher 时，on-policy 蒸馏（`pt-on-policy-distillation`）往往比「自己 RS 自己」更稠密；没有 teacher 且有 verifier，才在 RS 与 RL 之间选。RS / STaR 是硬过滤成功样本；OPSD 对错前缀都给软分布，见 `pt-star-vs-opsd`。流水线里可以先后出现，角色不同。
