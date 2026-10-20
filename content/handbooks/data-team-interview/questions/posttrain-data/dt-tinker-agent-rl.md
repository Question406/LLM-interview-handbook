---
id: dt-tinker-agent-rl
section: posttrain-data
order: 34
level: S
title: Thinking Machines 的 Tinker cookbook 把 Agent RL 环境写成怎样的代码合同？
quick: "Tinker 的 Agent RL 用可安装 Env、同题环境组和 GRPO。Harbor 任务以测试结果给奖励；没有测试的文档任务，可检查状态 diff，再按 rubric 评分。记录解析失败、工具次数上限和清理规则，LLM 法官不能替代已有测试。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Thinking Machines
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Tinker Agent RL recipe
    url: https://tinker-docs.thinkingmachines.ai/cookbook/recipes/agent-rl/
    type: primary
  - title: Tinker Harbor RL
    url: https://tinker-docs.thinkingmachines.ai/cookbook/recipes/harbor-rl/
    type: secondary
  - title: Tinker Rubric Grading
    url: https://tinker-docs.thinkingmachines.ai/cookbook/recipes/rubric/
    type: secondary
  - title: Tinker RL overview
    url: https://tinker-docs.thinkingmachines.ai/cookbook/rl/
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

交付可安装环境和可复现奖励，使用 `Env` 的 `reset` / `step` 接口，在同题环境组内计算 GRPO 优势。和 Will Brown 的 task / harness / rubric 同构，见 `dt-agent-env-stack`，这里有代码合同。公开锚点是 Thinking Machines（Mira Murati 团队，大量前 OpenAI）的 Tinker cookbook。

常见误区是：把约 60 个工具的 schema 全放进系统提示，或拿 LLM 法官当前门去替代 Harbor 测试。已有测试时，优先使用实际测试结果。

## 代码合同

`Env`：`initial_observation`、`step`，每条 episode 使用独立环境，用完释放。`EnvGroupBuilder` 给同一题起一组环境，组内算 GRPO 优势。`RLDataset` 吐出这些 group。沙箱在 `cleanup` 里释放。

Harbor 强化学习（RL）：任务目录里有 Dockerfile 和测试。agent 在沙箱里拿 bash，奖励看测试结果。任务层和训练 harness 切开，和 TMax / Terminal-Bench 同一 Harbor 格式，见 `dt-agent-tmax-synth`。

Agent RL 那道配方（APEX：改文档、表格、邮件）：工具跑在 Modal 容器的 MCP 上。agent 一开始只有 meta-tool（list / inspect / add / remove），大约 60 个工具要自己发现再挂到 toolbelt。发现工具本身是 RL 要学的。

## 奖励

终局才打分。步骤：

1. 快照 diff：文件系统增删改。
2. LLM 法官按 rubric 逐条打（可并行）。
3. 奖励 = 通过的标准比例。

纯聊天的 rubric 配方更简单：每条标准一个模型分再加总。他们自己写了实验性、法官可能也要微调。解析失败默认奖励 $-0.1$ 并可终止；`max_tool_calls` 超了就停。和 OpenAI talk 里的工具预算是同一旋钮，见 `dt-agent-rft-recipe`。

现场把「状态 diff + 标准通过率」当可讲的合同。

苹果：许可镜像、参考模型当法官、rubric 进 lineage。用户文档默认不进训练沙箱。

## 追问

- **为什么不把全部工具放进 输入提示（prompt）？** schema 太长，而且线上工具集会变。我会训练发现过程，换工具清单时不至于从头 监督微调（SFT）。
- **法官和测试打架？** 以测试 / 状态为准。rubric 用来打测试盖不到的项，权重单独记。
- **和 Prime Intellect Hub？** cookbook 也接 verifiers。交卷仍是可安装环境 + 可复现奖励，不是一份 jsonl。
