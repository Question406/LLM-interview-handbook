---
id: dt-case-web-skill
section: cases
order: 3
level: S
title: "案例 2/4：先写 test-time skill 补能力，什么时候该训进权重？"
quick: "先写一份几百 token 的设计 skill 放进上下文，当天就能对照。skill 能修好的部分说明模型会、只是缺引导，适合之后训进权重；修不好的才要去造数据。效果稳定、调用频繁、上下文成本明显的时候，就该把它训进模型。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - Data Story
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Anthropic: Improving frontend design through Skills"
    url: https://claude.com/blog/improving-frontend-design-through-skills
    type: secondary
  - title: "Which Skill to Distill? SGUID: Selecting a Compact Skill Bank for Model–Skill Co-Evolution"
    url: https://arxiv.org/abs/2610.12367
    type: primary
  - title: "Skill-SD: Skill-Conditioned Self-Distillation for Multi-turn LLM Agents"
    url: https://arxiv.org/abs/2604.10674
    type: primary
---

简单说，诊断出设计趋同以后，我们先写了一个设计 skill，没急着造数据。它最便宜：几百 token 的规则，遇到网页任务才加载，当天就能在冻结评测上做对照。它也顺便当了一次诊断：skill 能修好的，说明模型会做只是缺引导，适合之后蒸馏进权重；修不好的，才需要去造新数据。

skill 里写的是〔填：你们覆盖的规则，比如字体、配色、布局、动效〕。写法上我会坚持两点。规则要写成能检查的样子，比如「首屏至少有一个视觉焦点」，后面可以直接变成 judge 的 checklist。反例要具体，写「白底加紫色渐变的 hero」，模型就知道该避开什么；写「别太普通」，它没法执行。

对照就是同一批 prompt，有 skill、没 skill 各跑一遍，三层分数分开看。视觉分涨没涨是一方面，还要看功能分有没有掉，规则塞太多会挤掉模型对功能的注意。再看页面是不是又都变成了同一种「好看」，统计一下字体和主色的分布就知道。〔填：对照结果。〕

skill 有效以后，我们还是决定把它训进模型。一是每次调用都要多花上下文；二是 skill 得先被检索到才生效，任务描述不太像网页的时候就可能漏掉；三是审美上的整体感很难全写成规则，蒸馏能把带 skill 时的整体行为一起带过去。怎么训见 `dt-case-web-internalize`。

## 追问

**所有 skill 都值得训进去吗？**
不一定。SGUID 那篇发现，检索到的 skill 里不到 25% 在蒸馏时真正有用；只挑 6 个去蒸馏，效果就能追平甚至超过整个 skill 库，不挑的话有的模型还会掉分。所以先用对照证明 skill 有用，再拿它造数据。

**skill 和 system prompt 有什么区别？**
内容可以一样，区别在按需加载。它只在相关任务里进上下文，所以可以写得更长、更专门。

**训进去以后 skill 还要吗？**
可以留着兜底，也可以接着迭代。Skill-SD 这类工作就是循环着做：训完之后用新模型的 rollout 总结下一批 skill，再挑值得蒸馏的。

**Anthropic 那个 frontend skill 里写了什么？**
大约 400 token，分字体、配色、动效、背景四块，还专门提醒模型别收敛到新的默认值，比如所有页面都换成 Space Grotesk。

相关：`dt-case-web-diagnose`、`dt-prompt-rag-ft`、`dt-adapter-vs-base`
