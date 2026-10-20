---
id: pt-multi-objective-reward-pareto
section: posttrain
order: 229
level: S
title: 多目标 Reward 如何做 Pareto 权衡，而不是拍一个标量权重？
quick: >-
  把 helpfulness、safety、length、tool success 写成向量目标，先估近似 Pareto 前沿再按硬约束选部署点。
  固定线性加权只是一条射线；必须报告权重敏感度与约束违反率，不能只报加权总分上升。
tags:
  - Multi-objective RL
  - Reward Design
  - Pareto
  - Safe RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Safe RLHF — Safe Reinforcement Learning from Human Feedback
    url: https://arxiv.org/abs/2310.12773
    type: primary
  - title: InstructGPT
    url: https://arxiv.org/abs/2203.02155
    type: secondary
---

这块容易把「加权总分涨了」当成全面变好。正确性、安全性、简洁度、工具成功率不可交换：把不可妥协的安全项和可妥协的文风项塞进同一个 $w^\top r$，只是沿着权重射线切开 Pareto 曲面的一个点；权重一抖，最优策略可能跳到另一条 trade-off 上。Safe 基于人类反馈的强化学习（RLHF） 把伤害当约束而不是再乘一个可调系数，就是拒绝这种假交换。InstructGPT 已经把「有用、诚实、无害」写成需要同时盯的目标，不是一个可随意对冲的标量。

## 标量化只覆盖凸包上的一条射线

多维回报写成 $r(x,y)=(r_1,\ldots,r_m)$。线性加权

$$
r_w = w^\top r(x,y),\qquad w_i\ge 0,\ \sum_i w_i=1
$$

对应从原点出发的射线 $w$，只能稳定找到凸前沿上的点；凹进去的折中（例如「中等正确、极低伤害」）会被跳过。扫一组 $w$ 并画两两投影，才能看见「再压一点长度会掉多少 pass@k」。`pt-adaptive-thinking-budget` 里的 quality-cost 曲线是同一逻辑：全集平均准确率涨了，可能只是所有题都写得更长。

固定 $w$ 还有隐藏风险：某一维没有监控（citation 忠实度、过度拒答）会在总分里被其他维补偿掉。这和 `pt-safety-capability-regression` 一致：切片门禁，不要一个加权分宣布「都涨了」。代码助手同时优化 pass@k、危险命令拒绝率、平均 token 数 时，拍死的 $w$ 很容易刷出短但不可靠的补丁。Chebyshev / 最大最小标量化 $\min_i w_i(r_i-z_i)$ 能碰到线性加权够不着的非凸折中，但参考点 $z$ 本身又是一组超参。面试里要能说清：你是在找凸包点，还是在找「每一维都保持在允许范围内」的盒子。

把 length、latency 和 safety 放进同一可交换标量，是最常见的假 Pareto：模型用拒答或灌水换分数，曲线看起来光滑，产品不可用。正确拆法是代价维进约束或单独画 quality-cost 前沿（与 `pt-adaptive-thinking-budget` 同一张图的哲学），安全维进硬约束，只有可替换的文风 / 格式才允许加权。

## 约束优化怎么选部署点

更稳妥的流程是：先估计近似 Pareto 前沿（多组权重、分层优化、或约束 强化学习（RL）），再按产品硬约束在前沿上切一刀。常见切分是 safety 作约束、其余作目标：

$$
\max_\theta\ \mathbb{E}[r_{\mathrm{help}}(x,y)]\quad\mathrm{s.t.}\quad \mathbb{E}[c_{\mathrm{safe}}(x,y)]\le\tau.
$$

拉格朗日乘子由约束违反率调，而不是事先拍死。对偶问题里 $\lambda$ 过小会漏约束，过大则任务能力明显下降，表现得像「安全 washing」：安全集分数好看，主任务塌。扫前沿时至少记录：每组 $w$ 或 $\tau$ 下的各维均值、约束违反率、长度 / KL，以及是否有未监控维在恶化。上线前用业务阈值（安全违反率、P95 token）选点，并报告 $w$ 小扰动后主指标与违反率是否翻转。贴在拐点上的点不适合直接部署。分层优化（先满足安全，再最大化有用）实现简单，但第一阶段过狠会把可行集缩成拒答模型，第二阶段救不回来，所以每层都要保留对方的 replay。

不可交换的维进约束，可交换的才允许加权。只报 $r_w$ 上升，等于没做完多目标。

## 追问

- **线性加权找不到凹前沿怎么办？** 用约束、分层（先安全后能力）或网格搜非凸组合；不要假设加权已经穷尽全部折中。
- **$\tau$ 怎么定？** 相对冻结安全集的基线违反率，而不是绝对「看起来安全」。和 `pt-safety-capability-regression` 一样设双门禁。
- **和自适应思考预算？** `pt-adaptive-thinking-budget` 是质量-成本 Pareto；本题是对齐目标之间的 Pareto。都要画曲线选部署点，都不要只报加权总分。
- **权重敏感度怎么报？** 对 $w$ 做小扰动，看主指标与约束违反是否翻转；翻转剧烈说明当前点贴在拐点上。
