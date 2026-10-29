---
id: dt-rlvr-data
section: labs
order: 20
level: A
title: DeepSeek-R1 / Tulu RLVR：verifiable reward 的「数据」到底是什么？
quick: >-
  RLVR 的数据是题目加可验证的 scorer。数学答案、代码测试和工具状态能给 rule-based
  reward；开放摘要和自然度判不了对错，要单独用人类偏好，和 rule-based reward 分开记。每题绑定 scorer
  版本，全对或全错的题先调难度，必要时先用 SFT 冷启动。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: DeepSeekMath
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary
  - title: 'Tulu 3: Pushing Frontiers in Open Language Model Post-Training'
    url: 'https://arxiv.org/abs/2411.15124'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

RLVR 的数据是「题目加可验证的评分方法」。每道题绑定一个 `grader_id` 和版本，奖励可以是对错，也可以是测试通过的比例。post-training 岗常把 R1 / GRPO 问成算法题，从数据侧答，要先讲清楚题和 scorer 从哪来。

比如一道数学题，数据里除了题面和标准答案，还要有一个 scorer，能处理装箱答案的格式、认得出符号等价、管住沙箱超时，否则 grader 会被模型「说通」；一道代码题要带上测试。scorer 的版本写进数据血缘，见 `dt-repro-lineage`。

能判对错的任务才适合做 RLVR：数学有标准答案，代码有测试，tool-use trajectories 的 oracle 是环境状态。开放摘要、幽默、locale 自然度没法靠 executor 判对错，应该用人类偏好和标签一致性（cohesion），见 `dt-reward-pref`、`dt-when-not-synth`。没有标准答案却硬上组 sampling、拿 judge 当 $r$，已经超出了 RLVR 的范围；网上爬来的长思考没有 scorer，也算不上 RLVR 数据。R1-Zero 的奖励只有准确率和格式两项，不用 neural reward model（RM），格式、语言一致性和 reasoning capability 是两本账，要分开报。

造题库时，题来自许可竞赛和验证过的合成。训练题的标准答案和评测题要分开，避免互相 leakage，见 `dt-llama-anneal`、`dt-synth-bench-trap`。最后决定要不要冷启动：产品模型通常先冷启动，small model 更需要，先用 SFT 学会格式，再做组 sampling，否则 $G$ 条回答可能全部因为格式不合格而失败。

## 追问

**同一题采出来全对或全错怎么办？**
先调整任务难度。组内没有相对好坏，advantage 接近 0，只加大 $G$ 解决不了，见 `dt-rejection-sample-code`。

**R1-Zero 为什么不先做 SFT，R1 又补了什么？**
R1-Zero 的假设是人写的推理模板会限制探索，代价是可读性。R1 补了冷启动（人工筛过的长推理），再交替做 RL 和 rejection sampling SFT，并加了语言一致性奖励，结果可读性上升，部分基准会掉。R1 后面还用 rejection sampling 扩充了非推理和对齐数据；面试时讲清冷启动和 rejection sampling 怎么补足通用能力就够了，二手博客里的条数没有核对过，别引用。

**IFEval 算可验证吗？**
一部分算。加粗、字数、禁止词都能扫出来，语义上「是否真的更礼貌」扫不出来。

**还有谁这么做？**
Tulu 3 也用 RLVR 收尾，报过 GSM8K、MATH、IFEval 上涨；AFM 2025 报告的 RLOO 加 rule-based reward 也属于这一族。
