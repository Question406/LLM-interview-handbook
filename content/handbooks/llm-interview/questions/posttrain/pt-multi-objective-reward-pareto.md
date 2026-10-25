---
id: pt-multi-objective-reward-pareto
section: posttrain
order: 229
level: S
title: 多目标 Reward 如何做 Pareto 权衡，而不是拍一个标量权重？
quick: "把 helpfulness、safety、length、tool success 当成向量目标，先估一条近似 Pareto 前沿，再按硬约束在前沿上选部署点。固定线性加权只是一条射线，安全这类不可交换的维要进约束；汇报时要给权重敏感度和约束违反率，光报加权总分上升说明不了什么。"
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
我会把多个奖励当成一个向量，先扫出近似的 Pareto 前沿，再按产品的硬约束在前沿上选点。哪些维可以互相交换、哪些不行要先分清：安全这类不可妥协的维进约束，只有文风、格式这种可以替换的维才允许加权。汇报时只报加权总分 $r_w$ 上升，等于多目标没做完。

举个例子，代码助手同时优化 pass@k、危险命令拒绝率和平均 token 数。随手拍一个 $w$，很容易刷出又短又不可靠的补丁，总分还在涨。正确性、安全性、简洁度、工具成功率本来就不能互相换，把安全项和文风项塞进同一个 $w^\top r$，只是沿着权重射线在 Pareto 曲面上切了一个点，权重一抖，最优策略就可能跳到另一种 trade-off 上。Safe 基于人类反馈的强化学习（RLHF）把伤害写成约束，不当成再乘一个系数的可调项，拒绝的就是这种假交换；InstructGPT 也早把「有用、诚实、无害」当成要同时盯的几个目标。

## 标量化只覆盖凸包上的一条射线

多维回报写成 $r(x,y)=(r_1,\ldots,r_m)$，线性加权是

$$
r_w = w^\top r(x,y),\qquad w_i\ge 0,\ \sum_i w_i=1
$$

它对应从原点出发的一条射线 $w$，只能稳定找到凸前沿上的点，凹进去的折中，比如「中等正确、极低伤害」，会被跳过。扫一组 $w$、画两两投影，才看得见「长度再压一点，pass@k 会掉多少」。这和 `pt-adaptive-thinking-budget` 里的 quality-cost 曲线是一个逻辑，全集平均准确率涨了，可能只是每道题都写得更长了。

固定 $w$ 还有一个隐藏风险，没监控的那一维，比如 citation 忠实度、过度拒答，会在总分里被别的维补偿掉。所以要按切片设门禁，这和 `pt-safety-capability-regression` 一致。Chebyshev 或者最大最小标量化 $\min_i w_i(r_i-z_i)$ 能碰到线性加权够不着的非凸折中，但参考点 $z$ 又是一组超参。面试里要说清楚，你找的是凸包上的点，还是「每一维都待在允许范围内」的那个盒子。

最常见的假 Pareto，是把 length、latency 和 safety 放进同一个可交换的标量里。模型会用拒答或者灌水去换分，曲线看着很光滑，产品却没法用。拆法是代价维进约束，或者单独画一条 quality-cost 前沿，安全维进硬约束，只有可替换的文风、格式才加权。

## 约束优化怎么选部署点

流程上先估近似 Pareto 前沿，可以用多组权重、分层优化或者约束强化学习（RL），再按产品硬约束在前沿上切一刀。常见切法是安全当约束，其余当目标：

$$
\max_\theta\ \mathbb{E}[r_{\mathrm{help}}(x,y)]\quad\mathrm{s.t.}\quad \mathbb{E}[c_{\mathrm{safe}}(x,y)]\le\tau.
$$

拉格朗日乘子由约束违反率来调，不要事先拍死。对偶问题里 $\lambda$ 太小会漏掉约束，太大则任务能力明显下降，看着像「安全 washing」：安全集分数很好看，主任务塌了。

扫前沿时，每组 $w$ 或 $\tau$ 下至少要记各维均值、约束违反率、长度和 KL，以及有没有没监控的维在变差。上线前按业务阈值选点，比如安全违反率、P95 token，并且报告 $w$ 做小扰动以后，主指标和违反率会不会翻转。贴在拐点上的点不适合直接部署。分层优化（先满足安全，再最大化有用）实现起来简单，但第一阶段压得太狠，可行集会缩成一个只会拒答的模型，第二阶段救不回来，所以每一层都要保留另一层的 replay。

## 追问

**线性加权找不到凹前沿，怎么办？**
用约束、分层（先安全后能力）或者网格搜非凸组合。别假设加权已经覆盖了所有折中。

**约束阈值 $\tau$ 怎么定？**
相对冻结安全集上的基线违反率来定，别用「看起来安全」这种绝对感觉。和 `pt-safety-capability-regression` 一样设双门禁。

**和自适应思考预算是什么关系？**
`pt-adaptive-thinking-budget` 是质量和成本之间的 Pareto，这题是对齐目标之间的 Pareto。两边都要画曲线选部署点，都别只报加权总分。

**权重敏感度怎么报？**
对 $w$ 做小扰动，看主指标和约束违反会不会翻转。翻得厉害，说明当前点贴在拐点上。
