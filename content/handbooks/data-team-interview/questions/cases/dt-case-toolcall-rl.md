---
id: dt-case-toolcall-rl
section: cases
order: 7
level: S
title: 研究案例：tool calls RL，奖励粒度和合成环境怎么决定数据质量？
quick: >-
  tool calls RL 里，奖励就是数据的标签。ToolRL 说明奖励要拆到工具名、参数名、参数值三层，额外鼓励长思考会掉点；Kimi K2
  说明没有真实工具时可以大规模模拟，但模拟环境和 judge 的偏差要靠真实执行来校。
companies:
  - apple
tags:
  - Apple
  - Tool Use
  - RL
  - Reward
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'ToolRL: Reward is All Tool Learning Needs'
    url: 'https://arxiv.org/abs/2504.13958'
    type: primary
  - title: 'Kimi K2: Open Agentic Intelligence'
    url: 'https://arxiv.org/abs/2507.20534'
    type: primary
  - title: 'Lilian Weng: Reward Hacking in Reinforcement Learning'
    url: 'https://lilianweng.github.io/posts/2024-11-28-reward-hacking/'
    type: secondary
---

简单说，tool calls RL 里，reward function 就是数据的标签。标签太粗，模型不知道错在哪；标签有偏，模型就去讨好 grader。

ToolRL 讲的是粗细。如果一次调用只算对错，「工具选对了、一个参数写错了」和「完全乱调」都是 0 分，模型分不清该往哪改。他们把奖励拆成工具名、参数名、参数值三层分别匹配，只用 4K 条数据做 GRPO，Qwen2.5-7B 在 BFCL 上从 SFT 的 36.5% 到了 58.4%。他们还试过加一项鼓励多思考的奖励，1.5B 的模型直接从 46% 掉到 33%。tool calls 要的是选对工具、填对参数，想得长没用。

Kimi K2 讲的是没有真实工具时怎么办。他们合成了几千个工具，有真实的 MCP 工具，也有编出来的，再组合成几百个 agent，让它们和模拟的环境、模拟的用户多轮交互。每个任务配一份 rubric，用 LLM judge 打分过滤，留下的 trajectories 拿去做 rejection sampling 和 RL。代码类任务在真实沙盒里跑单测。

这条路的问题也很明显。模拟环境返回什么是模型生成的，往往比真实 API 好说话，模型学不会处理真实的报错；judge 要是和生成模型同一家，偏好还会被放大。所以能用真实执行判分的就用执行，再定期挑一批任务去真实 API 上重跑，看成功率差多少。

如果让我来做工具 RL 的数据，我会先把奖励拆细，长度、格式这类代理项的权重压得很小；合成环境定期和真实环境对齐；再留一批训练里没见过的工具做 held-out，看模型学到的是通用的调用能力，还是记住了某几个 schema。

## 追问

**SFT 还要做吗？**
看情况。ToolRL 在小数据上直接 RL 更好，但 Llama-3.2-3B 上两种做法差不多，说明和 base model 有关。多轮、格式复杂的场景，先用少量 SFT 教会调用格式，RL 会稳很多，见 `dt-agent-fireact`。

**多步任务为什么拆成单步来训？**
单步好给细粒度的奖励，训练也稳。代价是学不到跨步的规划和出错后的恢复，这些还得靠完整 trajectories 上的 outcome reward 来训。

**奖励被 hack 了怎么发现？**
奖励一直在涨，人看行为却在变差，就是代理指标没约束住。Lilian Weng 那篇 reward hacking 综述收了很多例子，说到底就是 proxy reward 和真实目标之间有缝，模型迟早会找到。

**模拟环境太「配合」怎么办？**
往里掺真实的报错和错误注入，让模型练习出错之后怎么恢复，见 `dt-tool-error-recover`。模拟用户也一样，要给它设人设和隐藏目标，偶尔改需求、给错信息，见 `dt-agent-user-sim`。

相关：`dt-tool-apigen`、`dt-synth-tool-mm`、`dt-agent-reward-spec`、`dt-tool-alias`、`dt-tau-passk`
