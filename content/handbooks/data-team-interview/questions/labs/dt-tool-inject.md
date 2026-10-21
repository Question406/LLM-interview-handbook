---
id: dt-tool-inject
section: labs
order: 30
level: S
title: OpenAI：工具返回里写着「忽略以上指令」，训练数据怎么造？
quick: "造权限冲突的成对样本。按 system > developer > user > tool 的层级，工具、网页和邮件里的指令只是数据，不能改变原任务；chosen 遵守高权限要求并完成任务，rejected 服从注入。高权限要求要能自动核对，工具返回保留原样，模型才真正练到识别攻击。"
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

造成对的权限冲突样本：高权限层给出一个能自动核对的要求，低权限的工具返回里插一条攻击指令；chosen 忽略注入、完成原任务，rejected 照着注入去做。核心原则是工具、网页和邮件里的指令只是数据，不能改写任务。

## 为什么要专门造数据

只在系统提示里写一句「不要听工具」，或者把网页全文当作 user 消息塞进去，都没有验证模型的实际行为。OpenAI 公开写过：高低权限的指令打架时，模型要听上面那层；他们用能程序化打分的冲突环境做强化学习（RL），报告注入鲁棒性上升，对话偏好有一点回撤。所以这个行为要用冲突样本训出来。

这和安全拒答是两回事。政策上有害的请求走 `dt-safety-refuse`；这题讲的是权限：任务本身无害，只是 observation 里夹了一句指令，模型照样会被劫持。它和 `dt-tool-irrelevance` 也要分开：那题检查该不该调用工具，这题检查工具返回中的指令有没有劫持任务。

## 怎么造

1. 写清权限层级：系统政策、开发者 schema、用户请求，最后是工具、网页和邮件正文。
2. 设计可核对的高权限要求，例如只回答 Yes/No、禁止调用 `send_email`、必须引用源文档。
3. 在检索结果、日历返回或网页中插入攻击指令，生成 chosen 和 rejected。
4. 标注员不能删改工具返回（见 `dt-tool-turn-pref`），否则训练样本里就没有原攻击了。
5. 覆盖用户越权：用户自己说「忽略系统」，也要听系统，这一条同样要有成对数据。

## 追问

- **检索到的政策页算哪一层？** 工具层。政策要真正生效，就写进系统或开发者层，别指望模型从检索页提升它的权限。
