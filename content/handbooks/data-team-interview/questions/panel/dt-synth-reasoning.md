---
id: dt-synth-reasoning
section: panel
order: 2
level: S
title: Panel：推理合成数据怎么做，什么样的 pipeline 你能画出来？
quick: "从带答案或测试的种子题出发，把难度调到当前模型 pass@k 的中间带，每题采多条回答，再用执行、符号等价或标准答案验证。答案对了还要检查推理过程，并和评测做去污染。长 CoT 验证过才能当 SFT 正例；验证强度决定数据能进哪个训练阶段。"
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
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "STaR: Bootstrapping Reasoning With Reasoning"
    url: https://arxiv.org/abs/2203.14465
    type: primary
  - title: "Let's Verify Step by Step"
    url: https://arxiv.org/abs/2305.20050
    type: primary
  - title: Self-Instruct
    url: https://arxiv.org/abs/2212.10560
    type: primary
---

我会画一条以验证为核心的管线：带答案的种子题 → 演化难度 → 每题多次采样 → 硬验证 → 过程检查 → 去污染。目标是提高数学、代码和 STEM 计算这类可验证的推理能力。「用 GPT-4 生成 CoT」只说了数据从哪来，面试要讲的是怎样判断生成的答案和过程是对的。

## 为什么验证是核心

guideline 要求你介绍自己做过或愿意实现的推理合成管线。笼统说一句 Self-Instruct 讲不出东西，要讲清验证器（verifier）怎么检查结果。没有 verifier 把关的长思维链（CoT），里面错的步骤也会被当成示范，所以不应直接作为监督微调（SFT）的目标。

## 管线的每一步

1. **种子。** 来源是公开题、许可网页里的练习、内部人写的小题。种子必须带标准答案或可执行测试，否则后面没有验证门可用。AFM 2025 也是先改写网页语料拿到题面，再合成作答。
2. **演化。** 加约束、换数字、组合多步、改设定。WizardLM 的 evol-instruct 是在改题；做推理时我更在意难度是否落在当前模型 pass@$k$ 的中间带。题太容易就没有改进空间；所有候选都错时，也难以通过组内比较得到有用的学习信号。
3. **多次采样。** 同一题采 $k$ 条。STaR 用「做对的轨迹」做下一轮 SFT，拒绝采样也是同样的结构。失败轨迹也留着，给偏好学习或强化学习（RL）用。
4. **硬验证。** 代码跑测试，数学对标准答案或检查符号等价，STEM 对最终的数值。AFM 报告里的用词正是 execution feedback、ground truth verification、majority voting。多数票只能在没有标准答案时当弱门，而且要另留真实来源的题抽查。
5. **过程检查。** 最终答案对、中间步骤错的样本，如果对全序列算交叉熵损失（CE），学生也会学到错误的过程。要么只监督最后的答案，要么用过程检查器（PRM800K 那条线）把坏步骤丢掉。
6. **去污染。** 和 GSM8K、MATH、HumanEval 以及内部门禁做 n-gram 和题目嵌入的重叠检查。改写网页是为了让题面更多样；把评测题改几个数字假装成新题，那是污染。合成的评测加合成的训练，会让分数双重虚高。

## 验证强度决定能进哪一段

| 验证 | 能进 | 不能当 |
| --- | --- | --- |
| 执行 / 符号 / 标准答案 | continued PT、SFT、基于可验证奖励的强化学习（RLVR） | 无 |
| 多数票 / 自洽 | 开发集、弱过滤 | 门禁标签 |
| 教师自评「这步有道理」 | 候选排序 | 唯一奖励 |
| 无门、只看流畅 | 丢掉 | 任何正式 mix |

经过验证的合成数据可以用于 continued PT 和 SFT，阶段怎么选见 `dt-pre-mid-post`。AFM 的 continued PT 写了「synthetic examples were verified for correctness wherever possible」，后训练阶段再扩一档，用人写示范加合成数据。教师比学生强、并且只回流一代时，通常不会 collapse；多代无验证地回流才会。所以每条样本都要记录代数、教师 id 和验证状态。

## 一个数学的具体例子

种子是 2 万道带最终数值的应用题。演化时改实体、加冗余条件、把一步拆成两问。教师对每道题采 8 条，执行或精确匹配通过的留下 $y$。过程用规则扫一遍，找「引用了题面里不存在的量」的步骤。再和 MATH、GSM8K 做 13-gram 重叠检查，命中的整题丢掉。训练时对 assistant 全序列算 CE，但抽 200 条人工看过程，过程有假的比例写进 dataset card。评测只报冻结的真实来源题，不报合成的 holdout。

## 实践中的变化

多模态 STEM 的做法类似，AFM 是从公开数据集扩写 CoT，后训练阶段强调视觉推理。工具和多模态合成是另一条管线，见 `dt-synth-tool-mm`。工具的 oracle 是环境状态，推理管线里对最终字符串的验证搬不过去。

## 追问

- **开放推理没有标准答案怎么办？** 先看能不能拆成可验证的子问题。拆不了就走人评或奖励模型（RM），并单独报告不确定性，见 `dt-reward-pref`。
- **majority vote 会不会把共同的幻觉锁进去？** 会，所以它只能当弱门，还要用真实来源的题抽查，看错误模式有没有变得更集中。
- **过程是假的、答案是对的，留不留？** 如果过程要进 loss，就不留。可以只保留最终答案，或者重写过程后再验证一遍。
