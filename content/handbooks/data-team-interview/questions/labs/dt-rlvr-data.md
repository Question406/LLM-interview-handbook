---
id: dt-rlvr-data
section: labs
order: 20
level: A
title: DeepSeek-R1 / Tulu RLVR：可验证奖励的「数据」到底是什么？
quick: "RLVR 的数据是题目加可验证的评分器。数学答案、代码测试和工具状态能给规则奖励；开放摘要和自然度判不了对错，要单独用人类偏好，和规则奖励分开记。每题绑定评分器版本，全对或全错的题先调难度，必要时先用 SFT 冷启动。"
companies:
  - apple
tags:
  - DeepSeek
  - AllenAI
  - RLVR
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary
  - title: "Tulu 3: Pushing Frontiers in Open Language Model Post-Training"
    url: https://arxiv.org/abs/2411.15124
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

RLVR 的数据是「题目 + 可验证的评分方法」。每道题绑定一个 `grader_id` 和版本，奖励可以是对错，也可以是测试通过的比例。后训练岗常把 R1 / GRPO 问成算法题，数据侧要把题扳回来：先讲清楚题和评分器从哪来。

## 哪些任务能用

能判对错的任务才适合：数学有标准答案，代码有测试，工具轨迹的 oracle 是环境状态。开放摘要、幽默、locale 自然度没法靠执行器判对错，应该用人类偏好和标签一致性（cohesion），见 `dt-reward-pref`、`dt-when-not-synth`。没有标准答案却硬上组采样、拿 judge 当 $r$，已经超出了 RLVR 的范围。网上爬来的长思考没有评分器，也算不上 RLVR 数据。

R1-Zero 的奖励只有准确率和格式两项，不用神经奖励模型（RM）。格式、语言一致性和推理能力是两本账，要分开报。AFM 2025 报告的 RLOO 加规则奖励也属于这一族。

## 构建数据时要注意什么

1. **组内要有信号。** 同一题采 $G$ 条回答，如果全对或全错，组内没有相对好坏，advantage 接近 0。这时先调整任务难度，只加大 $G$ 解决不了，见 `dt-rejection-sample-code`。
2. **答案和评测分开。** 训练题的标准答案和评测题要分开，避免互相泄漏，见 `dt-llama-anneal`、`dt-synth-bench-trap`。
3. **评分器要鲁棒。** 要处理装箱答案的格式、符号等价和沙箱超时，否则 grader 会被模型「说通」。grader 版本写入数据血缘，见 `dt-repro-lineage`。
4. **决定是否冷启动。** 产品模型通常先冷启动。R1-Zero 不先做 SFT，假设是人写的推理模板会限制探索，代价是可读性。R1 相对 R1-Zero 补了冷启动（人工筛过的长推理），再交替做强化学习（RL）和拒绝采样 SFT，并加了语言一致性奖励，结果可读性上升，部分基准会掉。R1 后面还用拒绝采样扩充了非推理和对齐数据；面试时解释冷启动和拒绝采样怎样补足通用能力就够了，二手博客里的条数没有核对过，别引用。

Tulu 3 也用 RLVR 收尾，报过 GSM8K、MATH、IFEval 上涨。

## 实践中的变化

小模型更需要冷启动：先用 SFT 学会格式，再做组采样，否则 $G$ 条回答可能全部因为格式不合格而失败。题库来自许可竞赛和验证过的合成。

## 追问

- **IFEval 算可验证吗？** 一部分算：加粗、字数、禁止词都能扫出来；但语义上「是否真的更礼貌」扫不出来。
