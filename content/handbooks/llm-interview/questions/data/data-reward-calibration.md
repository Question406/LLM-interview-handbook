---
id: data-reward-calibration
section: data
order: 14
level: S
title: Reward Model / Judge 的 rank accuracy 高，为什么还要看 calibration？
quick: "排序正确率只判断谁的分数更高；校准（calibration）还要判断预测置信度是否可靠，例如置信度为 0.9 的判断是否约有 90% 正确。当分数用于阈值、拒答、采样或强化学习（RL）时，分数尺度的偏差会直接影响决策。"
tags:
  - Reward Model
  - Calibration
  - Eval
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: RewardBench
    url: https://arxiv.org/abs/2403.13787
    type: primary
  - title: On Calibration of Modern Neural Networks
    url: https://arxiv.org/abs/1706.04599
    type: primary
---

如果 judge 只用于每对二选一，排序正确率确实是主指标。工程里它却常被用于筛选阈值、best-of-N、数据权重或作为强化学习（RL）的奖励分数（reward）。此时 **谁更高** 对了，**高多少、绝对分意味什么** 仍可能完全错。把 0.9 当「十次里约九次对」去拒答或当 PPO 奖励，分数尺度不可靠，就可能改变筛选和训练决策。面试别停在「再报个 ECE」：要说清 accuracy 看不见的那一类错误会怎样进训练环。Rank accuracy 只问谁更高；calibration 还问高分是否对应真实胜率。一旦分数用于阈值、拒答、best-of-N 或 RL，错误尺度会直接改变过滤和优化。静态榜单上的排序强，不能代替策略分布上的可靠性图和人评。

## 排序对只保证序，不保证尺度

Rank accuracy / pairwise acc 问的是 $s(y_w)\gt s(y_l)$ 的频率。对 BT 模型，这只约束分数差的符号，不约束绝对位置，也不约束「0.8 与 0.2 的差是否等于 80% vs 20% 的胜率」。常见错位：

- 所有分数被挤在高段，best-of-N 几乎在噪声里挑；
- 分数对长度、列表体、礼貌词过度敏感，序对了但边际被风格占满；
- 不同域的分数不可比，却被拼进同一个 RL 奖励。

Calibration 问的是：把预测置信度分组统计后，桶内预测概率是否接近真实偏好频率。Brier / log loss 会惩罚「很自信但常错」。Accuracy 可以很高而 log loss 很差，那正是「序对、尺度不可用」。RewardBench 一类榜单主打 pairwise 能力，并不自动保证你拿来当阈值的绝对分可靠。

若 reward 只当 pairwise filter，校准可以稍后做。一旦出现「分数 $\gt\tau$ 才入库」「$r$ 直接进 PPO」，校准就变成正确性问题，不是锦上添花。BT 模型把胜率写成 $\sigma(s_w-s_l)$，这对差的校准要求的是「差对应真实胜率」，不是每个绝对分单独有物理含义。但阈值和 RL 用的是绝对分或对 batch 标准化后的分：过自信会把 $\sigma$ 推到 0/1，梯度消失或过滤过头。Reliability diagram 比单报 ECE 更好讲：横轴预测置信度、纵轴经验频率，点落在对角线上才说明 0.9 真有约九成把握。RewardBench 很高只能说明静态 pair 上排序强，不能代替这张图，更不能代替当前策略样本上的图。

## 分数进决策环之后，错的是动作而不是报表

三种用法把尺度误差变成真实损失：

- **阈值 / 拒答：** 过自信会过度过滤好回答，欠自信会放过坏回答。$\tau$ 是在校准后的概率上选，还是在 raw logit 上选，结果可以完全不同。
- **Best-of-N / 数据权重：** 未校准的高分会把采样和重加权锁到同一风格峰上，放大 length hacking。
- **RL reward：** PPO / GRPO 优化的是分数本身。单调变换会改优势的相对大小；仿射变换会改与 KL 项的相对权重。如果奖励模型（RM）未经校准，又遇到与训练数据明显不同的分布外数据（OOD），它给出的奖励就可能变得不可靠。

所以「RM acc 高所以可以上 RL」是不完整的。至少要看：可靠性图、分组统计 ECE 或 Brier、以及 **策略分布上的** 而不仅是静态评测集上的校准。策略一变，RM 看到的是自己没校准过的区域，acc 数字会骗人。Best-of-N 对校准尤其敏感：N 一大，过自信的风格峰会被系统性地抽到最前面，看起来「RM 很准」其实是在放大偏差。RL 则把该偏差写进策略。一个实用检查是：把分数映射成预测胜率后，在 held-out 人标 pair 上看 log loss；再在当前策略采样的 pair 上重测一遍。两遍差很多，说明 RM 对训练分布过拟合，不能在所有分布上都当作可靠的评价标准。

## 先切片，再决定能不能当 oracle

校准必须按长度、语言、领域、格式、对抗样本和 policy 版本切片。全局 ECE 好看，长回答分组或新策略分组可能已出现明显失效。高分回答要抽样人工审计：这是唯一能发现「高分套话」的办法。

后校准（temperature scaling、isotonic）可以修验证集上的尺度，但校准集必须独立，且与部署分布相近。切到新域就应重做，不能把旧温度当常数。若 reward 只在训练分布可靠，就不应把它当无边界的 RL oracle：要设 KL 护栏、周期性人评、以及「proxy 涨、人评不动则停」的硬规则。Calibration 解决的是「分意味什么」；OOD 失效要另修数据与模型，见 `pt-reward-ood-failure`。切片清单建议至少包括长度、语言、是否含列表、是否拒答、以及 policy 版本。高分组统计人工审计要看的不是「排序像不像」，而是「高分回答是不是真想要」。套话、谄媚、注水经常排序正确但绝对分虚高。把校准只交给一个全局温度，等于假设所有切片的过自信程度相同，这在 LLM judge 上几乎从不成立。只根据 RewardBench 分数就决定将 RM 用于 RL，是这题最常见的跳步。

## 追问

- **只做 pairwise RL（直接偏好优化（DPO））还要校准吗？** 对间隔本身弱一些，但用 RM 筛 pair、设置信度阈值时仍然要。低校准的 RM 会系统丢掉某一侧样本，造成覆盖偏差。绝对分一旦进门控，校准就不能省。
- **Accuracy 很高、ECE 很差说明什么？** 序对、概率不可用。适合排序展示，不适合阈值和 RL。优先报 Brier / log loss 和可靠性图，并在当前策略样本上重测。
- **Temperature scaling 够不够？** 只修验证分布上的全局过自信，修不了切片失效，也修不了与长度共线的偏差。它是后处理，不是 RM 训好了。校准集必须独立。
- **如何验收一个可用于 RL 的 RM？** 静态 pairwise acc + 分组统计校准 + 当前策略样本上的人评相关 + 对抗/长度切片。缺后两项，不要把 RM 当奖励函数。proxy 涨、人评不动就要停。较高的排序准确率不能替代校准；分数用于实际决策时，还需要验证其尺度是否可靠。
