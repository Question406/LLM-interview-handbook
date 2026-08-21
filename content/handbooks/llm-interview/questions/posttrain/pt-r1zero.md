---
id: pt-r1zero
section: posttrain
order: 17
level: S
title: R1-Zero 为什么重要？RL 是否真的“创造”了推理？
quick: >-
  R1-Zero 展示了 strong base model 在可验证 reward 的 RL 下，即使没有传统 long-CoT cold-start
  SFT，也能显著强化 reasoning behavior；但这不能证明 RL 从零创造了 pretraining 中完全不存在的新算法。
tags:
  - DeepSeek-R1
  - Reasoning RL
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: legacy-reference
---

陷阱是两极：一边说「RL 从零发明了推理算法」，一边说「R1-Zero 只是多采样」。更稳的叙事是 **search–select–amplify**：强基座的长尾里已经偶尔能走出有用轨迹，可验证奖励把它们挑出来，策略梯度再提高这类轨迹的概率。RL 放大的是预训练里已有的搜索能力，不是在空白纸上写新算法。

## 1. R1-Zero 实际展示了什么

DeepSeek-R1-Zero 从 **base**（不是 instruction / long-CoT SFT）出发，用数学、代码一类可用规则或执行器打分的任务做大规模 RL（GRPO 族）。没有传统「先用人类或教师 CoT 做 cold-start SFT」也能把 AIME 等指标拉上去，并出现更长的反思、试错话术。

这一点重要，是因为它削弱了「推理 RL 必须先模仿一份标准 CoT 才启动」的工程教条。它**没有**证明：这些推理模式在 pretraining 语料与次词预测里完全不存在。Base 已经在海量公式、代码、解题文本上做过 next-token；RL 改的是**采样分布**，把稀有成功路径变成高频行为。

论文还记录了回复变长、自我验证话术增多，以及中英混杂等副作用。这些是搜索被放大后的表面统计，容易被讲成「模型顿悟出新算法」。更稳的读法：可验证奖励改变了**哪类轨迹被采样到**，没有在参数空间凭空插入预训练未见过的算法对象。

正式的 R1 仍然加了 cold-start 与后续对齐：可读性、语言混合、格式、安全，单靠 outcome RL 不够。Zero 是消融，不是产品终点。

## 2. 用四步机制，不要用「创造」

1. **Search。** 当前 $\pi$ 对同一题采多条长轨迹。Base 的温度采样下，正确解题、自我验证、换一种尝试，都以低概率出现。
2. **Select。** Verifier（答案核对、单测、编译）给成功轨迹高奖励，失败为 $0$ 或惩罚。信号便宜、客观、可规模化。
3. **Amplify。** 组内相对优势把成功轨迹的 token 概率抬高。这是 policy gradient，不是发现新程序空间的神谕。
4. **更好的 search。** 新策略更常进入「写长草稿、回头检查」的区域，下轮更容易再被 verifier 选中，形成正反馈。长度和「wait」一类表面统计会涨，那是放大的副作用，不是算法诞生的证据。

这可以解释：latent capability 被推到可评测的表面；test-time 计算增加；已有 primitive（代数变形、写测试、分步）被更频繁地**组合**。要声称「学到了预训练中没有的新算法」，需要更强实验：控制 pretraining 曝光、寻找真正新颖的算法泛化、分析可压缩程序结构，或做因果干预（抹掉某类数据再看 RL 能否长回来）。目前公开结果支撑不了这句大话。

## 3. 和「只是更长」怎么区分

奖励若与长度相关，模型会灌水。应用长度惩罚、在固定 token budget 下比准确率、做同长度匹配、对截断做 counterfactual，并看更高难 / 分布外的算法组合。若预算相同后增益消失，更像「买了更多搜索步数」，不是新推理法则。

Math / code 适合这套 RL，正因为 verifier 干净；开放聊天没有等价的 select，search–amplify 会放大空洞话术。把 R1-Zero 讲成「证明 RL 创造推理」，和讲成「只是温度采样」，都没抓住：它证明的是 **可验证奖励足以从 base 的长尾里把推理行为选出来并放大**，证明不了算法对象从零生成。

## 追问

- **为什么 math / code 特别适合？** 有便宜、客观、可规模化的 verifier，能做大规模 on-policy search。开放式写作缺少这一环。
- **怎么区分「更多 token」与「更好 algorithm」？** 固定 budget、长度匹配、截断对照、OOD 组合题。只看平均长度上涨不能当证据。
- **那 SFT cold-start 还有用吗？** 有。R1 用它管可读性、语言一致性和格式 prior。Zero 说明 **能力可以不靠模仿 CoT 启动**；不等于产品可以不要监督数据。
