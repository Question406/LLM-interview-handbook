---
id: align-debate
section: alignment
order: 27
level: A
title: 对齐：Debate / 递归监督的公开概念
quick: >-
  裁判比辩手弱时，不直接判最终答案，而是让双方交叉质询，把漏洞摆到弱裁判能看懂的地方。递归监督把「谁来监督辩手」再套一层。
  这是可扩展监督的思想实验；生产上更常见的是原则 + 抽查（CAI），不是每天开两模型对辩。
tags:
  - Anthropic
  - OpenAI
  - Debate
  - Oversight
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: AI safety via debate
    url: https://arxiv.org/abs/1805.00899
    type: primary
  - title: Supervising strong learners by amplifying weak experts
    url: https://arxiv.org/abs/1810.08575
    type: primary
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: https://arxiv.org/abs/2212.08073
    type: primary
---

Anthropic / OpenAI 对齐岗会把 Irving、Christiano、Amodei 的 debate 当「人盖不住模型时怎么办」的公开语言。Christiano 的 Iterated Amplification 是同一家族：把难题拆成弱专家能判的子问题。不是某次现场逐字题。不要答成「Claude 就是两个模型每天辩论」。工程落地更近 CAI，见 `align-cai`。师生能力差见 `align-weak-strong`。

## 弱裁判为什么可能够用

设定：正方 $\pi_A$、反方 $\pi_B$ 就命题 $x$ 轮流发言，弱裁判 $J$ 只看辩论记录再选边。希望是：谎言要维持一致性，交叉质询会把矛盾压到 $J$ 能识别的粒度；诚实方更容易赢。这和「让 $J$ 直接给超长答案打分」不同：后者就是弱 RM，钻缝见 `align-overopt-rm`。

面试要主动说失败模式，否则像在背摘要：

- **说服而非求真。** 若 $J$ 本身是偏好模型，辩论优化的是赢 $J$，文风、长度、自信腔都会被选中，见 `align-length-bias`、`align-llm-judge`。
- **串通。** 两辩手同一模型家族，可以学到对 $J$ 不可见的协议，把真问题藏起来。多模型、随机边、允许裁判提问能缓解，不是根治。
- **不可检查的步骤。** 代码、工具、多模态证据若裁判跑不动，质询变成空话。能验证的子问题应交给程序，见 `align-rft`。
- **递归深度。** 「谁监督辩手」若还是同样弱的 $J$，只是多套了一层同构问题。Amplification 的公开说法是：每层只要求人 / 弱模型做短、可检的判断，复杂工作交给拆解。

CAI 可以看成把「对手模型」换成「书面条款」：批评 / 改写是单边的自我辩论，人维护条款而不是当场当裁判。RLAIF 的隔离见 `align-rlaif`。面试对照：debate 强调对抗；CAI 强调可版本化原则。都还需要人抽查失败模式。

## 递归监督怎么讲一层就够

一层：人只比较两段辩论，不写完整答案。两层：对「哪一段质询更公平」再开一次短辩论。工程上很少真堆很多层。更常见的是任务图：检索、单测、引用核对这些节点用工具当裁判，开放价值判断才走人 / 原则。Agent 评测里的任务图同构，见 `design-eval-agent`。

白板不要画十二个 agent。画：$x$ → 两边发言 → $J$ 的接口（能看什么、能跑什么工具）→ 输出谁赢 → 这个胜负如何变成训练信号（偏好、RFT grader）。训练信号一旦变成「赢裁判」，又回到 proxy。held-out 必须是另一类裁判或真任务成功。

和红队的关系：debate 不是自动红队。红队要覆盖分类和 held-out 攻击，见 `align-red-team`。辩论协议可以被当成生成对抗样本的方式，但它过拟合自己的裁判时，安全数字会假绿。

公开文献里三件套别混：debate 是对抗论证；Iterated Amplification 是把题拆短；递归奖励建模是用模型帮人打奖励，再递归。CAI 更像「条款版单边批评」，便宜、可版本化，但没有对手专门找漏洞。面试被问「你们怎么 scalable oversight」时，先承认人盖不住，再选一条能检查的子问题交给程序（RLVR），开放价值才走人 / 原则 / 偶尔辩论。不要画一个十二层辩手图当答案。

和 RM 过优化同一句：胜负若来自弱 $J$，策略会钻 $J$ 的缝，长度和自信腔先被选中。所以辩论胜率不能当发版金标，要另备任务成功或另一家族裁判，见 `align-overopt-rm`。工具环上能跑的检查不要改成「让两个 agent 辩论该不该点提交」。

Anthropic 岗若已经问过 CAI，debate 用来对照「对抗 vs 原则」；OpenAI 岗更常从 weak-to-strong 滑过来。两种都不要承诺已部署成训练主路径。白板收尾写：$J$ 的接口比辩手模型名重要（它能跑代码吗、能看图吗、只能看文字吗）。

## 追问

- **生产系统在用 debate 吗？** 当作监督思想。线上更常见 SFT + 原则 / CAI + 可验证 RL + 人抽查。
- **为什么诚实方该赢？** 假设谎言更难在交叉质询下自洽，且裁判能看见相关证据。这两条随时可破。
- **和过程奖励一样吗？** 不一样。过程奖是给步骤打标量；debate 是给两套论证一个比较。噪声来源不同。
- **裁判也用 LLM 行不行？** 行，但那是弱-to-strong 的判官，要防迎合和位置偏差，见 `align-llm-judge`。
- **辩论记录给用户看吗？** 默认不。那是监督过程，会泄漏策略和攻击面，见 `align-cot-leak`。
- **和 CAI 选哪个讲？** Anthropic 岗 CAI 优先；问 scalable oversight 时再用 debate / amplification 对照。
- **两辩手同一检查点行不行？** 便宜，但串通风险更高。面试要提换家族或随机边，不当成已经解决。
- **辩论能替代人抽查吗？** 不能。条款漏洞和不可检查步骤仍要人看失败切片，见 `align-cai`。
