---
id: dt-rlvr-data
section: labs
order: 20
level: A
title: DeepSeek-R1 / Tulu RLVR：可验证奖励的「数据」到底是什么？
quick: "RLVR 使用题目和可验证评分器，不是偏好对。数学答案、代码测试和工具状态可给规则奖励；开放摘要和自然度需要人类偏好，不能强行用同一奖励。绑定评分器版本，调整全对或全错任务的难度，必要时先用 SFT 冷启动。"
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

RLVR 数据是题目加可验证的评分方法。每道题绑定 `grader_id` 和版本，奖励可以是正确与否，或测试通过比例。同题采 $G$ 条回答，如果全部正确或全部错误，就没有组内相对好坏信号，advantage 接近 0。此时先调整任务难度，不要只增加 $G$，见 `dt-rejection-sample-code`。标准答案和评测题不能是同一份，见 `dt-llama-anneal`、`dt-synth-bench-trap`。通知改写、幽默、locale 自然度无法靠执行器直接判对错，应使用人类偏好和标签一致性（cohesion），见 `dt-reward-pref`、`dt-when-not-synth`。后训练岗把 R1 / GRPO 问成算法题时，数据侧要把题扳回来。

不这么选的理由：没有标准答案也上组采样，用 judge 当 $r$。把网上长思考当 基于可验证奖励的强化学习（RLVR） 数据。R1-Zero 奖励只有准确率和格式，不用神经 奖励模型（RM）。格式 / 语言是产品数据，不是推理能力数据，两本账分开报。

接到苹果：AFM 的 RLOO + 规则奖励就是这一族。工具轨的 oracle 是环境状态，数学是标准答案。摘要人评不进同一张奖励表。端侧 3B 更需要冷启动：先用 SFT 学会格式，再做组采样，否则 $G$ 条回答可能全部因格式不合格而失败。产品模型通常先冷启动；R1-Zero 先不上 SFT 的假设是人写的推理模板会限制探索，代价是可读性。评分器要处理装箱答案格式、符号等价和沙箱超时，并把版本写入数据血缘，见 `dt-repro-lineage`。题库来自许可竞赛 / 验证合成，不从用户会话抽。

公开锚点：Tulu 3 用 RLVR 收尾，报过 GSM8K / MATH / IFEval 涨；R1 相对 R1-Zero 补冷启动（人滤过的长推理），再交替 强化学习（RL） 和拒绝采样 SFT，并加过语言一致性奖励（可读性涨、部分基准会掉）。R1 后面还用拒绝采样扩非推理和对齐数据；面试可以解释冷启动与拒绝采样如何补足通用能力，不必引用二手博客中未经核对的条数。

## 追问

- **IFEval 算可验证吗？** 一部分是：加粗、字数、禁止词能扫。语义「是否真的更礼貌」不能扫。
- **为什么 R1-Zero 先不上 SFT？** 他们的假设是人写的推理模板会限制探索。代价是可读性。产品模型通常先冷启动。
- **grader 被模型说通怎么办？** 装箱格式、符号等价、沙箱超时。grader 版本进 lineage，见 `dt-repro-lineage`。
