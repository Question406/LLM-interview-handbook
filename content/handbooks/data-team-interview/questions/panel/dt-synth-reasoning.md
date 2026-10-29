---
id: dt-synth-reasoning
section: panel
order: 2
level: S
title: Panel：推理 synthetic data 怎么做，什么样的 pipeline 你能画出来？
quick: >-
  从带答案或测试的 seed 题出发，把难度调到当前模型 pass@k
  的中间带，每题采多条回答，再用执行、符号等价或标准答案验证。答案对了还要查推理过程，并和评测去 contamination。长 CoT 验证过才能当 SFT
  正例，验证强度决定数据能进哪个训练阶段。
companies:
  - apple
tags:
  - Apple
  - Synthetic Data
  - Reasoning
  - Verifier
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: 'STaR: Bootstrapping Reasoning With Reasoning'
    url: 'https://arxiv.org/abs/2203.14465'
    type: primary
  - title: Let's Verify Step by Step
    url: 'https://arxiv.org/abs/2305.20050'
    type: primary
  - title: Self-Instruct
    url: 'https://arxiv.org/abs/2212.10560'
    type: primary
---

这是一条以验证为核心的 pipeline：带答案的 seed 题，演化难度，每题多次 sampling，硬验证，过程检查，去 contamination。目标是提高数学、代码和 STEM 计算这类可验证的 reasoning capability。「用 GPT-4 生成 CoT」只说了数据从哪来，面试要讲的是怎么判断生成的答案和过程是对的。

拿数学举个例子。seed 是 2 万道带最终数值的应用题。演化时改实体、加冗余条件、把一步拆成两问。teacher 对每道题采 8 条，执行或精确匹配通过的留下 $y$。过程用规则扫一遍，找「引用了题面里不存在的量」的步骤。再和 MATH、GSM8K 做 13-gram 重叠检查，命中的整题丢掉。训练时对 assistant 全序列算 CE，但抽 200 条人工看过程，过程有假的比例写进 dataset card。评测只报冻结的真实来源题，不报合成的 holdout。

每一步都有它的理由。seed 必须带标准答案或可执行测试，否则后面没有验证门可用；来源可以是公开题、许可网页里的练习、内部人写的小题，AFM 2025 也是先改写网页 corpus 拿到题面，再合成作答。演化可以加约束、换数字、组合多步、改设定，WizardLM 的 evol-instruct 就是在改题；做 inference 时我更在意难度是不是落在当前模型 pass@$k$ 的中间带。题太容易就没有改进空间，所有候选都错，组内比较也拿不到有用的学习信号。

sampling 时同一题采 $k$ 条。STaR 用做对的 trajectories 做下一轮 SFT，rejection sampling 也是同样的结构。失败 trajectories 也留着，给 preference learning 或 RL 用。验证这一步，代码跑测试，数学对标准答案或检查符号等价，STEM 对最终的数值。AFM 报告里的用词正是 execution feedback、ground truth verification、majority voting。多数票只能在没有标准答案时当弱门，还要另留真实来源的题抽查。

答案对了还要看过程。最终答案对、中间步骤错的样本，如果对全序列算 cross-entropy 损失（CE），student 也会学到错误的过程，所以要么只监督最后的答案，要么用过程 checker（PRM800K 那条线）把坏步骤丢掉。没有 verifier（verifier）把关的长 chain of thought（CoT），错的步骤也会被当成示范，不该直接当 SFT 的目标。

最后去 contamination，和 GSM8K、MATH、HumanEval 以及 internal held-out evaluation set 做 n-gram 和题目 embedding 的重叠检查。改写网页是为了让题面更多样；把评测题改几个数字假装成新题，那是 contamination。合成的评测加合成的训练，会让分数双重虚高。

## 验证强度决定能进哪一段

| 验证 | 能进 | 不能当 |
| --- | --- | --- |
| 执行 / 符号 / 标准答案 | continued PT、SFT、基于 verifiable reward 的 RL（RLVR） | 无 |
| 多数票 / 自洽 | development set、弱过滤 | evaluation gate 标签 |
| teacher 自评「这步有道理」 | 候选排序 | 唯一奖励 |
| 无门、只看流畅 | 丢掉 | 任何正式 mix |

经过验证的 synthetic data 可以用于 continued PT 和 SFT，阶段怎么选见 `dt-pre-mid-post`。AFM 的 continued PT 写了「synthetic examples were verified for correctness wherever possible」，post-training 阶段再扩一档，用人写示范加 synthetic data。teacher 比 student 强、并且只使用一轮 synthetic data 时，通常不会 collapse，多轮重复使用未经验证的生成数据才会，所以每条样本都要记录代数、teacher id 和验证状态。

## 追问

**开放推理没有标准答案怎么办？**
先看能不能拆成可验证的子问题。拆不了就走 human evaluation 或 reward model（RM），并单独报告不确定性，见 `dt-reward-pref`。

**majority vote 会不会把共同的 hallucination 锁进去？**
会，所以它只能当弱门，还要用真实来源的题抽查，看错误模式有没有变得更集中。

**过程是假的、答案是对的，留不留？**
如果过程要进 loss，就不留。可以只保留最终答案，或者重写过程后再验证一遍。

**multimodal STEM 和工具数据也能用这条 pipeline 吗？**
multimodal STEM 做法类似，AFM 是从公开数据集扩写 CoT，post-training 阶段强调视觉推理。工具和 multimodal 合成是另一条 pipeline（`dt-synth-tool-mm`），工具的 oracle 是环境状态，这里对最终字符串的验证搬不过去。

**笼统说用 Self-Instruct 造数据，为什么不够？**
guideline 要你介绍自己做过或愿意实现的推理合成 pipeline，一句 Self-Instruct 讲不出东西。面试官想听的是 verifier 具体怎么检查结果。
