---
id: align-debate
section: alignment
order: 27
level: A
title: 对齐：Debate / 递归监督的公开概念
quick: "Debate 让双方交叉质询，把复杂输出里的漏洞缩小到弱裁判能检查的范围；递归监督再把监督工作拆成短判断。它依赖证据可检查、裁判不易被迎合，生产中应优先用工具验证子问题，再结合原则和人抽查，独立评测真实任务成功。"
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

Debate 想解决的是：模型比人更强时，能否通过双方交叉质询，把错误暴露到人能够检查的粒度。它是一种可扩展监督思路，成立需要裁判能检查相关证据，也需要辩论奖励与真实正确性尽量一致。

正方 $\pi_A$ 与反方 $\pi_B$ 围绕命题 $x$ 轮流发言，弱裁判 $J$ 看记录选边。希望谎言更难持续自洽，对方能把矛盾缩成一个短问题，让诚实方更容易赢。若直接让 $J$ 给复杂长答案评分，就会回到弱 RM 被钻漏洞的问题，见 `align-overopt-rm`。Irving、Christiano、Amodei 的公开 debate 工作讨论这条路线；Christiano 的 Iterated Amplification 则强调把难题拆给弱专家检查。这道题不是现场逐字记录。

例如代码或工具结果可以执行检查，就先交给程序，见 `align-rft`。裁判连代码都跑不了时，两方对实现正确性的争论很容易只剩说服。如果 $J$ 是偏好模型，文风、长度、自信腔可能比证据更能赢，见 `align-length-bias`、`align-llm-judge`。同一家族的两个辩手还可能形成裁判看不见的协议，隐藏真正的问题；换模型家族、随机分边、允许裁判提问可以缓解，但不能保证消除。

## 递归如何落到可检查的工作

一层监督可以让人只比较两段论证；再一层，可以针对“哪段质询更公平”开一次短比较。若每层仍要求同一个弱裁判直接判断不可检查的问题，只是重复原困难。Amplification 的要求是每层只做短、可检的判断，把复杂工作交给拆解。

工程上更常用任务图：检索、单测、引用核对由工具检查，开放价值判断交给人或原则，见 `design-eval-agent`。白板可以画 $x$、两边发言、$J$ 能读什么和运行什么、胜负怎样变成偏好或 RFT grader。裁判只能看文字、能否看图或运行代码，比辩手模型名更能决定可检查的范围。

CAI 用可版本化条款驱动批评和改写，可视作单边自我批评；debate 更强调对手找漏洞，两者都需人抽查，见 `align-cai`、`align-rlaif`。公开概念也要区分：debate 是对抗论证，Iterated Amplification 是拆短问题，递归奖励建模是用模型辅助人打奖励再递归，师生能力差见 `align-weak-strong`。

不能把辩论胜率当发版标准。胜负仍是 proxy，要用另一类裁判或真实任务成功做 held-out。辩论也不自动替代红队，仍需攻击分类和未见攻击集，见 `align-red-team`；它可生成对抗样本，但也会过拟合自己的裁判。生产更常结合 SFT、原则 / CAI、可验证 RL 与人抽查，不能声称 Claude 已经把双模型辩论作为日常主训练路径。Anthropic 语境可用 CAI 对照原则与对抗，OpenAI 语境可接 weak-to-strong，均不承诺部署细节。

## 追问

**为什么诚实方应该赢？**
这依赖谎言更难自洽、且裁判看得见证据，两条假设都可能失败。

**和过程奖励一样吗？**
不同。过程奖给步骤一个标量，debate 比较两套论证，噪声来源不同。

**裁判也能用 LLM 吗？**
能，但要防迎合与位置偏差，见 `align-llm-judge`，并用独立任务结果验证。

**两个辩手能用同一检查点吗？**
可以降低成本，但串通风险更高，换家族或随机分边仍只是缓解。

**辩论记录给用户看、能替代人抽查吗？**
默认不展示监督记录，避免泄漏策略和攻击面，见 `align-cot-leak`。不可检查步骤与条款漏洞仍要人查失败切片，不能取消抽查。
