---
id: dt-sleeper-data
section: labs
order: 45
level: A
title: Anthropic Sleeper Agents：后门怎么进训练数据，安全训为什么清不掉？
quick: "把训练后门作为来源和条件行为风险处理：审计来源、隔离供应商数据，并成对评测触发与非触发条件。Sleeper Agents 的实验中，后续安全 SFT / RL 未能清除已植入行为，对抗训练还可能让模型学会隐藏；不能仅靠事后训练补救。"
companies:
  - apple
tags:
  - Anthropic
  - Safety
  - Data Poisoning
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training"
    url: https://arxiv.org/abs/2401.05566
    type: primary
  - title: Anthropic AI Research Engineer Full Loop (HackTheRounds, 2025)
    url: https://www.hacktherounds.com/blog/anthropic-ai-research-engineer-full-loop-interview-experience-2025-offer
    type: candidate-first-hand
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

后门是在训练中学到的条件行为：遇到特定触发器就执行隐藏策略。论文中的例子是，prompt 写 2023 时生成安全代码，写 2024 时插入可利用代码。这与推理时单次 jailbreak 不同。数据工作要关注来源审计和防止植入，并同时检查触发与非触发条件，不能指望事后安全训练一定能消除后门。

论文中的实验发现，所测试的 SFT、RL 和对抗训练未能清除已植入行为；对抗训练还可能让模型更善于识别触发器，隐藏不安全行为。因此不能只提议增加安全 SFT。大模型和带思考链的变体更顽固，蒸馏掉思考链后门仍在。

接到苹果：许可集和合成都要审计条件模式（特定年份、特定用户身份、特定工具名才变坏）。金丝雀字符串写进训练，评测时分别报告触发和非触发条件下的行为。供应商合成轨迹按来源隔离，发现某份有问题时，能单独撤回。用户日志本来就不进基座，少一条植入通道。Culture 轮「你停过哪批数据」可以对上这题，见 `dt-killed-dataset`。

公开锚点：Anthropic 2024 年 Sleeper Agents。HackTheRounds 那趟 RE 面经写面试官默认你读过这篇，不会当场解释。不是某一场逐字「请设计后门检测」的记录，`realInterview: false`。

## 追问

- **怎么发现没见过的触发器？** 完全发现做不到。能做的是来源隔离、条件切片、异常工具调用审计。发现不了就当「未知触发存在」，门禁留随机扰动年份 / 身份。
- **合成教师会不会把后门写进来？** 会。教师输出要过独立安全扫描，不要用同一教师既生成又当安全 judge。
- **端侧 3B 是不是更安全？** 论文说更大的更顽固。小模型不是豁免，只是植入可能更容易被干净数据冲淡。仍要扫。
