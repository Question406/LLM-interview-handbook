---
id: arl-model-harness-ablation
section: agentrl
order: 11
level: S
title: 怎么判断提升来自 Model，还是 Harness / Tool / Budget？
quick: "做受控消融：固定模型、工具、token 预算、环境和运行框架，每次只改一个变量；再做模型 × Harness 的 2×2 交叉，把模型本身的效果和两者配合产生的变化分开。B 配高预算 Harness 与 A 配低预算 Harness 的差值，不能直接记成模型增益，结果还要同时报成本和延迟。"
tags:
  - Eval Design
  - Harness
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: SWE-bench
    url: 'https://arxiv.org/abs/2310.06770'
    type: primary
---

做受控消融：固定模型、工具、token 预算、环境和运行框架，每次只改一个变量；再做模型 × harness 的交叉矩阵，把模型本身的效果和两者配合产生的效果分开。最常见的错，是拿 B 配贵 harness 去比 A 配穷 harness，再把差值全记到模型头上。

比如发版纪要里写「换模型 +8 分」，可同一个版本还换了更强的搜索、加了 retry、拉长了 context、多开了子 Agent。这些都是 test-time compute 和脚手架，涨的分不能写成「模型变强」。所以要声称是模型增益，就得冻结工具集和预算；工具和步数变了，就拆成两行写。

## 交叉矩阵，比单点对比可靠

最小的矩阵是 $2\times 2$：模型 $A/B$ × harness $X/Y$。如果 $B$ 只在 $Y$ 上强，就存在 interaction，$B+Y$ 对 $A+X$ 的差不能归给模型。工具、步数上限、并行、检索器、确认策略、token 预算、Skill 有没有加载，都算 harness 这一轴。报成功率的同时，报 cost/latency 的 Pareto：同一预算下谁高，或者同一成功率谁更便宜。只报成功，会选出「砸预算的脚手架」。评测预算本身也是变量，多给三倍步数涨的分，记在 compute 账上，别记在权重账上。

Skill 和 router 也属于 harness，见 `agent-skill-eval`、`agent-tool-routing`。评 Skill 时冻结模型，评模型时冻结 Skill 和候选工具的宽度，否则两边互相抢功劳。

## 先写清楚评的是模型还是系统

评模型本身（intrinsic model），就用标准化 harness，固定工具、固定步数和超时、固定提示骨架，只换权重。评产品系统可以全栈优化，但结论要写成 system improves，别写 model improves。SWE-bench 一类榜已经说明，分数是系统的属性，提交各带私有脚手架时，横向比的是产品，比不出权重。

最小报告模板包括模型版本、工具列表哈希、步数 / token 上限、retry 策略、是否加载 Skill，缺一项就不能说消融是干净的。

## 追问

**Leaderboard 为什么常常答不了模型能力？**
提交之间的 scaffold、tool budget、retry、输入提示（prompt）、并行都不一样，分数是 system property。要先对齐 harness 再比权重，不然比的是产品。

**Harness 本身也要训练怎么办？**
做联合消融，或者冻住一侧，同时报训练数据和 compute，再测 cross-model / cross-harness 迁移。只在自家脚手架上好的模型，泛化的说法要收着说。

**评 Skill 时怎么控制变量？**
Skill 是 harness 的一块。评 Skill 冻模型和预算，评模型冻 Skill，见 `agent-skill-eval`。两边同时改，就别写「模型 +8」。

**交互效应显著时结论怎么写？**
如实写「只在 Y 脚手架上赢」，别平均进模型的主效应。换到标准 harness 就掉点，说明增益在系统里，不在权重里。
