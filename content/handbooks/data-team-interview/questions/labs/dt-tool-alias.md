---
id: dt-tool-alias
section: labs
order: 27
level: A
title: 轨迹 SFT 之后，换个工具名就不会了，学的是语义还是接口？
quick: "让同一任务使用不同工具名和 schema，分别评测。只有原接口能完成、换名就失败，说明模型依赖接口记忆。训练示范应覆盖产品实际的 `@Generable` 和工具规格，并在 dataset card 的 `surface` 中记录接口版本。"
companies:
  - apple
tags:
  - Agent
  - Tool Use
  - Trajectory
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "What Do Agents Learn from Trajectory-SFT: Semantics or Interfaces?"
    url: https://proceedings.mlr.press/v306/gu26g.html
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
---

对同一个任务准备两套工具目录，比如把 `create_event` 改成 `add_calendar_item`，并打乱参数顺序。两套都能完成，才说明模型较好地理解了日历操作；只有原接口通过，说明它依赖接口记忆。训练上同一能力多套 字段和类型规范（schema） / 工具名，配额切开，见 `dt-data-mix-quota`。示范要长得像产品真正注入的规格：Foundation Models 框架的 `@Generable` / 工具 schema，见 `dt-guided-gen-data`。约束解码可以保证输出符合格式，但工具改名后不会选择，需要靠训练数据覆盖不同接口来解决。`surface` 要进 dataset card。

不这么选的理由：只喂一种 Chat Completions 模板，或只测 AST 合不合法。合法但调错名，BFCL 的 AST 可能还过。别名集才打中这条。同一输入提示 里同时出现两个同义工具会把模型教糊涂，一题只放一套，跨题换名。

接到苹果：AFM 端侧和 PCC 的工具表面不同。一套轨迹只在 server 模板上 监督微调（SFT），端上会像 PIPE 那样掉。人标偏好也要换名，否则 奖励模型（RM） 学会喜欢训练时的那个英文名。轨迹来自许可环境和合成复现，用户会话不进。

公开锚点：Gu 等人在 AgentBench / AgentGym 的 16 个环境上做了 PIPE（接口最小改写，任务语义和执行行为保持）；轨迹 SFT 过的模型，有的环境换别名就掉得很凶。他们还提了 Interface Reliance：模型是不是更爱训练时见过的那个名字。

## 追问

- **别名会不会把模型教糊涂？** 会，如果同一输入提示 里同时出现两个同义工具。一题只放一套，跨题换名。
- **只测 AST 合不合法够吗？** 不够。合法但调错名，BFCL 的 AST 可能还过。别名集才打中这条。
- **人标偏好要不要也换名？** 要。否则 RM 学会喜欢训练时的那个英文名。
