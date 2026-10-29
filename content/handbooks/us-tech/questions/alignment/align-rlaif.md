---
id: align-rlaif
section: alignment
order: 10
level: A
title: 对齐：RLAIF，批评模型隔离，宪法条款要有反例
quick: >-
  RLAIF 把逐条偏好标注交给 AI，人仍负责原则和失败抽查。我会冻结批评模型，训练与验收换裁判，并给原则配正反例，避免把 over-refusal
  当无害、把迎合错误当尊重。
tags:
  - Anthropic
  - Google
  - RLAIF
  - Constitutional AI
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      RLAIF vs. RLHF — Scaling Reinforcement Learning from Human Feedback with
      AI Feedback
    url: 'https://arxiv.org/abs/2309.00267'
    type: primary
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: 'https://arxiv.org/abs/2212.08073'
    type: primary
  - title: Constitutional AI (Anthropic)
    url: >-
      https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback
    type: primary
---

## 可以这样回答

RLAIF 用 AI 提供偏好反馈，人负责写原则、设计比较方式并抽查失败。例如原则只写「尊重用户」，批评模型可能把同意用户的错误也判成好回答，所以还要给反例，并隔离批评模型与被训策略。Google 的 RLAIF 和 Anthropic 的 CAI 都在讨论这类反馈分工。

RLHF：人看两条回答，标 chosen/rejected，训 RM，再 RL。瓶颈是 throughput，无害性数据的标注还会给标注员带来负担。RLAIF：同样训 RM 或直接用于成对偏好损失，但偏好来自模型。人的工作上移到写原则、设计比较 prompt、抽查失败。Lee 等人表明，在 summarization 一类任务上，AI 反馈可以接近人反馈的 RLHF，前提是比较指令写清楚。

## 技术备查

RLAIF 用 AI 提供偏好反馈，人负责写原则、设计比较方式并抽查失败。例如原则只写「尊重用户」，批评模型可能把同意用户的错误也判成好回答，所以还要给反例，并隔离批评模型与被训策略。Google 的 RLAIF 和 Anthropic 的 CAI 都在讨论这类反馈分工。

## 人和模型分别负责什么

RLHF：人看两条回答，标 chosen/rejected，训 RM，再 RL。瓶颈是 throughput，无害性数据的标注还会给标注员带来负担。RLAIF：同样训 RM 或直接用于成对偏好损失，但偏好来自模型。人的工作上移到写原则、设计比较 prompt、抽查失败。Lee 等人表明，在 summarization 一类任务上，AI 反馈可以接近人反馈的 RLHF，前提是比较指令写清楚。

这套流程仍可能训练 reward model，也仍然需要人工定义目标。CAI 是 RLAIF 的一种：比较时显式读 constitution。也可以不用书面宪法，只把「更无害 / 更有用」写进 judge prompt，那是弱原则，更依赖抽查。Helpfulness 仍常走人偏好，harmlessness 走 AI 反馈，两条目标分开，不要塞进一个标量。

自奖励是其中风险更高的特例：同一策略给自己打分再更新，可能不断强化原有文风和拒答模板，分数上涨、行为却变窄。RLAIF 可以使用冻结教师，self-rewarding 默认没有这层隔离，需要单独说明。

## 怎么隔离和抽查

我会分别处理版本、家族、信息和任务的隔离：

- **版本隔离。** 批评模型 / judge 冻结，不跟被训策略同步更新。CAI 论文用单独模型（或同家族但固定 checkpoint）做比较。策略更新后，旧 judge 面对的回答会逐渐偏离它熟悉的数据分布，要定期换 judge 并做人抽查，而不是让 policy 和 judge 一起梯度下降。
- **家族隔离。** 训练用 judge A，验收用 judge B 或人。同一家族既当奖励又当 acceptance checks，策略会 overfitting judge 口味：更长、更客气、更像该家族，见 `align-reward-hack`、`align-red-team`。
- **信息隔离。** 比较 prompt 不要泄露「哪条是当前策略」。position bias（先出现的赢）要随机交换顺序。把原则文本交给批评模型（critic），不要把「请给高分」写进去。
- **任务隔离。** 被训模型如果同时生成批评和回答，批评会变成自我辩解。监督阶段的 critique-revision 可以同模型，但 RL 阶段的偏好来源应尽量换一套或至少换权重。

如果 RM 分上涨、人工切片下降，我会先查 critic 和 policy 是否同源，再查原则有没有漏洞。换 critic 家族后得分大幅下降，也提示策略可能 overfitting 了 judge。

原则还要配上正例和反例，说明它如何应用。只写「要无害、要尊重用户」，critic 容易奖励表面合规：

- 「无害」的反例：该答的医疗 / 新闻 / 虚构被拒，见 `align-over-refuse`。
- 「尊重用户」的反例：用户事实错误时仍附和，见 `align-sycophancy`。
- 「诚实」的反例：为了礼貌编造来源。
- 「有帮助」的反例：空话套壳、不解决任务。

抽查集按这些反例切片，条款改版时回归旧反例，避免修了一类又破坏另一类。Constitution 和抽查集一起版本化，记录哪次改动导致误拒上涨。人工重点找原则失效的模式，并抽查 critic 与人分歧的 pair；全量重标 AI 偏好会失去 RLAIF 的规模优势。

把反例放进 judge 提示，比单写「请更无害」更能说明 decision criteria。

相关：`align-cai`。

## 追问

**RLAIF 能完全换掉 RLHF 吗？**
在 harmlessness 上可以大幅减人标；helpful / 任务成功通常还要人。叠用比替换更常见。
**为什么不能让当前策略当唯一 critic？**
会自我强化已有模式，RM 分和真实质量脱钩。至少冻版本，验收换 judge。
**反例写进 constitution 算 overfitting 评测吗？**
反例是原则的单元测试，不是把公开 jailbreak 集背进训练。acceptance checks 仍要 held-out 失败模式。
**和 CAI 一句话分？**
CAI 是带书面宪法的 RLAIF 流水线（SL 改写 + AI 偏好 RL）。RLAIF 更泛，比较指令可以没有长宪法。
**helpful 和 harmless 用同一个 critic 行吗？**
不建议。目标冲突时同一个 judge 会倒向更好打分的那一侧，通常是拒答或套话。分开比较、分开抽查。
