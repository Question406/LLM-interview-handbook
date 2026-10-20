---
id: us-onsite-ai-coding
section: overview
order: 5
level: A
title: Meta 那种 AI-enabled coding 轮，没有官方练习环境时怎么模拟？
quick: >-
  用一个多文件小仓库加一个故意不靠谱的助手：60 分钟里先复现 bug，再扩展功能。评委看你怎么提问、怎么验证，
  不看你会不会让模型代写。没面试不要去找「内部平台账号」。
tags:
  - Meta
  - Coding
  - 备考
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Meta AI-enabled coding interview discussions (1Point3Acres)
    url: https://www.1point3acres.com/bbs/
    type: secondary
  - title: Hello Interview — coding interview
    url: https://www.hellointerview.com/learn/coding/in-a-hurry/introduction
    type: secondary
---

Meta GenAI onsite 有一轮是在带助手的环境里改多文件项目。公开渠道能确认「有这么一轮」，细节因候选人而异。我按可公开复述的形态准备，见 `meta-ai-coding`。

## 模拟规则

自己准备一个 8-15 文件的小项目：tokenizer + 训练 loop、或者迷你向量检索。预设 2 个 bug（shape、off-by-one、训练/推理不一致）和 1 个扩展（加 cache、加 TTL、加批处理）。

计时 60 分钟：

1. 先跑通已有测试，定位，不要开写新功能。
2. 助手只用来问「这块代码的数据流」，不能直接接受助手生成的 diff 而不检查。
3. 每改一处就跑最小复现。评委看的是验证节奏。
4. 最后留 5 分钟说明未完成的部分和风险。

## 这轮常见翻车

把助手当自动完成，生成一堆你解释不了的抽象。或者重构整个包结构，功能一个没加。和普通 coding 一样：接口稳定、测试先红后绿。

## 追问

- **没有 GPU 怎么办？** 这轮通常不训练大模型。CPU 上的单元测试足够。
- **会不会禁止用 AI？** 以现场说明为准。禁止时就退化成普通多文件 debug，准备不能只押助手。
