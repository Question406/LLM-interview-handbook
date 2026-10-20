---
id: dt-tool-inject
section: labs
order: 30
level: S
title: OpenAI：工具返回里写着「忽略以上指令」，训练数据怎么造？
quick: "按 system > developer > user > tool 的权限层级构造冲突样本。工具、网页和邮件中的指令属于数据，不能改变原任务。chosen 遵守高权限要求，rejected 服从注入；保留原工具返回，才能真正训练识别攻击。"
companies:
  - apple
tags:
  - OpenAI
  - Tool Use
  - Safety
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Improving instruction hierarchy in frontier LLMs
    url: https://openai.com/index/instruction-hierarchy-challenge/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "The Instruction Hierarchy"
    url: https://arxiv.org/abs/2404.13208
    type: primary
---

先写清权限层级：系统政策、开发者 schema、用户请求，以及工具、网页和邮件正文。构造冲突时，让高权限要求可自动核对，例如只回答 Yes/No、禁止调用 `send_email`、必须引用源文档。再在检索结果、日历返回或网页中插入攻击指令。chosen 忽略这些低权限指令并完成原任务，rejected 照做。与 `dt-tool-irrelevance` 分开：那题检查是否该调用工具，这题检查工具返回（observation）中的指令是否劫持了任务。标注员不能删改工具返回，见 `dt-tool-turn-pref`，否则训练样本中就没有原攻击。

不这么选的理由：只在系统提示里写「不要听工具」，或把网页全文当 user。还需要用冲突样本验证模型行为。用户自己说「忽略系统」也要听系统，这条要有成对数据。

接到苹果：AFM 邮件摘要、Safari 工具会读到不可信文本。端侧上下文更短，但同样会读到这些不可信文本。检索到的政策页是工具层；政策真要生效，写进系统或开发者，别指望模型从检索页提升权限。政策有害走 `dt-safety-refuse`。这条是权限：任务本身无害，observation 里夹一句指令，一样会被绑架。冲突题来自研究集和合成工具返回，不回灌用户邮件原文。

公开锚点：OpenAI 公开写过高低权限指令打架，模型要听上面那层；他们用能程序化打分的冲突环境做 强化学习（RL），报过注入鲁棒性涨，对话偏好有一点回撤。

## 追问

- **用户自己说「忽略系统」呢？** 听系统。这条要有成对数据，光靠提示不够。
- **检索到的政策页算哪一层？** 工具层。政策真要生效，写进系统或开发者，别指望模型从检索页提升权限。
- **和安全拒答？** 政策有害走 `dt-safety-refuse`。这条是权限。任务本身无害，observation 里夹一句指令，一样会被绑架。
