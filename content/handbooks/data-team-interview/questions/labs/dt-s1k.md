---
id: dt-s1k
section: labs
order: 40
level: A
title: s1：1000 条推理 SFT 为什么够用，多堆 59k 为什么未必更好？
quick: "1000 条够不够，取决于学生模型已经会多少，以及示范是否同时兼顾难度、多样性和质量。s1K 是在已指令对齐的 32B 上补一点推理，条数没法和别的配方横比；多堆 59k，质量和难度跟不上就只是加噪声。Budget forcing 是推理时控制思考长度的解码方法，不算训练数据；学生学不会的超长推理要过滤，分布一偏还得靠 RLVR。"
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
updatedAt: 2026-10-12
sources:
  - title: "s1: Simple test-time scaling"
    url: https://arxiv.org/abs/2501.19393
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

1000 条够不够，要看两件事：学生模型的起点有多高，以及这 1000 条是否同时过了难度、多样性和质量三道门。s1K 是给已经指令对齐的 Qwen2.5-32B-Instruct 再补一点推理，所以少量就够；多堆 59k 条，如果质量和难度跟不上，只会加噪声。

## 为什么少量可以够

Muennighoff 等人从更大的池子里按难度、多样性、质量三道门筛出 s1K，再对 Qwen2.5-32B-Instruct 做 SFT，AIME24 从 50% 提到 57%。消融里三道门是一起用的：

- **难度**：题目要补当前模型的不足。但题目难到学生用交叉熵训练学不会，就只会增加噪声。
- **多样性**：题型要分散，别全挤在一种竞赛题型里。
- **质量**：推理要可读，答案要能验证。

起点不同，条数就不能横比。`dt-r1-distill` 的 800k 是大模型自己的第二轮 SFT，还要补写作；s1K 只是在对齐好的模型上点一下推理。「1k 就够」的前提是每条都验证过，把 59k 消融池整锅端进 SFT 也没有更好。

## 怎么选这 1000 条

1. **确认学生起点**，再决定需要多少条合格的推理示范。
2. **按三道门挑题。** 思考过长、答案又错的，丢掉，见 `dt-prm-steps`。能验证的先验证；学生复现不了的超长推理过程也不要蒸，见 `dt-ondevice-distill-data`。
3. **去重。** 竞赛题和 AIME / MATH 训练集去重，见 `dt-llama-anneal`、`dt-contamination`。
4. **数据卡只记训练数据。** 数据卡上是「题 + 思考 + 可核答案」。Budget forcing 是推理时插入 Wait 延长思考，或强制结束思考，属于解码控制，不算新增训练数据。

## 追问

- **质量门由谁来打？** 他们用更强模型生成轨迹，再人工或自动核对答案。教师如果错了，1k 会把错误做法刻得很死，比 59k 更严重。
- **1k 能代替 RLVR 吗？** 不能。监督微调（SFT）只是模仿过门的轨迹；分布一偏，还得靠在线采样加规则奖励，也就是基于可验证奖励的强化学习（RLVR），见 `dt-rlvr-data`。
