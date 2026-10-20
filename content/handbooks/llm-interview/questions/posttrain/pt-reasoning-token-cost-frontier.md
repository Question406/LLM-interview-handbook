---
id: pt-reasoning-token-cost-frontier
section: posttrain
order: 41
level: S
title: 如何在 RL / 偏好训练里惩罚无效 thinking，并测量其边际收益？
quick: "区别于「自适应预算控制器」：这里直接把无效推理当作可优化目标。给不提高解题质量的推理 token 增加代价，并用固定预算消融估计每多花 $k$ token 的准确率边际收益。"
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

`pt-adaptive-thinking-budget` 管推理时决定想多久；本题管训练目标如何让模型少生成无效的分步推理（CoT）。策略会刷长思维骗过程奖励或格式分，要把质量-成本写成可训信号。

## 训练信号

常见形状：

$$
r = r_{\mathrm{correct}} - \lambda\cdot \mathrm{len}_{\mathrm{think}}
$$

或只在答错时允许更长思考（对了就短）。对重复句、自言自语循环给显式负分。配对偏好可构造「同正确、更短 thinking」为胜者。$\lambda$ 过大模型会删关键步骤；过小长度 hacking 继续。$\lambda$ 应随训练退火或按难度条件化，而不是全局常数。

## 测量边际收益

同一 checkpoint 上对预算 $B\in\{B_1,\ldots,B_m\}$ 强制截断 / 扩写 thinking，画 $\mathrm{accuracy}(B)$ 与 $\mathrm{cost}(B)$。边际收益是

$$
\frac{\Delta\mathrm{acc}}{\Delta\mathbb{E}[\text{tokens}]}.
$$

曲线很快变平，说明额外 token 多数没有带来解题收益。训练中盯「长度↑且验证集持平」。评估必须用无长度偏置的裁判或可执行答案，避免「写得长 = 看起来认真」。

## 例子

数学强化学习（RL） 加轻度长度惩罚后，简单题平均 thinking 从 800 降到 200 token 而准确率不变，难题仍保留很长的推理过程。惩罚打中了无效 token，而不是伤到必要搜索。这和 long-to-short 蒸馏互补：蒸馏换模型，本题改同一策略的目标。

## 追问

- **最终结果-only 也会自发变长？** 会。探索和「多写一点碰对」都会拉长；过程奖励 更容易诱发空洞过程。
- **和 test-time compute 冲突吗？** 不冲突。训练出成本意识后，推理仍可用预算控制器在难题上加 token。
- **$\lambda$ 怎么定？** 先画 frontier，把 $\lambda$ 选在边际收益明显下降的拐点，再按题型分层。
