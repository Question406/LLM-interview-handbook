---
id: ali-reward-hacking
section: alibaba
order: 9
level: A
title: Reward hacking 是什么？训练指标里怎么发现？
quick: 模型钻奖励模型/规则空子，指标上涨但真实质量下降。看 KL 异常、长度膨胀、模板刷分、人工抽检 divergence、多 RM 分歧。
tags:
  - Alibaba
  - RLHF
  - Reward
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
---

这块容易直接答成把 RM 曲线新高当成 SOTA，或把 hacking 说成普通过拟合。Reward hacking 是模型钻奖励模型或规则的空子，训练指标上涨但真实质量下降。典型现象：RM score 升但人工偏好 / 下游任务降；输出变长、套话、格式刷分；对已知 RM 弱点过拟合。发现要靠 KL 异常、长度膨胀、模板刷分、人工抽检 divergence、多 RM 分歧，不能只看一条奖励曲线。GRPO 的 KL 项见 `ali-grpo-loss`，分数尺度见 `data-reward-calibration`。

## 指标涨、质量掉

适用条件：不可验证的偏好 RM，或规则有漏洞（「必须包含谢谢」「越长越好」）。数学 / 代码等可用 verifier 的任务，应尽量用规则分替代纯 RM。短 SFT 没有奖励优化，一般不叫 hacking，那是过拟合。过拟合是拟合训练集分布；hacking 是利用奖励函数与真实目标的缝隙，即使在训练分布内也会走捷径。客服 RM 喜欢「态度好」，策略学会每句加三段道歉和 emoji，RM 分持续新高，人工抽检却抱怨废话、问题解决率下降。这就是 hack，不是「对齐成功」。

## 怎么在训练里发现

并行看：task success、人工盲测、安全性、长度直方图、对 $\pi_{\mathrm{ref}}$ 的 KL / 熵、模板 n-gram 重复率。长度右移且 KL 突然抬升，是强信号。多 RM 分歧：训练 RM 升、held-out RM 或 rule score 降，说明在钻单一判官。只盯 RM 做 early stop，会把黑客策略当成最优。组内相对奖励也会被hack：大家都变长之后 $\sigma$ 变小，看起来稳定，其实在刷同一模板。Agent 终局奖励更粗，更要拆过程约束，见 `ali-agent-final-reward`。

## 缓解：约束 + 可验证奖励

KL / 熵约束与长度惩罚；多奖励集成、定期换 / 重训 RM；可验证任务用 rule / verifier 代替纯 RM。客服应把「是否解决」规则分和态度分拆开，避免态度吞掉任务。定期换一批盲测题重训 RM，防止策略过拟合旧判官。发现 hack 后先冻策略做人工归因，再改奖励，而不是加大学习率「冲过去」。

## 追问

- **和过拟合差在哪？** 过拟合吃训练集；hacking 吃奖励与真目标的缝，分布内也会捷径。
- **KL 大一定是 hack 吗？** 不一定，也可能在学新能力。要对照人工与下游，不单看 KL。
- **为何 verifier 更抗 hack？** 单元测试 / 规则通过与否难靠套话伪造；仍要防刷格式、空实现。
- **长度惩罚会伤推理吗？** 会。应对「无效重复」惩罚，而不是一刀切短；推理任务看正确率不是字数。
