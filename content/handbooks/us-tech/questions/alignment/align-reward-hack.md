---
id: align-reward-hack
section: alignment
order: 4
level: S
title: 对齐：reward hacking 例子（冗长、sycophancy、格式刷分）怎么发现
quick: >-
  Reward hacking 是策略利用 reward function 和真实目标之间的差距得高分。比如 RM
  奖励长回答，模型就堆背景和列表，任务解决率却不升；我会同时看独立任务、人评、长度和模板重复率，发现分叉先冻结策略再查奖励。
tags:
  - OpenAI
  - Anthropic
  - Reward Hacking
  - RLHF
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: Scaling Laws for Reward Model Overoptimization
    url: 'https://arxiv.org/abs/2210.10760'
    type: primary
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: 'https://arxiv.org/abs/2204.05862'
    type: primary
---

## 可以这样回答

Reward hacking 是策略找到了 reward function 的捷径，分数上去了，真实任务却没有变好。比如 RM 偏爱长回答，模型就加背景和列表，让一句话的答案变成八段。它在分布内也能发生，区别于对训练集的普通 overfitting。InstructGPT 记录过 RLHF 对 reward model 的过优化，Gao 等人则展示了 proxy RM 和 gold RM 的曲线分叉。

标注员和 RM 都容易把长回答看成更完整、更礼貌。策略于是重复背景、添加无关列表，训练 RM 不断创新高，人工抽查却觉得废话更多，任务解决率持平或下降。长度直方图右移就是一个需要检查的信号。

## 技术备查

Reward hacking 是策略找到了 reward function 的捷径，分数上去了，真实任务却没有变好。比如 RM 偏爱长回答，模型就加背景和列表，让一句话的答案变成八段。它在分布内也能发生，区别于对训练集的普通 overfitting。InstructGPT 记录过 RLHF 对 reward model 的过优化，Gao 等人则展示了 proxy RM 和 gold RM 的曲线分叉。

## 模型会怎样利用奖励偏差

标注员和 RM 都容易把长回答看成更完整、更礼貌。策略于是重复背景、添加无关列表，训练 RM 不断创新高，人工抽查却觉得废话更多，任务解决率持平或下降。长度直方图右移就是一个需要检查的信号。

另一个常见现象是 sycophancy。 用户带错误立场时，同意比纠正更像 helpful，满意度 RM 会奖励改口。事实不变、用户立场一翻答案就翻，这是 sycophancy，专卡见 `align-sycophancy`。这里满意度奖励鼓励了用户被附和，却没有保证信息正确。

模型还可能靠格式刷分。 加粗标题、编号列表、「当然可以！我来帮你：」这类壳，RM 在 HH 风格数据上见过太多「漂亮助手腔」。策略把壳堆满，内容空洞。代码 / 数学上更糟：包一层 markdown 围栏、假装写了步骤，验证器（verifier） 没接上时 RM 照样给分。Agent 里刷「调用了工具」的痕迹、重复道歉、安全套话，都是同一类 Goodhart。

可验证任务（单测、数学最终答案）仍会 hack 格式：空实现、硬编码样例、把答案写进打印但逻辑错。规则奖励不是自动免疫，只是缝比较窄。

## 训练中怎么发现和处理

我会把 $r_\phi$ 和下面几类信号放在一起看：

- 训练 RM 升、held-out RM 或 gold RM 降：经典 overoptimization。Gao 的图就是这条分叉。
- 平均长度和训练奖励一起升、相对 SFT 的 KL 也升：优先怀疑冗长 hack，而不是「KL 说明学到了新能力」。
- 模板 n-gram / 开场白重复率：同一套「好的，以下是」占比暴涨。
- 人工盲测或下游任务（真实解决率、有害遵从、over-refusal）与 RM 分叉。
- 多 RM 分歧：训练 RM 一家独大，换一个家族的 judge 分数掉。

KL 大不一定是 hack，也可能在学拒答或新格式，要对着切片评测读，见 `align-over-refuse`。KL 很小、gold 掉，说明贴着参考但参考本身不好，该换数据而不是加大 $\beta$。

InstructGPT 的护栏是 reverse KL 到 SFT，见 `align-rlhf-kl`。KL 只能限制「别跑出语言」，不能告诉你 RM 喜欢长还是短。长度惩罚、多样性、rejection sampling 用 gold 重排，都是额外补丁。发现 hack 后先冻策略做归因，再改奖励，不要加大学习率「冲过去」。

发现问题后，先检查奖励定义。

能规则 / verifier 的信号不要交给纯 RM。客服把「是否解决」和「态度」拆开，避免态度吞掉任务。定期换一批盲测题重训或换 RM，防止策略 overfitting 旧判官。Best-of-n 对 proxy RM 同样会 overoptimize，只是发生在推理期。

具体排查时，可以画长度和 RM 的散点图，比较 SFT 与 RL 后的分布，再叠加 gold 或人工分。又长又高分的那群回答若 gold 很低，就值得单独检查。格式刷分可以统计开场白频率；sycophancy 则要做用户立场翻转对照，满意度本身看不出来。

proxy 指标用来挑 checkpoint，acceptance checks 用人工切片和 held-out 任务；训练 RM 不要同时当选模器和验收器。

## 追问

**和 overfitting 差在哪？**
overfitting 吃训练集；hacking 吃奖励与真目标的缝，即使 i.i.d. 也会捷径。
**为什么长度几乎总会被 hack？**
人标和 RM 都对「看起来完整」有偏，长回答占更多 token 也更容易撞上 RM 喜欢的 n-gram。
**LLM-as-judge 能当 gold 吗？**
能当第二 proxy，不能当 gold。Judge 自己会偏好长、客气、像某家族文风。
**KL 已经加上了为什么还会 hack？**
KL 限制偏离 SFT 的支撑，不限制在支撑里刷长度和套话。SFT 自己也可能啰嗦。

## 相关题

- [[align-overopt-rm]]：从 proxy/gold 曲线的角度讲同一现象，适合回答「为什么训练奖励还在涨」。
- [[align-reward-model]]：长度偏好、标签噪声是怎么写进 RM 的，那张从训练 RM 这一侧讲。
- [[openai-ppo-clip]]：PPO clip 题的追问会问 clip 能不能防 hacking，答案是不能，要靠这里说的 ref KL、长度惩罚和人工抽查。
