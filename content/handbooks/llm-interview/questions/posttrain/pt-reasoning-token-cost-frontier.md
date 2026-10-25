---
id: pt-reasoning-token-cost-frontier
section: posttrain
order: 41
level: S
title: 如何在 RL / 偏好训练里惩罚无效 thinking，并测量其边际收益？
quick: "在奖励里给不提高解题质量的推理 token 加代价，比如 $r = r_{\\mathrm{correct}} - \\lambda\\cdot \\mathrm{len}_{\\mathrm{think}}$，或构造「同样正确、思考更短」的偏好对。边际收益用同一 checkpoint 的固定预算消融来测，估每多花 $k$ token 准确率涨多少，$\\lambda$ 选在拐点附近。"
tags:
  - Reasoning
  - RL
  - Token Cost
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Training Language Models to Reason Efficiently
    url: https://arxiv.org/abs/2502.04463
    type: primary
---

做法分两步：训练时在奖励里给无效推理 token 加代价，测量时在同一个 checkpoint 上强制不同的思考预算，看每多花一些 token 准确率涨多少。推理时决定想多久的是 `pt-adaptive-thinking-budget`，这题讲的是改训练目标，让模型本身少写无效的分步推理（CoT）。

要管这件事，是因为策略会刷长思维去骗过程奖励或格式分，所以得把质量和成本写成能训的信号。最常见的奖励形状是

$$
r = r_{\mathrm{correct}} - \lambda\cdot \mathrm{len}_{\mathrm{think}}
$$

也可以只在答错时允许思考更长，答对就要求短；对重复句、自言自语的循环给显式负分。偏好训练里可以把「同样正确、thinking 更短」的那条当胜者。$\lambda$ 过大，模型会删掉关键步骤；过小，长度 hacking 会继续。所以 $\lambda$ 最好随训练退火，或者按难度做条件化，一个全局常数通常不够。

测边际收益时，对预算 $B\in\{B_1,\ldots,B_m\}$ 强制截断或扩写 thinking，画出 $\mathrm{accuracy}(B)$ 和 $\mathrm{cost}(B)$。边际收益是

$$
\frac{\Delta\mathrm{acc}}{\Delta\mathbb{E}[\text{tokens}]}.
$$

曲线很快变平，说明额外的 token 大多没带来解题收益。训练中要盯「长度在涨、验证集持平」这个信号。评估要用无长度偏置的裁判或可执行答案，免得「写得长」被当成「认真」。

举个例子，数学强化学习（RL）加了轻度长度惩罚以后，简单题的平均 thinking 从 800 降到 200 token，准确率不变，难题仍保留很长的推理过程。这说明惩罚打中的是无效 token，必要的搜索没被伤到。它和 long-to-short 蒸馏互补：蒸馏是换一个模型，这里改的是同一个策略的目标。

## 追问

**只给最终结果奖励，也会自发变长吗？**
会。探索和「多写一点碰对」都会拉长输出；过程奖励更容易诱发空洞过程。

**和 test-time compute 冲突吗？**
不冲突。训练出成本意识以后，推理时仍然可以用预算控制器在难题上多给 token。

**$\lambda$ 怎么定？**
先画 frontier，把 $\lambda$ 选在边际收益明显下降的拐点，再按题型分层调。
