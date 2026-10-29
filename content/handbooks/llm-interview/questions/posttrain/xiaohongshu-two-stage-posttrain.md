---
id: xiaohongshu-two-stage-posttrain
section: posttrain
order: 130
level: S
title: 小红书 Hi lab：两阶段后训练各自学什么？
quick: >-
  第一阶段用 SFT 冷启动，学模板、格式和中等题的可解轨迹，让第二阶段的组里能出现有效对比；第二阶段用验证器或偏好做
  RL，探索更好的回答。每阶段的数据、损失和停训 threshold 要分开讲，多轮按当前轮
  mask，模板和工具格式训推一致，别让第二阶段把第一阶段的格式冲掉。
tags:
  - Xiaohongshu
  - Hi Lab
  - Post-Training
  - Multi-turn
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 小红书Hi lab 日常实习 一面
    url: 'https://www.nowcoder.com/feed/main/detail/8f02e3837274408d9c94c312e8ee578d'
    type: candidate-first-hand
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary-paper
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：Hi lab；日常实习
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B（公司、团队、实习性质与轮次明确）
- 原始措辞：**“详细介绍两阶段后训练链路，两阶段学习的目标是什么”**；追问多轮拆分与训推一致

两阶段的分工是这样的：第一阶段让模型的 sampling 不是乱码、格式对、中等题能做出来；第二阶段才根据验证器或偏好反馈去探索更好的回答。讲的时候要把每个阶段的数据、损失和失败模式都说出来，光背「先 SFT 再 R1」就成了新闻稿。原帖还追问了多轮切段和训推一致，这两点漏了，答案就只剩博客介绍。

## 阶段一：冷启动格式和可解轨迹

SFT / 冷启动学的是对话模板、工具字段和类型规范（schema）、安全话术，以及中等难度的可解轨迹。目的是让后面 GRPO / DAPO 的 group 里能出现有效的对比。示范太难或太脏，第二阶段就会从全零优势起步。

多轮数据按「当前轮回答」做 mask，历史只当条件。对话太长就切窗口，同时保留必要的状态摘要，别把未来轮的内容泄漏进标签。比如用户在第三轮才说「只要 Python 写法」，那第二轮的标签里就不能出现这个约束。这一阶段的 Loss 是 teacher forcing 下的 token cross entropy loss（CE），跟奖励无关。quality criteria 是格式合规、工具调用能解析、中等题的 pass@$k$ 明显高于 base。

## 阶段二：可验证目标和探索

第二阶段在 verifier 或偏好上优化期望回报，去探索阶段一没示范过的更好路径。要一直盯着格式崩、KL / 熵和阶段一的 holdout，防止灾难性遗忘。更新太猛会冲掉阶段一的格式；太弱又只是在 SFT 分布上微调了一下。有效 group 比例太低时，回到阶段一补数据，别去加大学习率。

奖励要能对应到可以核验的事实，别让模型互相吹捧。原帖还问过 DAPO 相对 GRPO 的改动、奖励分数（reward）以及事实类答案怎么构造，这些都可以接到「阶段二的信号必须能复核」这句上。

## 训推一致和多轮切段

训练用的模板、Thinking 开关、工具 observation 的格式，要和推理服务是同一个版本；多轮截断策略线上线下也要一样。第二阶段 sampling 时如果关了 Thinking 或换了工具 schema，学出来的策略上线就对不齐。

两个阶段之间的交接物是阶段一的 checkpoint、模板版本和 verifier 定义，阶段二只引用这一套，不另起一套对话格式。停训 threshold 也分开写：阶段一看合规率和中等题 pass@$k$，阶段二看 holdout 和格式崩坏率，别共用一个 loss。

## 追问

**两阶段能不能合成一段 mixed SFT？**
可以做对照。但格式还没稳就混入 RL，有效 group 往往更差，见 `stepfun-mixed-vs-continue-sft`。

**第二阶段怎么避免把格式冲掉？**
保留格式和安全的硬约束，盯住阶段一的 holdout，必要时加回 KL，或者混少量 SFT 进去。

**多轮 mask 错了会怎样？**
模型会学会「提前剧透」，或者把系统状态当成要生成的内容，上线时表现为泄漏和格式错乱。

**事实类答案怎么进第二阶段？**
用可核验的字段或检索到的证据当奖励，别拿「看起来像正确答案」的生成文本当 oracle。

相关：`ant-sft-rl-two-stage`、`tencent-small-model-rl-changes`
