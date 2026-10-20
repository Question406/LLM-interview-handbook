---
id: tencent-small-model-rl-changes
section: posttrain
order: 104
level: S
title: 腾讯 WXG：用 RL 训练小模型，相比大模型要改什么？
quick: "小模型的初始成功率与 exploration coverage 往往更低，直接用稀疏奖励做强化学习，容易所有样本都得零分；先提高可学习起点，再缩短 / 分级任务、提高验证器质量、调小更新激进度，并区分能力上限和算力不足，不能照搬大模型 recipe。"
tags:
  - Tencent
  - WXG
  - Reasoning RL
  - Small Model
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯WXG暑期实习面经-大模型算法（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/7a83aaa9a03e497ba925f86c9dfc5d53?sourceSSR=post
    type: candidate-first-hand
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary-paper
---

## 真题记录

- 公司：腾讯
- 团队 / 岗位：WXG；大模型算法
- 届别 / 流程：暑期实习；三面（面委会面）
- 面试时间：原帖未披露；帖子发布于 2026-05-25
- 来源类型与可信度：牛客候选人原帖，B（公司、团队、岗位、轮次明确；届别和面试日期未披露）
- 原始措辞：**“和使用强化学习训练大模型相比，使用强化学习训练小模型需要做出哪些改变”**

常见误区是：「小模型显存不够，换成 ZeRO-3 / LoRA」或「把 70B 的 GRPO 超参原样缩小」。小模型的首要瓶颈往往是采样时几乎生成不了正确轨迹，组内奖励方差塌成零，而不是卡放不下。大模型 recipe 里「稀疏可验证奖励 + 长链探索」默认存在足够 pass@$k$；小模型没有这个前提。

## 先测可学习起点，再决定冷启动

上 RL 前先测 base 的 pass@$k$、有效奖励组比例（组内不全对/全错）、格式合规率和长度分布。若 pass@$8$ 接近 0，直接稀疏 RL 会全零优势，梯度没有方向。此时优先高质量 SFT 冷启动、教师蒸馏或拒绝采样，并按短到长安排任务，或把任务拆成可验证子目标。数据不要用远超学生模型能力的竞赛长推理过程凑数据量，学生很难从中学到有效步骤。DeepSeek-R1 也把冷启动当作小模型能跟上 RL 的前置，而不是可选项。

## 更新更保守，奖励更干净

小模型对噪声奖励和大幅度更新更脆。实务上用较小 KL / clip、更低学习率、保持探索熵，并加强格式与反 hacking 检查。Verifier 质量比盲目加大组更重要：错误标签会把仅有的正向样本学歪。缩短生成预算、分级难度，让组内能出现对/错对比。区分「能力上限」和「算力/步数不够」：加长 rollout 仍全错，多半是表征不够；偶尔能对但更新后崩，才是优化过猛。

## 同预算对照，不要只看训练 reward

用 base、SFT-only、RL-only、SFT+RL 在同一算力下对照 holdout。SFT 涨、RL 不涨 → 缺正向信号或奖励不可靠；两者都不涨 → 容量或数据难度错配；训练 reward 涨、holdout 掉 → hacking 或过拟合。小模型还更容易在格式维「看起来在学」：合规率升但任务正确率不动，要把格式奖励和任务奖励拆开看。相关卡：`xiaohongshu-two-stage-posttrain`、`meituan-onpolicy-no-correct-rollout`。

## 追问

- **小模型能不能直接 R1-Zero？** 多数不行。没有正确轨迹时组相对优势全是 0，应先冷启动。
- **是不是参数少所以一定要 LoRA？** 不是同一件事。LoRA 管可训参数和显存；本题管探索覆盖。两者可叠加，但不要互相替代。
- **组大小加大能不能补覆盖？** 有限。若 pass@$k$ 极低，加大 $n$ 只是多采失败；更有效的是降难度或加示范。
- **怎么判断该停 RL 回去 SFT？** 有效 group 比例长期过低、格式崩坏率升、holdout 不涨时，先修数据和冷启动，而不是加大学习率。
