---
id: pt-long-to-short-reasoning
section: posttrain
order: 30
level: S
title: 如何把 Long-CoT Reasoner 蒸馏成短思考模型，同时尽量不掉能力？
quick: 不是简单删 token。先筛出正确且有信息密度的长轨迹，训练学生保留关键决策或答案，再用质量–token 曲线验证；若任务需要中间证明，应蒸馏状态转移而非只蒸馏最终答案。
tags:
  - Distillation
  - Chain of Thought
  - Efficiency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Kimi k1.5
    url: https://arxiv.org/abs/2501.12599
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
---

Long-to-short 是把已经会做长思考的 teacher 压成短思考学生，而不是把长 CoT 截断当监督。目标是在相近准确率下显著降低平均 / P95 reasoning token。面试陷阱是「把长轨迹删掉后半段再 SFT」：删掉的往往是真正的分支决策、验算和纠错，留下的是套话。Kimi k1.5 等配方强调先有强 long-CoT，再压长度；这和 `pt-adaptive-thinking-budget`（推理时决定想多久）、`pt-reasoning-token-cost-frontier`（训练时惩罚无效 thinking）互补，但改的是学生的监督信号。

## 先过滤，再决定蒸馏什么

Teacher rollout 必须先过可验证答案或高质量 judge。错误但写得漂亮的长 CoT 是有害监督：学生会学会「用很长的正确语气走到错误结论」。过滤后还要看信息密度：关键决策、反例、工具返回后的状态更新是否还在。压缩目标按下游需求选：

- 短 rationale：保留可审计步骤。
- 关键步骤摘要：只留状态转移。
- 只输出答案：把过程留在训练信号里，线上不暴露。

若任务本身需要中间证明（数学推导、代码不变量），应蒸馏「在什么状态下做什么下一步」，而不是只蒸馏最终答案。只学答案在分布内能撑住 `pass@1`，一换题型或要审计就塌。压缩时优先删重复验算、自我鼓励和复述题面，保留：分岔点、反例、工具返回后的状态改写、最终校验。删错这四类，短模型会在需要回退的题上一次性走死。

## 训练时同时约束正确性和长度

常见做法：按 token bucket 训出多预算版本；或把目标长度当条件输入，让同一学生在短 / 中 / 长模式间切换。损失上同时打正确性（或 token-level 蒸馏）和长度。$\lambda$ 过大，学生删掉验算；过小，只是换了一种「假装短」的套话。条件长度若只出现在系统提示、从不在训练标签里对齐，线上会忽略。

离线 SFT 只在 teacher 前缀上学习，学生一走偏就 OOD。更稳的是 `pt-on-policy-distillation`：学生自己 rollout，teacher 在学生实际访问的状态上给短续写或分布信号。teacher 轨迹和学生会访问的状态分布不一致，是 long-to-short 最常见的静默失败：验证集上模仿 loss 很低，一开采样就回到又长又乱的自己。

也可以先让学生生成短草稿，teacher 只修补缺失的关键步，而不是重写全文。这样长度由学生控制，正确性由 teacher 托底，比「把长链截断到 200 token」更不容易砍掉决策。

## 评估必须画质量–token 曲线

不要只报「平均更短」。同一题集上报告准确率、平均 / P95 token、延迟，以及按预算截断的退化曲线。简单题应明显变短且准确率持平；难题允许保留更长思考。还要测 OOD 和需要中间证明的子集：若短模型只在原分布上不掉点，多半是背了短答案模板。曲线应和 `pt-adaptive-thinking-budget` 的控制器一起看：短模型是新政策，控制器是同一政策上的开关。

失败模式可以白板列举：删掉分支决策、只模仿表面措辞、长度条件被忽略、teacher 偏差被更高效地继承、过滤阈值过松把错长链放进来。出现后先查过滤，再查学生状态是否离线。抽检时不要只看最终答案，要问「这一短步是否还对应 teacher 的那个决策」。

白板口令：过滤正确性，蒸馏状态转移，用质量–token 曲线验收；平均长度下降而难题切片塌掉，就是失败的压缩。

交付清单可以压成三句话：只蒸馏过滤后的正确高密度轨迹；监督的是状态转移不是删节散文；验收看质量–token 曲线和难题切片，不看平均长度。

## 追问

- **和直接加长度惩罚有何不同？** 长度惩罚改同一策略的 reward（`pt-reasoning-token-cost-frontier`）；本题换一个更小 / 更短的学生，监督来自已验证的长轨迹。两者可叠：先有长 teacher，再压学生，线上再用预算控制器。
- **为什么错误长 CoT 特别毒？** 它同时教错误算法和「长 = 认真」的风格，后续 RL 会把这两种都放大。过滤必须先于压缩，不能指望长度损失把错链「罚短」。
- **必须保留可读 CoT 吗？** 取决于产品：要审计就蒸馏短 rationale；只要答案且有独立 verifier，可以压到答案加内部信号。若还要 `pt-cot-monitorability-regression`，短 rationale 不能短到监控器失明。
- **学生比 teacher 弱很多怎么办？** 先降难度或先冷启动格式，再蒸馏状态转移；硬学超难长链会 degeneracy。也可改 on-policy：学生走自己的状态，teacher 只给下一步，而不是整段模仿。
