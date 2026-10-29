---
id: minimax-agent-eval-planning-hallucination
section: agentrl
order: 103
level: S
title: MiniMax：Agent 评估怎样量化规划能力与 hallucination 率？
quick: >-
  规划和 hallucination
  要用两套可执行的定义分开测。规划看子目标在当前状态下能否达成、依赖顺序对不对、状态变了会不会重规划、最终状态满不满足判定规则；hallucination
  按事件计，编造工具或参数、无视工具结果、引用不存在的证据、越权都算，成功轨迹里也要计。最后和成功率、成本、安全按任务类型一起出表。
tags:
  - MiniMax
  - Agent Eval
  - Planning
  - Hallucination
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Minimax大模型算法面经分享-攒人品（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/0380bd3ab1ba40f48865eeff2d15d746'
    type: candidate-first-hand
---
## 真题记录

- 公司：MiniMax
- 团队 / 岗位：大模型算法
- 届别 / 流程：原帖未披露；轮次未披露
- 面试时间：原帖未披露；帖子发布于 2026-05-06
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Agent 评估体系包括哪些维度？如何衡量规划能力 vs hallucination 率？”**

我会给规划和 hallucination 各写一套能执行的定义，分开测，再和成功率、成本、安全放在一起看 Pareto。压成一个成功率，或者请 LLM judge 打个总分，都会把问题藏起来：轨迹可以「最终做成了但中间编了工具」，也可以「计划合法但执行器超时」。评估体系的总原则见 `arl-eval`。

规划要测的是状态感知，语言计划写得流不流畅不算数。评测任务里要带 dependency、hidden state、tool failure 和成本上限，然后看四件事：拆出的子目标在当前环境里是不是真的可达，别是空口号；必须先查后写的步骤有没有颠倒；观察和预期不符时有没有改分解，也就是 replan，见 `agent-when-to-replan`；最后环境状态是不是满足成功判定规则。评测集要主动把状态藏起来，比如库存其实是零、依赖的工具第一次调用会失败、成本只够调三次。只拿「步骤写得很完整」的静态题，测到的是文笔。

还要把计划错和执行器错分开。可以用局部 oracle、trace 标注和干预 replay：同一个计划换成确定性执行器还是失败，多半是计划的问题；计划合法、只是工具超时，不该记成不会规划。结果按错误类型分开报，短链、长依赖、注入失败后的恢复率各一项，别只给一个 plan score。

hallucination 按事件计，「看起来在胡说」不算标准。能计的事件有这几类：调用不存在的工具或 schema 之外的参数；无视 tool result，仍然断言旧事实；引用轨迹里不存在的证据、文件或 ID；把环境状态说错，比如 URL、库存、权限；执行没有授权的 action。每类报发生率和 severity，还要报它在最终成功的轨迹里占多少，成功不能把中间的 hallucination 洗白。

这些最后和 success、steps、latency、token / API cost、安全违规一起出表。单一 LLM judge 的总分会把「做成了但编过」排在前面。评估体系至少还包括任务成功、成本、安全、恢复，规划和 hallucination 是其中两根轴，互相替代不了，也别被总分稀释。在提示层拦截 hallucination 的做法可以对照 `xiaohongshu-hallucination-prompt`，这题讲的是评测怎么定义。

## 追问

**最终成功了还要报 hallucination 吗？**
要。成功轨迹里有无证据的断言，说明这个策略不能部署，只是这次没出事。

**Judge 能不能打规划分？**
只能当辅助。主指标要能对照环境状态或规则来判，judge 自己也会 hallucination。

**和普通任务成功率有什么区别？**
成功率是 outcome，规划和 hallucination 是轨迹质量。只报成功率，会把危险的或者效率极低的路径藏起来，见 `arl-eval`。

**Replan 怎么自动标？**
在 tool failure 或隐藏状态翻转的地方，看后续的分解有没有变化。没变、还在重复原来的 action，就记一次规划失败。
