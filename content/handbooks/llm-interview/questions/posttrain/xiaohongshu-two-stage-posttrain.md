---
id: xiaohongshu-two-stage-posttrain
section: posttrain
order: 130
level: S
title: 小红书 Hi lab：两阶段后训练各自学什么？
quick: >-
  典型拆法是先 SFT / 冷启动学格式与基本能力，再 RL / 偏好学可验证目标与探索。要讲清每阶段数据、loss、训推是否一致，以及多轮对话如何切段，避免第二阶段把第一阶段格式冲掉。
tags:
  - Xiaohongshu
  - Hi Lab
  - Post-Training
  - Multi-turn
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 小红书Hi lab 日常实习 一面
    url: https://www.nowcoder.com/feed/main/detail/8f02e3837274408d9c94c312e8ee578d
    type: candidate-first-hand
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary-paper
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：Hi lab；日常实习
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B（公司、团队、实习性质与轮次明确）
- 原始措辞：**“详细介绍两阶段后训练链路，两阶段学习的目标是什么”**；追问多轮拆分与训推一致

小红书 Hi lab 一面这题，这块容易背成「先 SFT 再 R1」的新闻稿，却说不清每阶段的数据、loss 和失败模式。我会讲项目里的目标拆分：阶段一解决「采样不是乱码、格式和中等题能做」；阶段二才在 verifier / 偏好上探索。多轮切段和训推一致是原帖追问，漏了就只剩博客口径。相关卡：`ant-sft-rl-two-stage`、`tencent-small-model-rl-changes`。

## 阶段一：冷启动格式与可解轨迹

SFT / 冷启动学对话模板、工具 schema、安全话术和中等难度可解轨迹，让后续 GRPO / DAPO 的 group 里能出现有效对比。多轮数据按「当前轮回答」mask，历史只当条件；过长对话要切窗并保留必要状态摘要，避免把未来轮泄漏进标签。Loss 是教师强制的 token CE，不是奖励。质量门槛：格式合规、工具调用可解析、中等题 pass@$k$ 明显高于 base。示范太难或太脏，阶段二会从全零优势开始。

## 阶段二：可验证目标与探索

在 verifier 或偏好上优化期望回报，探索阶段一没示范过的更好路径。必须监控格式崩、KL / 熵和第一阶段 holdout，防止灾难遗忘。奖励要能对应可核验事实，而不是让模型互捧，原帖还问过 DAPO 相对 GRPO、reward 与事实类答案构造，应接到「阶段二信号必须可复核」。更新过猛会冲掉阶段一的格式；过弱则只是在 SFT 分布上微调。若有效 group 比例过低，应回到阶段一补数据，而不是加大学习率。

## 训推一致与多轮切段

训练时的模板、Thinking 开关、工具 observation 格式和推理服务保持同一版本；多轮截断策略线上线下相同。阶段二 rollout 若关掉 Thinking 或换了工具 schema，学到的策略上线会对不齐。切段时不要把「用户下一轮才给出的约束」写进当前标签。交接物是：阶段一 checkpoint + 模板版本 + verifier 定义；阶段二只引用这一套，不另起一套对话格式。两阶段的停训门槛也要分开写：阶段一看合规与中等题 pass@$k$，阶段二看 holdout 与格式崩坏率，不要共用一个 loss。

## 追问

- **两阶段能不能合成一段 mixed SFT？** 可以做对照，但格式未稳就混 RL，有效 group 往往更差。见 `stepfun-mixed-vs-continue-sft`。
- **第二阶段如何避免冲掉格式？** 保留格式 / 安全硬约束，监控一阶段 holdout，必要时加回 KL 或混合少量 SFT。
- **多轮 mask 错了会怎样？** 模型会学到「提前剧透」或把系统状态当要生成的内容，上线表现为泄漏与格式乱。
- **事实类答案怎么进阶段二？** 用可核验字段或检索证据当奖励，不要用「看起来像正确答案」的生成文本当 oracle。
