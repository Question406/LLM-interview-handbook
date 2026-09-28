---
id: agent-skill-eval
section: agent
order: 9
level: S
title: 怎么评估一个 Agent Skill 写得好不好？
quick: >-
  别只看 Skill 内容是否「合理」。做 no-skill / metadata-only / full-skill / optimized-skill
  ablation，测 task success、tokens、tool calls、latency、robustness 和 interference。
tags:
  - Skill
  - Eval
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Equipping agents for the real world with Agent Skills
    url: 'https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills'
    type: primary
---

Skill 读着「很合理」不等于上线有增益。它可能泄漏了评测答案、只对某一模型有效，或误触发伤害相邻任务。评的是同一模型、同一 harness 下只改 Skill 条件的因果效应，不是文笔。错法：开卷改完 Skill 就宣布「Agent 更强了」。Anthropic 把 Skill 写成可加载的程序性说明书，价值应落在「少走弯路」，而不是把题解写进文档。

## 对照实验：只改 Skill

固定任务集、工具、预算，只切换 Skill：

- No skill：基线能力；
- Metadata only：名字/触发描述是否已有提示效应；
- Full skill：真实增益；
- Full + distractors：抗干扰、误触发；
- 旧/新版本：回归。

增益应同时看成功率、token、tool-call 次数、延迟。程序性 Skill 的价值常在减少无效探索，而不只是抬 accuracy。还要测 negative transfer：目标任务 +10%，相邻任务误触发 −20%，净效益为负就不是好 Skill。效率用 success per token / per tool-call / per latency。只报成功、不报成本，会选出「更啰嗦的说明书」。Skill 是 harness 的一块：评 Skill 时冻结模型和预算；反过来声称模型变强时也要冻结 Skill，见 `arl-model-harness-ablation`。

## 防泄漏，并承认模型绑定

Skill 应写 procedure（先查再改、失败怎么停、何时问用户），不是 benchmark 的标准答案或隐藏数字。用 held-out 实例、参数化任务、藏答案、换域变体；若拿掉数字答案成功率崩盘，这是作弊不是 Skill。不同模型对同一篇自然语言 Skill 理解差很大，应把它当 model-conditioned artifact：要么分模型变体，要么写更结构化、可执行的步骤，降低「会不会读长文」的差异。评测集要和 Skill 作者隔离，避免边看失败 case 边把答案写进下一版。

发布门禁：相对 no-skill 的成功增益、token 不涨或涨幅可解释、distractor 条件下误触发低于阈值、held-out 变体不崩。过不了就当文档，不当默认加载。Skill 仓库要有版本和回归集，和代码一样审。「写得清楚」不是合并条件，「对照实验有增益且无负迁移」才是。作者边看失败边改 Skill，评测必须 held-out，否则增益只是把答案写进了说明书。

## 追问

- **如何判断 Skill 只是把答案泄漏进去？** 用 held-out 实例、参数化任务、隐藏数字答案和跨域变体。Skill 应描述 procedure；拿掉题面特解就崩，说明在作弊。
- **不同模型效果不同怎么办？** 把 Skill 当 model-conditioned artifact：分模型变体，或写成更结构化的可执行清单，降低「会不会读长文」的差异。不要假设一篇散文通吃。
- **和 harness 增益怎么分？** 评 Skill 时冻结模型、工具与预算；声称模型变强时冻结 Skill。见 `arl-model-harness-ablation`。两边同时改，功劳无法拆。
- **只看成功率够吗？** 不够。要看 token、调用次数、延迟和 distractor 下的误触发。啰嗦说明书能抬一点成功，却把成本与负迁移一起抬上去。
- **Metadata-only 为什么要单列？** 名字和触发描述本身就有提示效应；不拆开会把检索增益算进 Skill 正文。
