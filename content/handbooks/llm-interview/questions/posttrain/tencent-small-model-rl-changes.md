---
id: tencent-small-model-rl-changes
section: posttrain
order: 104
level: S
title: 腾讯 WXG：用 RL 训练小模型，相比大模型要改什么？
quick: >-
  小模型最先卡住的是 sampling 时几乎生成不了正确轨迹，稀疏奖励下整组都得零分、没有梯度方向。所以先测 pass@k 并用 SFT
  冷启动、distillation 或 rejection sampling
  把起点抬上来，再缩短或分级任务、提高验证器质量、把更新调得更保守，同时分清是能力上限还是算力不够，大模型的 recipe 不能照搬。
tags:
  - Tencent
  - WXG
  - Reasoning RL
  - Small Model
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 腾讯WXG暑期实习面经-大模型算法（候选人原帖）
    url: >-
      https://www.nowcoder.com/feed/main/detail/7a83aaa9a03e497ba925f86c9dfc5d53?sourceSSR=post
    type: candidate-first-hand
  - title: DeepSeekMath
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary-paper
---

## 真题记录

- 公司：腾讯
- 团队 / 岗位：WXG；大模型算法
- 届别 / 流程：暑期实习；三面（面委会面）
- 面试时间：原帖未披露；帖子发布于 2026-05-25
- 来源类型与可信度：牛客候选人原帖，B（公司、团队、岗位、轮次明确；届别和面试日期未披露）
- 原始措辞：**“和使用 RL 训练大模型相比，使用 RL 训练小模型需要做出哪些改变”**

小模型最先卡住的地方，往往是 sampling 时几乎生成不了正确轨迹，组内奖励方差塌成零，卡放不下倒是次要的。大模型的 recipe 是「稀疏可验证奖励 + 长链探索」，它默认 pass@$k$ 足够高，小模型没有这个前提。所以要改的是起点、任务难度、奖励质量和更新幅度。常见的错答是「小模型显存不够，换成 ZeRO-3 / LoRA」，或者「把 70B 的 GRPO 超参原样缩小」。

比如拿一个小模型直接跑竞赛数学的 GRPO，每道题采 8 条，8 条全错。组内优势全是 0，这一步算力就白花了，跑多少步都学不到东西。

## 先测可学习起点，再决定冷启动

上 RL 之前，我会先测 base 的 pass@$k$、有效奖励组比例（组内不是全对也不是全错）、格式合规率和长度分布。pass@$8$ 接近 0 的话，直接做稀疏 RL 就会得到全零优势，梯度没有方向。

这时候先做高质量的 SFT 冷启动、教师 distillation 或 rejection sampling，任务按从短到长排，或者拆成可验证的子目标。数据别拿远超学生能力的竞赛长推理过程来凑量，学生很难从里面学到有效的步骤。DeepSeek-R1 也把冷启动当成小模型能跟上 RL 的前置条件，没把它当可选项。

## 更新更保守，奖励更干净

小模型对噪声奖励和大幅度更新更脆，实际做法是用较小的 KL / clip、更低的学习率，保住探索熵，同时把格式检查和反 hacking 检查做严。验证器（verifier）的质量比一味加大组更要紧，标签错了，仅有的那点正向样本也会被学歪。生成预算缩短一点、难度分级，让组内能出现有对有错的对比。

还要分清「能力上限」和「算力或步数不够」。rollout 加长了还是全错，多半是表征能力不够；偶尔能做对、一更新就崩，那才是优化太猛。

## 同预算对照，别只看训练 reward

在同一算力下，用 base、SFT-only、RL-only、SFT+RL 四组对照 holdout。SFT 涨、RL 不涨，说明缺正向信号或奖励不可靠；两边都不涨，是容量或数据难度错配；训练 reward 涨、holdout 掉，是 hacking 或 overfitting。小模型还更容易在格式这一维「看起来在学」：合规率上去了，任务正确率不动，所以格式奖励和任务奖励要拆开看。

## 追问

**小模型能不能直接 R1-Zero？**
多数不行。没有正确轨迹时组相对优势全是 0，要先冷启动。

**参数少，是不是一定要上 LoRA？**
这是两件事。LoRA 管的是可训参数和显存，这题问的是探索覆盖。两者可以叠加，但谁也替代不了谁。

**把组加大能不能补覆盖？**
作用有限。pass@$k$ 极低时，加大 $n$ 只是多采几条失败的；降难度或加示范更有效。

**怎么判断该停下 RL、回去做 SFT？**
有效 group 比例长期过低、格式崩坏率在升、holdout 不涨，这时先修数据和冷启动，别去加大学习率。

相关：`xiaohongshu-two-stage-posttrain`、`meituan-onpolicy-no-correct-rollout`
