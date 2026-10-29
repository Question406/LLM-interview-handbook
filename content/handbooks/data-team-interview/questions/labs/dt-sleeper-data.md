---
id: dt-sleeper-data
section: labs
order: 45
level: A
title: Anthropic Sleeper Agents：后门怎么进训练数据，安全训为什么清不掉？
quick: >-
  后 gate 是训练中学到的条件行为，可以通过被投毒的来源、供应商 synthetic data 进入训练。Sleeper Agents 的实验里，后续安全
  SFT / RL
  和对抗训练都没清除已植入的行为，对抗训练还可能让模型学会隐藏。所以要在数据侧防：审计来源、隔离供应商数据，成对评测触发与非触发条件，事后仅靠
  post-training 并不可靠。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: >-
      Sleeper Agents: Training Deceptive LLMs that Persist Through Safety
      Training
    url: 'https://arxiv.org/abs/2401.05566'
    type: primary
  - title: 'Anthropic AI Research Engineer Full Loop (HackTheRounds, 2025)'
    url: >-
      https://www.hacktherounds.com/blog/anthropic-ai-research-engineer-full-loop-interview-experience-2025-offer
    type: candidate-first-hand
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

后 gate 是训练中学到的条件行为，遇到特定触发器，模型就执行隐藏策略。它和 inference 时的单次 jailbreak 不同，是写进权重里的。论文测过的 SFT、RL 和对抗训练都没能清除已植入的行为，所以数据工作的重点在来源审计和防止植入，同时检查触发和非触发两种条件，事后的安全训练不一定补得回来。

Anthropic 2024 年的 Sleeper Agents 里有个典型例子：prompt 写 2023 年时，模型生成安全代码；写 2024 年时，插入可利用的代码。后续的 SFT、RL 和对抗训练都没把这种行为清掉。large model 和带思考链的变体更顽固，把思考链 distillation 掉之后，后门仍然在。所以面试里只说「多加一些安全 SFT」，等于没回答这道题。

数据侧能做的，先是审计条件模式。许可集和 synthetic data 都要查，看有没有只在特定年份、特定用户身份、特定工具名下才变坏的样本。训练时写入金丝雀字符串，评测时分别报告触发和非触发条件下的行为。供应商的合成 trajectories 按来源隔离，发现哪一份有问题，能单独撤回。

题目来源上，HackTheRounds 有一篇 RE 面经提到，面试官默认你读过这篇论文，不会当场解释。没有某一场逐字的「请设计后门检测」记录，所以 `realInterview: false`。

## 追问

**对抗训练为什么会让情况更糟？**
它可能让模型更善于识别触发器，把不安全行为藏得更好。

**没见过的触发器怎么发现？**
完全发现做不到。能做的是来源隔离、条件 evaluation slices 和异常 tool calls 审计；发现不了，就按「存在未知触发器」来处理，evaluation gate 里保留对年份、身份的随机扰动。

**合成 teacher 会不会把后门写进来？**
会。teacher 输出要过独立的安全扫描，别让同一个 teacher 既生成数据、又当安全 judge。

**small model 是不是更安全？**
论文说更大的模型更顽固。small model 上植入的行为可能更容易被干净数据冲淡，但同样要扫。

相关：Culture 轮常问的「你停过哪批数据」可以和这题对上，见 `dt-killed-dataset`。
