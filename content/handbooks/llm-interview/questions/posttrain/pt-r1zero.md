---
id: pt-r1zero
section: posttrain
order: 17
level: S
title: R1-Zero 为什么重要？RL 是否真的“创造”了推理？
quick: "R1-Zero 说明强基座不先做长 CoT 冷启动 SFT，靠可验证奖励的 RL 也能把推理行为显著放大。机制是 search-select-amplify：base 长尾里偶尔走出的好轨迹被 verifier 挑出来再提权，这证明不了 RL 从零创造了预训练里完全没有的新算法。"
tags:
  - DeepSeek-R1
  - Reasoning RL
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: legacy-reference
---

R1-Zero 重要，是因为它说明强基座不先模仿一份长 CoT，单靠可验证奖励的强化学习（RL）就能把推理行为拉起来。但它证明的是放大，证明不了创造：base 的长尾里本来就偶尔能走出有用的轨迹，奖励把它们挑出来，策略梯度再把它们的概率抬高。

具体看它做了什么。DeepSeek-R1-Zero 从 base 出发，没有经过 instruction 或 long-CoT 监督微调（SFT），用数学、代码这类能靠规则或执行器打分的任务做大规模 RL（GRPO 族）。没有传统的「先用人类或教师 CoT 做 cold-start SFT」，AIME 等指标也拉了上去，还出现了更长的反思和试错话术。这削弱了「推理 RL 必须先模仿一份标准 CoT 才能启动」这条工程教条。

为什么说是放大。base 已经在海量公式、代码、解题文本上做过 next-token 预测，RL 改的是采样分布，把稀有的成功路径变成高频行为。可以按四步讲。先是 search：当前 $\pi$ 对同一题采多条长轨迹，温度采样下，正确解题、自我验证、换一种尝试都以低概率出现。然后 select：verifier（答案核对、单测、编译）给成功轨迹高奖励，失败给 $0$ 或惩罚，这种信号便宜、客观、能规模化。接着 amplify：组内相对优势把成功轨迹的 token 概率抬高，这就是普通的 policy gradient，它不是发现新程序空间的神谕。最后是更好的 search：新策略更常进入「写长草稿、回头检查」的区域，下一轮更容易再被 verifier 选中，形成正反馈。

论文里记录的回复变长、自我验证话术增多、中英混杂这些副作用，都是搜索被放大后的表面统计，长度和「wait」一类词的频率会涨，很容易被讲成「模型顿悟出新算法」。稳一点的读法是：可验证奖励改变了哪类轨迹会被采到，没有在参数空间凭空插入预训练没见过的算法对象。这套机制能解释 latent capability 被推到可评测的表面、test-time 计算变多、已有的 primitive（代数变形、写测试、分步）被更频繁地组合。要声称学到了预训练里没有的新算法，需要更强的实验：控制 pretraining 曝光、找真正新颖的算法泛化、分析可压缩的程序结构，或者做因果干预，抹掉某类数据再看 RL 能不能长回来。目前公开的结果撑不起这句话。

还得排除「只是写得更长」。奖励和长度相关时模型会灌水，所以要加长度惩罚、在固定 token budget 下比准确率、做同长度匹配、对截断做 counterfactual，再看更难的、分布外的算法组合题。预算拉平后增益消失，更像是买了更多搜索步数，谈不上新的推理法则。

最后，正式的 R1 仍然加了 cold-start 和后续对齐，处理可读性、语言混合、格式和安全，单靠 outcome RL 不够。Zero 是一个消融实验，离产品终点还远。math / code 适合这套方法，正因为 verifier 干净；开放聊天没有同等的 select 环节，search-amplify 会把空洞话术一起放大。

## 追问

**为什么 math / code 特别适合？**
因为有便宜、客观、能规模化的 verifier，可以做大规模 on-policy search。开放式写作缺这一环。

**怎么区分「更多 token」和「更好的算法」？**
固定 budget，做长度匹配和截断对照，再上分布外数据（OOD，即与训练数据明显不同的数据）的组合题。只看平均长度上涨不能当证据。

**有人说 R1-Zero 只是多采样，怎么回？**
这也说偏了。温度采样只对应 search 那一步，R1-Zero 还有 select 和 amplify，把选出来的行为写进了参数，下次采样时这类轨迹本身就更常出现。它证明的是可验证奖励足以从 base 的长尾里把推理行为选出来并放大。

**那 SFT cold-start 还有用吗？**
有。R1 用它管可读性、语言一致性和格式 prior。Zero 说明能力可以不靠模仿思维链（CoT，即分步推理过程）启动，产品照样需要监督数据。
