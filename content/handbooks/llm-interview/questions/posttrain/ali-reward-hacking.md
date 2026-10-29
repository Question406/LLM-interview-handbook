---
id: ali-reward-hacking
section: posttrain
order: 9
level: A
title: Reward hacking 是什么？训练指标里怎么发现？
quick: >-
  模型钻 reward model 或规则的空子，训练奖励上涨，真实质量却在下降。要几条信号一起看：KL、输出长度、模板重复率，以及人工评价和不同 RM
  的打分是否和训练奖励出现分歧。
tags:
  - Alibaba
  - RLHF
  - Reward
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
---

Reward hacking 是模型钻 reward model 或规则的空子：训练指标一直涨，真实质量在掉。发现它要几条信号一起看，KL 异常、长度膨胀、模板刷分、人工抽检和训练奖励出现 divergence、多个 RM 之间出现分歧，盯一条奖励曲线是看不出来的。

举个例子，客服 RM 喜欢「态度好」，策略就学会每句加三段道歉和 emoji，RM 分持续新高，人工抽检却抱怨全是废话，问题解决率也在下降。这就是 hack。典型现象还有 RM score 升但人工偏好或下游任务降，输出变长、套话、格式刷分，以及对已知 RM 弱点 overfitting。所以别把 RM 曲线创新高当成 SOTA。

它和普通 overfitting 不是一回事。overfitting 是拟合训练集分布；hacking 是利用 reward function 和真实目标之间的缝隙，就算在训练分布内也会走捷径。短期 SFT 没有奖励优化，一般不叫 hacking，那是 overfitting。最容易出问题的是不可验证的偏好 RM，或者规则本身有漏洞，比如「必须包含谢谢」「越长越好」。数学、代码这类能用验证器（verifier）的任务，尽量用规则分代替纯 RM。

训练里要并行看 task success、人工盲测、安全性、长度直方图、对 $\pi_{\mathrm{ref}}$ 的 KL / 熵、模板 n-gram 重复率。长度右移、KL 又突然抬升，是很强的信号。训练 RM 在涨，held-out RM 或 rule score 在降，说明模型在钻单一判官的空子。只盯 RM 做 early stop，会把 hack 出来的策略当成最优。组内相对奖励也能被 hack：大家都变长之后 $\sigma$ 变小，看着很稳定，其实在刷同一个模板。Agent 的终局奖励更粗，更要拆出过程约束，见 `ali-agent-final-reward`。

缓解靠约束加可验证奖励：KL / 熵约束和长度惩罚，多奖励集成，定期换或重训 RM，可验证任务用 rule / verifier 替代纯 RM。回到客服的例子，应该把「是否解决」的规则分和态度分拆开，免得态度分把任务吃掉；再定期换一批盲测题重训 RM，防止策略 overfitting 旧判官。发现 hack 之后先冻住策略做人工归因，再改奖励，别加大学习率「冲过去」。GRPO 的 KL 项见 `ali-grpo-loss`，分数尺度见 `data-reward-calibration`。

## 追问

**KL 大一定是 hack 吗？**
不一定，也可能是在学新能力。要对照人工评价和下游任务看，单看 KL 下不了结论。

**为什么 verifier 更抗 hack？**
单元测试、规则通过与否很难靠套话伪造。不过还是要防刷格式、空实现这类漏洞。

**长度惩罚会伤推理吗？**
会。惩罚应该打在「无效重复」上，别一刀切地要求变短；推理任务看的是正确率，跟字数无关。
