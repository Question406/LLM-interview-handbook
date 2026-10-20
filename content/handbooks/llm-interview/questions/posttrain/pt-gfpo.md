---
id: pt-gfpo
section: posttrain
order: 253
level: S
title: GFPO 怎么用组内过滤压长度膨胀？和 DAPO overlong 差在哪？
quick: "GFPO 每题多采样，先按长度或 reward-per-token 滤掉冗长回复，只在保留的回复上算组优势。DAPO overlong 改的是奖励，GFPO 改的是谁进梯度。"
tags:
  - GFPO
  - GRPO
  - Length
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: Sample More to Think Less — Group Filtered Policy Optimization for Concise Reasoning
    url: https://arxiv.org/abs/2508.09726
    type: primary
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary
---

GRPO 之后回答变长，不全是「更会思考」。很多 token 是重复、套话、对正确率没贡献的填料，见 `sys-rl-longer-after-rl`、`data-length-hacking`。GFPO（`2508.09726`）的点是：训练时多采样，只拿短且有效的轨迹更新，让推理默认变短。百度面经会把它和 DAPO / GSPO 并列，不要答成又一个 clip 公式。

## 先滤，再算组优势

同一题采一个更大的组。过滤键常见两种：

- **长度。** 留下更短的正确（或更高分）回复。
- **token 效率。** $R/|y|$，同样的分更短的更值钱。

过滤之后，只在幸存者上做 $\hat A_i=(R_i-\mu)/(\sigma+\epsilon)$。长度没有进标量奖励，避免和正确率抢权重、也避免「长度惩罚把该写的证明写没」。Adaptive Difficulty 变体按当前难度把探索预算分给更难的题，和动态采样是同一类课，见 `pt-dapo`、`data-rlvr-select`。

现场口令：sample more to think less。训练实际耗时略涨，换的是部署延迟。论文报过长度膨胀砍掉一大截、准确率基本保住；数字随模型和题集变，面试讲机制，不要背百分比。

## 和谁不要混

| | 动哪一层 | 长度怎么进目标 |
| --- | --- | --- |
| DAPO overlong | 奖励 shaping | 超长软惩罚，截断不再一刀零分 |
| 长度惩罚系数 | 标量 $R$ | 和任务分抢权重，容易提前收束 |
| Long-to-short 蒸馏 | 监督信号 | 已经会的长 思维链（CoT，即分步推理过程） 压给学生，见 `pt-long-to-short-reasoning` |
| GFPO | 谁进梯度 | 组内先滤，优势仍只看任务 $R$ |

Dr.GRPO 修的是 std / 长度归一化的估计偏置，见 `pt-drgrpo`。GFPO 修的是「正确但灌水」仍拿正优势。可以叠，不是二选一。

过滤过狠会把多样化的正确链滤没，$G$ 名义上很大、有效组仍可能全对。要盯平均长度、holdout pass@1、以及滤掉比例。只报「我们开了 GFPO」不够。

## 追问

- **错但很短的要留吗？** 过滤应在「先对后短」或效率键上，不要变成最短错误答案竞赛。
- **和 SimKO？** SimKO 保 next-token support，防 pass@K 塌，见 `pt-grpo-family-sapo-simko`。GFPO 压的是长度。一个管多样性，一个管 token 预算。
- **组滤完 $G$ 变 1 怎么办？** 优势未定义。过滤后仍要 $\ge 2$，或回退到这题本步不更新。
