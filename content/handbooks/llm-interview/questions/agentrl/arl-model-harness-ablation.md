---
id: arl-model-harness-ablation
section: agentrl
order: 11
level: S
title: 怎么判断提升来自 Model，还是 Harness / Tool / Budget？
quick: >-
  必须做 controlled ablation：固定 model、tools、token
  budget、environment、scaffold，只替换一个变量；最好做 model×harness 交叉矩阵，分离 main effect 和
  interaction。
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

错法：拿 B+贵 harness 对比 A+穷 harness，把差值全记在模型头上。换了更强搜索、更多 retry、更长 context、更多子 Agent，分数涨了，不能写成「模型变强」。这些都是 test-time compute 和脚手架。声称 model gain 时必须冻结工具集与预算。SWE-bench 一类榜已经说明：分数是系统属性，提交若各带私有脚手架，横向比的是产品不是权重。

## 交叉矩阵，而不是单点对比

最小 $2\times 2$：模型 $A/B$ × harness $X/Y$。若 $B$ 只在 $Y$ 上强，存在 interaction，不能把 $B+Y$ 对 $A+X$ 的差归因给模型。工具、步数上限、并行、检索器、确认策略、token budget、Skill 是否加载，都要列入 harness 轴。报告成功率同时报告 cost/latency 的 Pareto：同一预算下谁高，或同一成功率谁更便宜。只报成功会选出「砸预算的脚手架」。

Skill 与 router 也是 harness（见 `agent-skill-eval`、`agent-tool-routing`）。评 Skill 时冻结模型；评模型时冻结 Skill 和候选工具宽度。否则两边互相抢功劳。

## 先写清：评模型还是评系统

评 intrinsic model：用标准化 harness（固定工具、固定步数/超时、固定提示骨架），只换权重。评产品系统：可以全栈优化，但结论写 system improves，不写 model improves。Harness 若也要训（router、retriever），做联合消融或冻住一侧，并报训练数据与 compute，测 cross-model / cross-harness 迁移。只在自家脚手架上好的模型，泛化陈述要收。Leaderboard 常答不了「模型能力」，正因为提交之间 scaffold、tool budget、retry、prompt、并行都不同。

内部实验也一样：发版纪要里写「换模型 +8 分」必须附带「工具与步数未变」；变了就拆开两行。

最小报告模板：模型版本、工具列表哈希、步数/token 上限、retry 策略、是否加载 Skill。缺一项就不能声称消融干净。交互显著时（只在某套脚手架上赢）要如实写，不要平均掉。评测预算本身也是变量：多给三倍步数涨的分，应记在 compute 账上，不记在权重账上。声称 model gain 必须冻工具和预算；做 $2\times 2$ 交叉。只报 B+贵脚手架对 A+穷脚手架，是在偷换自变量。Pareto 上同一预算才可比。

## 追问

- **Leaderboard 为什么常答不了模型能力？** 提交之间 scaffold、tool budget、retry、prompt、并行都不同，分数是 system property。要对齐 harness 再比权重，否则比的是产品。
- **Harness 本身也要训练？** 做联合消融或冻住一侧，并报训练数据与 compute，测 cross-model / cross-harness 迁移。只在自家脚手架上好，泛化陈述要收。
- **和 Skill 评测？** Skill 是 harness 的一块。评 Skill 冻模型和预算；评模型冻 Skill。见 `agent-skill-eval`。同时改两边就不要写「模型 +8」。
- **交互显著怎么写结论？** 如实写「只在 Y 脚手架上赢」，不要平均进模型主效应。换标准 harness 掉点，说明增益在系统不在权重。
