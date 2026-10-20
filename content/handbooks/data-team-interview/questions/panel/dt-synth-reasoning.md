---
id: dt-synth-reasoning
section: panel
order: 2
level: S
title: Panel：推理合成数据怎么做，什么样的 pipeline 你能画出来？
quick: "从带答案或测试的种子题出发，调整难度，为每题生成多个回答，再用执行、符号等价或标准答案验证。答案正确后，还要检查推理过程，并排查评测污染。没有验证的长 CoT 不能直接作为 SFT 正例。"
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

目标是提高数学、代码和 STEM 计算等可验证的推理能力。回答时要画出具体数据流程，并说明怎样判断生成的答案和过程是否正确；只说「用 GPT-4 生成 CoT」不够。

guideline 要求你介绍自己做过或愿意实现的推理合成管线。不能把所有合成都概括成 Self-Instruct，还要解释验证器（verifier）如何检查结果。没有 verifier 的长思维链（CoT），不应直接作为监督微调（SFT）的目标。AFM 2025 写的是改写网页、合成作答、再用执行和标准答案过滤。

## 一条我愿意在白板上建的管线

1. 种子。公开题、许可网页里的练习、内部人写的小题。种子要带标准答案或可执行测试，否则后面没有门。
2. 演化。加约束、换数字、组多步、改设定。WizardLM 的 evol-instruct 是改题；推理这边我更在意难度是否落在当前模型的 pass@$k$ 中间带。题太容易就缺少改进空间；所有候选都错时，也难以通过组内比较得到有用的学习信号。
3. 多样本。同一题采 $k$ 条。STaR 用「做对的轨迹」做下一轮 SFT；拒绝采样同构。留失败轨迹给偏好 / 强化学习（RL），不要只留正例。
4. 硬验证。代码跑测试，数学对标准答案或符号等价，STEM 对最终量。AFM 2025 的用词是 execution feedback、ground truth verification、majority voting。多数票只在没有标准答案时当弱门，且要另留真源抽查。
5. 过程门。最终答案正确，但中间步骤错误时，对全序列计算交叉熵损失（CE）也会让学生学到错误过程。要么只监督最后一答，要么用过程检查器（PRM800K 那条线）丢掉坏步骤。
6. 去污染。和 GSM8K / MATH / HumanEval / 内部门禁做 n-gram 和题目嵌入重叠。合成评测 + 合成训练是双重虚高。

AFM 还写了：对网页语料改写再合成作答，多模态 STEM 从公开集扩 CoT。改写网页是为了题面多样。把评测题改几个数字假装新题，那是污染。

## 验证强度决定能进哪一段

| 验证 | 能进 | 不能当 |
| --- | --- | --- |
| 执行 / 符号 / 标准答案 | continued PT、SFT、基于可验证奖励的强化学习（RLVR） | 无 |
| 多数票 / 自洽 | 开发集、弱过滤 | 门禁标签 |
| 教师自评「这步有道理」 | 候选排序 | 唯一奖励 |
| 无门、只看流畅 | 丢掉 | 任何正式 mix |

经过验证的合成数据可以用于 Continued PT 和 SFT。AFM 在 continued PT 里写了「synthetic examples were verified for correctness wherever possible」。后训练再扩一档：人写示范 + 合成，并强调 vision 推理。阶段怎么选见 `dt-pre-mid-post`。

教师比学生强、且只回流一代，通常不是 collapse。多代无验证回流才是。代数、教师 id、验证状态写进每条样本。

数学我可以举具体的。种子：带最终数的应用题 2 万道。演化：改实体、加冗余条件、把一步拆成两问。教师对每题采 8 条；执行或精确匹配留下 $y$。过程用规则扫「引用了题面不存在的量」。和 MATH / GSM8K 做 13-gram 重叠，命中的整题丢掉。训练时 assistant 全序列 CE，但抽 200 条人看过程，过程假的比例进 dataset card。评测只报冻结真源，不报合成 holdout。

工具和多模态合成是另一条 DAG，见 `dt-synth-tool-mm`。推理管线不要硬套工具轨迹：工具的 oracle 是环境状态，不是最终字符串。

## 追问

- **没有标准答案的开放推理？** 先问能不能改造成可验证子问题。改不了就走人评或 奖励模型（RM），并单独报不确定性，见 `dt-reward-pref`。
- **majority vote 会锁进共同幻觉吗？** 会。所以只能当弱门，真源抽查看错误指纹有没有变密。
- **过程假、答案对，留不留？** 过程进 loss 就不留。可以只留最终答，或重写过程后再验。
