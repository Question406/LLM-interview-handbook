---
id: minimax-agent-eval-planning-hallucination
section: agentrl
order: 103
level: S
title: MiniMax：Agent 评估怎样量化规划能力与幻觉率？
quick: >-
  不能把两者压成单一成功率。规划测 state-aware subgoal、依赖顺序、replan 与最终完成；幻觉测不可用工具 / 参数、无证据断言、错误
  grounding 与未授权 action。要有可执行 oracle、trace 级标签、成本 / 安全约束和分桶报告。
tags:
  - MiniMax
  - Agent Eval
  - Planning
  - Hallucination
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Minimax大模型算法面经分享-攒人品（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/0380bd3ab1ba40f48865eeff2d15d746
    type: candidate-first-hand
---
## 真题记录

- 公司：MiniMax
- 团队 / 岗位：大模型算法
- 届别 / 流程：原帖未披露；轮次未披露
- 面试时间：原帖未披露；帖子发布于 2026-05-06
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Agent评估体系包括哪些维度？如何衡量规划能力 vs 幻觉率？”**

不能把规划能力和幻觉率压进一个成功率。轨迹可以「最终做成了但中间编了工具」，也可以「计划合法但执行器超时」。MiniMax 这问要两套 **可执行定义**，再和成本 / 安全一起做 Pareto，而不是请 LLM judge 打总分。总原则见 `arl-eval`。

## 规划：测状态感知，不测文笔

规划指标不能用语言计划的流畅度代替。任务要带 dependency、hidden state、tool failure 与成本上限，然后分别看：

- **Subgoal 可达：** 拆出的中间目标在当前环境是否真的可达，而不是空口号。
- **依赖顺序合法：** 必须先查后写的，有没有颠倒。
- **Replan：** 观察与预期不符时是否改分解，见 `agent-when-to-replan`。
- **Goal-state：** 最终环境是否满足成功 oracle。

要用局部 oracle、trace 标注和干预 replay 区分 **plan 错** 与 **executor 错**：同一计划换确定性执行器仍失败，多半是计划；计划合法但工具超时，不应记成不会规划。报告按桶：短链 / 长依赖 / 注入失败后的恢复率，而不是一个 plan score。规划评测集要主动藏状态：库存其实为零、依赖工具第一次失败、成本只够三次调用。只拿「步骤写得很完整」的静态题，测到的是文笔。

## 幻觉：拆错误类型，成功轨迹也要计

幻觉率按事件计，不要「看起来在胡说」：

- 调用不存在的工具或参数（schema 外）；
- 忽略 tool result，仍断言旧事实；
- 引用轨迹里不存在的证据 / 文件 / ID；
- 错误环境状态（URL、库存、权限）；
- 未授权 action。

每类报 rate、severity，以及 **最终成功轨迹中的比例**——成功但不能洗白中间幻觉。和 success、steps、latency、token / API cost、安全违规一起出表。单一 LLM judge 总分会把「做成了但编过」排到前面。提示层拦截对照 `xiaohongshu-hallucination-prompt`，本题强调的是评测定义。评估体系至少还有：任务成功、成本、安全、恢复。规划与幻觉是其中两根轴，不能互相替代，也不能被总分稀释。

面试收口：规划看 subgoal / 顺序 / replan / 终局；幻觉看不可用工具、无证据断言、错误 grounding、越权。两套指标 + 成本安全 Pareto，不用一个分数代替。

## 追问

- **最终成功了还要报幻觉吗？** 要。成功轨迹里的无证据断言说明策略不可部署，只是这次没爆。
- **Judge 能不能打规划分？** 只能当辅助。主指标必须能对照环境状态或规则。Judge 自己会幻觉。
- **和普通任务成功率？** 成功率是 outcome。规划与幻觉是轨迹质量。只报前者会掩盖危险或极低效路径，见 `arl-eval`。
- **Replan 怎么自动标？** 在 tool failure / 隐藏状态翻转处看后续分解是否变化。不变还重复原 action，记规划失败。
