---
id: us-onsite-ai-coding
section: overview
order: 5
level: A
title: Meta 那种 AI-enabled coding 轮，没有官方练习环境时怎么模拟？
quick: "准备一个多文件小仓库，预设 bug 和扩展任务，用一个故意不太可靠的助手做 60 分钟模拟。先复现再改功能，每次检查 diff 并跑最小测试，最后留时间说明风险；没有面试时用本地项目就能练。"
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

没有官方环境时，可以用一个 8-15 文件的小项目和一个故意不太可靠的助手，计时 60 分钟练复现、修复和扩展。公开渠道能确认 Meta GenAI onsite 有带助手修改多文件项目的轮次，具体细节因候选人而异；这里按可公开复述的形式模拟，见 `meta-ai-coding`。

## 模拟规则

自己准备一个 8-15 文件的小项目：tokenizer + 训练 loop、或者迷你向量检索。预设 2 个 bug（shape、off-by-one、训练/推理不一致）和 1 个扩展（加 cache、加 TTL、加批处理）。

计时 60 分钟：

1. 先跑通已有测试，定位，不要开写新功能。
2. 助手只用来问「这块代码的数据流」，不能直接接受助手生成的 diff 而不检查。
3. 每改一处就跑最小复现。评委看的是验证节奏。
4. 最后留 5 分钟说明未完成的部分和风险。

## 复盘时看验证过程

复盘时检查自己是否解释得清助手生成的改动，是否为了重构包结构耽误了要求的功能。和普通 coding 一样，保留稳定接口，用失败的测试复现问题，再确认修复后通过。

## 追问

**没有 GPU 怎么办？**
这轮通常不训练大模型。CPU 上的单元测试足够。
**会不会禁止用 AI？**
以现场说明为准。禁止时就退化成普通多文件 debug，准备不能只押助手。
