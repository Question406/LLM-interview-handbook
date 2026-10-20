---
id: align-reward-hack
section: alignment
order: 4
level: S
title: 对齐：reward hacking 例子（冗长、谄媚、格式刷分）怎么发现
quick: "策略可能利用 RM 或规则与真实目标的差异，通过冗长、逢迎或固定格式拿高分，却没有解决问题。对比训练 RM、人工和 held-out RM 的评分，同时检查长度、模板重复率和 ref KL，不能只看训练奖励上涨。"
tags:
  - OpenAI
  - Anthropic
  - Reward Hacking
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Scaling Laws for Reward Model Overoptimization
    url: https://arxiv.org/abs/2210.10760
    type: primary
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: https://arxiv.org/abs/2204.05862
    type: primary
---

OpenAI 对齐岗爱问「RM 曲线很好，你为什么停」。InstructGPT 自己写了 基于人类反馈的强化学习（RLHF） 会 overoptimize 奖励模型；Gao 等人后来把 proxy RM 和 gold RM 的分叉画成标量。这块容易把 hacking 说成普通过拟合。过拟合是吃训练集；hacking 是吃奖励函数和真目标的缝，分布内也会走捷径。

## 三个面试够用的例子

**冗长。** 标注员和 RM 都更容易给长回答高分：看起来更全、更礼貌、更「像助手」。策略学会重复背景、加无关列表、把一句话拆成八段。训练 RM 分持续新高，人工抽检抱怨废话，任务解决率不动或下降。长度直方图右移是第一信号，不是「学得更认真」。

**谄媚。** 用户带错误立场时，同意比纠正更像 helpful，满意度 RM 会奖励改口。事实不变、用户立场一翻答案就翻，这是 sycophancy，专卡见 `align-sycophancy`。Hacking 角度：你优化的是「用户喜欢被同意」，不是「用户得到对的信息」。

**格式刷分。** 加粗标题、编号列表、「当然可以！我来帮你：」这类壳，RM 在 HH 风格数据上见过太多「漂亮助手腔」。策略把壳堆满，内容空洞。代码 / 数学上更糟：包一层 markdown 围栏、假装写了步骤，验证器（verifier） 没接上时 RM 照样给分。Agent 里刷「调用了工具」的痕迹、重复道歉、安全套话，都是同一类 Goodhart。

可验证任务（单测、数学最终答案）仍会 hack 格式：空实现、硬编码样例、把答案写进打印但逻辑错。规则奖励不是自动免疫，只是缝比较窄。

## 怎么在训练里发现，而不是事后背锅

并行盯一组曲线，不要只盯 $r_\phi$：

- 训练 RM 升、held-out RM 或 gold RM 降：经典 overoptimization。Gao 的图就是这条分叉。
- 平均长度和训练奖励一起升、相对 监督微调（SFT） 的 KL 也升：优先怀疑冗长 hack，而不是「KL 说明学到了新能力」。
- 模板 n-gram / 开场白重复率：同一套「好的，以下是」占比暴涨。
- 人工盲测或下游任务（真实解决率、有害遵从、过度拒绝）与 RM 分叉。
- 多 RM 分歧：训练 RM 一家独大，换一个家族的 judge 分数掉。

KL 大不一定是 hack，也可能在学拒答或新格式，要对着切片评测读，见 `align-over-refuse`。KL 很小、gold 掉，说明贴着参考但参考本身不好，该换数据而不是加大 $\beta$。

InstructGPT 的护栏是反向 KL 到 SFT，见 `align-rlhf-kl`。KL 只能限制「别跑出语言」，不能告诉你 RM 喜欢长还是短。长度惩罚、多样性、拒绝采样用 gold 重排，都是额外补丁。发现 hack 后先冻策略做归因，再改奖励，不要加大学习率「冲过去」。

## 缓解怎么说才不像空话

能规则 / verifier 的信号不要交给纯 RM。客服把「是否解决」和「态度」拆开，避免态度吞掉任务。定期换一批盲测题重训或换 RM，防止策略过拟合旧判官。Best-of-n 对 proxy RM 同样会 overoptimize，只是发生在推理期。

我会画一张长度 vs RM 散点：SFT 是一团，强化学习（RL） 之后变成「又长又高分」的角。再叠 gold 或人工分，角上的点 gold 很低，就是 hack 集群。格式刷分用开场白计数器就能抓；谄媚必须做立场翻转对照，单看满意度看不出来。

proxy 指标用来挑 checkpoint，门禁用人工切片和 held-out 任务；训练 RM 不要同时当选模器和验收器。

## 追问

- **和过拟合差在哪？** 过拟合吃训练集；hacking 吃奖励与真目标的缝，即使 i.i.d. 也会捷径。
- **为什么长度几乎总会被 hack？** 人标和 RM 都对「看起来完整」有偏，长回答占更多 token 也更容易撞上 RM 喜欢的 n-gram。
- **LLM-as-judge 能当 gold 吗？** 能当第二 proxy，不能当 gold。Judge 自己会偏好长、客气、像某家族文风。
- **KL 已经加上了为什么还会 hack？** KL 限制偏离 SFT 的支撑，不限制在支撑里刷长度和套话。SFT 自己也可能啰嗦。

## 相关题

- [[align-overopt-rm]]：从 proxy/gold 曲线的角度讲同一现象，适合回答「为什么训练奖励还在涨」。
- [[align-reward-model]]：长度偏好、标签噪声是怎么写进 RM 的，那张从训练 RM 这一侧讲。
- [[openai-ppo-clip]]：PPO clip 题的追问会问 clip 能不能防 hacking，答案是不能，要靠这里说的 ref KL、长度惩罚和人工抽查。
