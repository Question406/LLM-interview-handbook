---
id: pt-rejection-sampling-vs-rl
section: posttrain
order: 33
level: S
title: 什么时候应先做 rejection-sampling fine-tuning，什么时候必须进入 on-policy RL？
quick: "先看 base policy 在较小 K 下能不能采出足够多、足够多样的正确样本：能，就先做 RS，简单稳定、可审计。正确轨迹稀少、要跨多步探索，或奖励依赖当前策略走到的状态，RS 会越滤越窄，这时转 on-policy 强化学习（RL），或先补 seed / teacher / 验证器（verifier）。"
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

分界线有两条：base policy 的正确候选覆盖率够不够，以及奖励依不依赖当前策略走到的状态。小 $K$ 就能采出足够多、足够多样的好样本，先做 rejection sampling（RS）；正确轨迹很稀、要连续多步探索才能到达可验证状态，或者奖励必须在当前策略的 state distribution 上估（过程分、工具环境），就该进 on-policy 强化学习（RL）。

RS 是对每个 prompt 采 $K$ 个回答，用 reward、规则或人工过滤，再把成功样本当监督微调（SFT）数据。它学的是「现有策略已经会生成的成功子集」，过滤后做 MLE，相当于在高 reward 区域上做行为克隆。计算简单、能离线审计、可复现，失败样本也不会直接进梯度，适合格式和风格对齐、覆盖率已经高的可验证任务，以及需要人审的离线数据。Llama 2 等配方用它回收高质量对话，R1 类流水线也在 RL 前后用它沉淀成功轨迹。

它的风险是 support 收缩。正确轨迹很稀时，筛出来的数据又少又窄；重复 RS 时，每一轮的 support 都是上一轮策略的成功子集，会越滤越窄，策略被锁死在少数题型上。这是 RS 和 on-policy RL 最关键的差别，也是为什么把 RS 叫「离线 RL」会误导人。

所以我会先画 $K$-success 曲线：覆盖率随 $K$ 怎么变，过滤后的有效条数和题型熵是多少。设 $C(K)$ 为过滤后有效且去重后的轨迹数。$C(K)$ 已经能覆盖目标题型、过程抽检也干净，就 RS；$C(K)$ 随 $K$ 几乎不涨，或者有效轨迹高度重复，就别再烧采样，先改善 seed / 教师模型（teacher）/ 验证器（verifier）（`pt-reasoning-seed-data-quality`），或者上 on-policy RL，在当前策略附近持续采样、用相对奖励更新。只有极大 $K$ 才偶尔成功时还继续 RS，会过拟合那几条幸运轨迹。

举两道题对比。一道竞赛填空，base 在不大的 $K$ 下就常出对，RS 能很快把 `pass@1` 抬上去，格式也干净。另一道要多轮调工具，中途状态会变，过滤集几乎是空的，或者全是同一条幸运路径，RS 只会教模型「背这一条」，必须 on-policy 探索，或者先改环境和 seed。

上 RL 也有代价：采样轨迹（rollout）成本、staleness（`pt-online-freshness`），还有模型钻奖励规则的空子。没有可信的 reward，上 RL 只是把 hacking 自动化。所以切换要看 held-out coverage、reward 可不可信和总算力，「现在都在讲 GRPO」算不上理由。RS 自己也有偏差要防：filter 偏爱长答案、偏爱某一种解题模板，或者和训练 checker 有同样漏洞的假成功，进 SFT 之前要做过程抽检，和 `pt-rlvr-reasoning-eval` 是同一个原则。

实际流水线里两者常常前后都有：先用 RS 冷启动或回收稳定样本，再用 RL 扩展边界，RL 之后再做一次 RS，把验证过的成功轨迹冻成 SFT 数据，降低线上方差。`pt-cold-start-to-multistage-rl` 讲多阶段怎么排，RS 在里面就是这个「沉淀」角色。手上有强 teacher 的话，先考虑 `pt-on-policy-distillation`，监督比「自己采自己滤」更稠密，状态也和学生相关。

## 追问

**RS 算不算 RL？**
不算。它没有用当前策略的 on-policy 梯度去优化期望奖励，只是在过滤集上做监督。叫它「离线 RL」会掩盖 support 收缩这个核心风险。

**覆盖率高就永远不用 RL 吗？**
不一定。要跨多步、reward 依赖状态，或者想把长尾成功变成默认行为时，RL 仍然更合适。覆盖率高只说明 RS 值得先做，说明不了它是终点。

**覆盖率低能不能硬做 RS？**
能跑，但数据窄、容易过拟合。优先补 seed 或 teacher，别把 $K$ 加到不经济。多轮 RS 越滤越窄，比一轮失败更隐蔽。

**和蒸馏怎么选？**
有强 teacher 时，on-policy 蒸馏通常比自己 RS 自己更稠密；没有 teacher 但有 verifier，才在 RS 和 RL 之间排期。RS / STaR 是硬过滤成功样本，OPSD 对对错前缀都给软分布，见 `pt-star-vs-opsd`。流水线里它们可以先后出现，角色不同。
