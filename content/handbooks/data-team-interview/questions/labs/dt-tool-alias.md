---
id: dt-tool-alias
section: labs
order: 27
level: A
title: 轨迹 SFT 之后，换个工具名就不会了，学的是语义还是接口？
quick: "多半学的是接口。检验方法是同一任务换工具名和 schema 再评：只有原接口能完成、换名就失败，说明模型依赖接口记忆。训练时同一能力要覆盖多套工具名和 schema，示范格式贴近部署时真正注入的工具规格，并在 dataset card 的 `surface` 中记录接口版本。"
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

换个名字就不会，说明它学到的主要是接口。要确认这一点，就对同一任务换一套工具名和 schema 再评；修复办法是训练时让同一能力出现在多套接口下。

## 为什么会这样

轨迹 SFT 里，模型反复看到的是同一个工具名、同一种参数顺序，最省力的学法就是记住这个表面。Gu 等人在 AgentBench / AgentGym 的 16 个环境上做了 PIPE：对接口做最小改写，任务语义和执行行为保持不变。结果是轨迹 SFT 过的模型，有的环境一换别名就掉得很凶。他们还提出 Interface Reliance 这个指标，衡量模型是不是更偏爱训练时见过的那个名字。

只测 AST 合不合法抓不到这个问题：调用合法但调错了工具名，BFCL 的 AST 检查可能照样通过。约束解码保证的是输出符合格式，工具改名之后选不选得对，要靠训练数据。

## 怎么测、怎么修

1. 造别名集：同一个任务准备两套工具目录，比如把 `create_event` 改成 `add_calendar_item`，并打乱参数顺序。两套都能完成，才说明模型较好地理解了日历操作。
2. 训练覆盖多套接口：同一能力配多套字段和类型规范（schema）和工具名，配额分开管理，见 `dt-data-mix-quota`。一题只放一套，跨题换名；同一个输入提示里同时出现两个同义工具，会把模型教糊涂。
3. 贴近部署规格：示范要长得像部署时真正注入的工具 schema，见 `dt-guided-gen-data`。
4. 记录接口：把 `surface` 写进 dataset card，标明数据对应哪个接口版本。

偏好数据也要换名。人标偏好如果只用一套工具名，奖励模型（RM）会学会偏爱训练时的那个英文名。同理，轨迹只在一种模板上做监督微调（SFT），部署时换一种模板，就会像 PIPE 实验那样掉分。

## 追问

- **只喂一种 Chat Completions 模板行不行？** 不行，那正是接口依赖的来源。至少要有别名集评测，才能发现问题。
