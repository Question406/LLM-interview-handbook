---
id: pt-gfpo
section: posttrain
order: 253
level: S
title: GFPO 怎么用组内过滤压长度膨胀？和 DAPO overlong 差在哪？
quick: "GFPO 每道题多采一些，先按长度或 reward-per-token 滤掉冗长的回复，只在留下的回复上算组优势。DAPO overlong 改的是奖励，GFPO 改的是谁进梯度，长度不进标量奖励，也就不和正确率抢权重。"
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

GFPO 的做法是每道题多采一些，先把冗长的回复滤掉，只在留下来的短而有效的回复上算组优势，这样推理默认就变短了。它和 DAPO overlong 的区别在动的那一层：DAPO 改奖励，给超长加软惩罚；GFPO 改的是谁进梯度，奖励本身只看任务分。

GRPO 之后回答变长，不全是因为「更会思考」了。很多 token 是重复、套话，对正确率没贡献，见 `sys-rl-longer-after-rl`、`data-length-hacking`。比如一道题两条回答都对，一条把同一步检查反复写了好几遍，GRPO 照样给它正优势。GFPO（`2508.09726`）要把这种「正确但灌水」的回答挡在梯度外面。百度面经会把它和 DAPO、GSPO 并列着问，别答成又一个 clip 公式。

## 先滤，再算组优势

同一道题采一个更大的组，过滤键常见两种：一种按长度，留下更短的正确（或更高分）的回复；一种按 token 效率 $R/|y|$，同样的分数，越短越值钱。过滤之后，只在剩下的回复上算 $\hat A_i=(R_i-\mu)/(\sigma+\epsilon)$。长度没进标量奖励，所以不会和正确率抢权重，也不会出现「长度惩罚把该写的证明写没了」。Adaptive Difficulty 变体按当前难度把探索预算多分给难题，和动态采样是同一类课程设计，见 `pt-dapo`、`data-rlvr-select`。

论文标题里那句 sample more to think less 就是它的取舍：训练时的实际耗时略涨，换来的是部署时的延迟下降。论文报告长度膨胀砍掉了一大截、准确率基本保住；具体数字随模型和题集变化，面试讲机制就行，别背百分比。

过滤也不能太狠，会把多样化的正确推理链滤没了，$G$ 名义上很大，有效组可能还是全对。要盯平均长度、holdout pass@1 和被滤掉的比例，光说「我们开了 GFPO」不够。

## 和谁容易混

| | 动哪一层 | 长度怎么进目标 |
| --- | --- | --- |
| DAPO overlong | 奖励 shaping | 超长软惩罚，截断不再一刀零分 |
| 长度惩罚系数 | 标量 $R$ | 和任务分抢权重，容易提前收束 |
| Long-to-short 蒸馏 | 监督信号 | 已经会的长 思维链（CoT，即分步推理过程） 压给学生，见 `pt-long-to-short-reasoning` |
| GFPO | 谁进梯度 | 组内先滤，优势仍只看任务 $R$ |

Dr.GRPO 修的是 std 和长度归一化带来的估计偏置，见 `pt-drgrpo`；GFPO 修的是「正确但灌水」还能拿正优势。两者可以叠加使用。

## 追问

**错了但很短的回答要留吗？**
过滤要按「先对再短」或者效率键来做，别变成最短错误答案的比赛。

**和 SimKO 什么关系？**
SimKO 保的是 next-token 的 support，防止 pass@K 塌，见 `pt-grpo-family-sapo-simko`；GFPO 压的是长度。一个管多样性，一个管 token 预算。

**组过滤完只剩 1 条怎么办？**
优势没法定义。过滤后仍要 $\ge 2$ 条，不够就让这道题这一步不更新。
