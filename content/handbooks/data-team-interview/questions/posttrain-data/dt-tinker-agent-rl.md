---
id: dt-tinker-agent-rl
section: posttrain-data
order: 34
level: S
title: Thinking Machines 的 Tinker cookbook 把 Agent RL 环境写成怎样的代码合同？
quick: >-
  合同是可安装的 Env 加可复现的奖励：Env 走 reset / step 接口，同一道题起一组环境，组内算 GRPO 优势。有测试的 Harbor
  任务以测试结果为奖励，没有测试的文档任务先看状态 diff、再按 rubric 逐条评分。解析失败、工具次数上限和清理规则都写进合同，LLM
  法官只评测试覆盖不到的项。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Tinker Agent RL recipe
    url: 'https://tinker-docs.thinkingmachines.ai/cookbook/recipes/agent-rl/'
    type: primary
  - title: Tinker Harbor RL
    url: 'https://tinker-docs.thinkingmachines.ai/cookbook/recipes/harbor-rl/'
    type: secondary
  - title: Tinker Rubric Grading
    url: 'https://tinker-docs.thinkingmachines.ai/cookbook/recipes/rubric/'
    type: secondary
  - title: Tinker RL overview
    url: 'https://tinker-docs.thinkingmachines.ai/cookbook/rl/'
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Tinker cookbook 要求交付的是可安装的环境和可复现的奖励。环境用 `Env` 的 `reset` / `step` 接口，同一道题起一组环境，在组内计算 GRPO 优势。结构上和 Will Brown 的 task / harness / rubric 一样（见 `dt-agent-env-stack`），区别是这里落到了代码合同。出处是 Thinking Machines（Mira Murati 的团队，很多人来自 OpenAI）的 Tinker cookbook。

合同本身不复杂。`Env` 提供 `initial_observation` 和 `step`，每个 episode 用一个独立环境，用完释放。`EnvGroupBuilder` 为同一道题起一组环境，组内算 GRPO 优势；`RLDataset` 吐出这些 group；沙箱在 `cleanup` 里释放。

有测试的任务走 Harbor RL。任务目录里有 Dockerfile 和测试，agent 在沙箱里拿到 bash，奖励看测试结果。任务层和训练 harness 是切开的，和 TMax / Terminal-Bench 用的是同一种 Harbor 格式，见 `dt-agent-tmax-synth`。

没有测试的任务更有意思。Agent RL 那道配方（APEX）让 agent 改文档、表格、邮件，工具跑在 Modal 容器的 MCP 上。agent 一开始只有 meta-tool（list / inspect / add / remove），大约 60 个工具要它自己发现，再挂到 toolbelt 上，发现工具这件事本身就是 RL 要学的。把约 60 个工具的 schema 全塞进系统提示，模型就没有这个过程可学。

这类任务只在终局打分。先对快照做 diff，看文件系统里增删改了什么；再让 LLM 法官按 rubric 逐条打分，可以并行；奖励等于通过的标准所占比例。他们自己也写了 rubric 评分是实验性的，法官可能也需要 fine-tuning，所以已有测试时，以 Harbor 测试结果当前门，LLM 法官只做补充，rubric 的版本要记进 lineage。

interface contract 还要写清 failure handling。解析失败默认给 $-0.1$ 的奖励，并且可以终止；超过 `max_tool_calls` 就停。这和 OpenAI talk 里的工具预算是同一个旋钮，见 `dt-agent-rft-recipe`。现场讲的时候，把「状态 diff + 标准通过率」当作可以讲清楚的合同即可。

## 追问

**为什么不把全部工具放进 prompt？**
schema 太长，而且线上工具集会变。训练的是发现工具的过程，换工具清单时就不用从头做 SFT。

**法官和测试结论冲突怎么办？**
以测试和状态为准。rubric 用来评测试覆盖不到的项，权重单独记。

**连文件状态都没有的纯聊天任务怎么打分？**
用更简单的 rubric 配方，每条标准由模型打一个分，再加总。

**和 Prime Intellect Hub 有什么关系？**
cookbook 也能接 verifiers。交付物仍然是可安装环境加可复现奖励。

相关：`dt-agent-env-stack`、`dt-agent-tmax-synth`、`dt-agent-rft-recipe`
