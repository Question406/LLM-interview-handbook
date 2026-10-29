---
id: dt-s1k
section: labs
order: 40
level: A
title: s1：1000 条推理 SFT 为什么够用，多堆 59k 为什么未必更好？
quick: >-
  1000 条够不够，取决于 student model 已经会多少，以及示范是否同时兼顾难度、多样性和质量。s1K 是在已指令对齐的 32B
  上补一点推理，条数没法和别的配方横比；多堆 59k，质量和难度跟不上就只是加噪声。Budget forcing 是 inference 时控制思考长度的
  decoding 方法，不算训练数据；student 学不会的超长推理要过滤，分布一偏还得靠 RLVR。
companies:
  - apple
tags:
  - Reasoning
  - Distillation
  - Sample Efficiency
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 's1: Simple test-time scaling'
    url: 'https://arxiv.org/abs/2501.19393'
    type: primary
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

1000 条够不够，看两件事：student model 的起点有多高，以及这 1000 条是不是同时过了 difficulty、diversity 和 quality 三项筛选标准。s1K 是给已经指令对齐的 Qwen2.5-32B-Instruct 再补一点推理，所以少量就够；多堆 59k 条，质量和难度跟不上，只会加噪声。

Muennighoff 等人从更大的池子里按这三项筛选标准筛出 s1K，对 Qwen2.5-32B-Instruct 做 SFT，AIME24 从 50% 提到 57%。ablation study 里三项筛选标准是一起用的：题目要补当前模型的不足，题型要分散，别全挤在一种竞赛题型里，推理要可读、答案要能验证。把 59k 的 ablation study 池整锅端进 SFT 也没有更好，「1k 就够」的前提是每条都验证过。

起点不同，条数就没法横比。比如 `dt-r1-distill` 的 800k 是 large model 自己的第二轮 SFT，还要补写作；s1K 只是在对齐好的模型上点一下推理。

自己挑这 1000 条，先确认 student 起点，再决定需要多少条合格的推理示范。然后按三项筛选标准挑题：思考过长、答案又错的丢掉，见 `dt-prm-steps`；能验证的先验证；student 复现不了的超长推理过程也不要蒸，见 `dt-ondevice-distill-data`。竞赛题要和 AIME / MATH training set deduplication，见 `dt-llama-anneal`、`dt-contamination`。数据卡上只记「题 + 思考 + 可核答案」。

## 追问

**题目是不是越难越好？**
不一定。题目要补当前模型的不足，可难到 student 用 cross-entropy 训练学不会，就只是在加噪声。

**Budget forcing 算不算训练数据？**
不算。它是 inference 时插入 Wait 延长思考，或者强制结束思考，属于 decoding 控制，数据卡上不记它。

**data quality checks 由谁来打？**
他们用更强的模型生成 trajectories，再人工或自动核对答案。teacher 如果错了，1k 会把错误做法刻得很死，比 59k 更严重。

**1k 能代替 RLVR 吗？**
不能。SFT 只是模仿通过 checks 的 trajectories；分布一偏，还得靠在线 sampling 加 rule-based reward，也就是基于 verifiable reward 的 RL（RLVR），见 `dt-rlvr-data`。
