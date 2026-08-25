---
id: align-rlaif
section: alignment
order: 10
level: A
title: 对齐：RLAIF，批评模型隔离，宪法条款要有反例
quick: >-
  RLAIF 用 AI 反馈代替人标偏好，原则仍由人写。批评模型和被训策略必须隔离版本，否则自嗨。条款要带反例：过度拒绝、谄媚、假无害，抽查的是原则失败而不是全量偏好。
tags:
  - Anthropic
  - Google
  - RLAIF
  - Constitutional AI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: RLAIF vs. RLHF — Scaling Reinforcement Learning from Human Feedback with AI Feedback
    url: https://arxiv.org/abs/2309.00267
    type: primary
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: https://arxiv.org/abs/2212.08073
    type: primary
  - title: Constitutional AI (Anthropic)
    url: https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback
    type: primary
---

Google 的 RLAIF 论文和 Anthropic 的 CAI 是同一族问题的两边：反馈从哪来、人还干什么。对齐岗常追「模型给自己打分会不会崩」。CAI 流程见 `align-cai`。本题收三个点：RLAIF 不是无 RM、批评模型要隔离、条款没有反例等于没写。

## RLAIF 在替什么，不在替什么

RLHF：人看两条回答，标 chosen/rejected，训 RM，再 RL。瓶颈是吞吐，harmless 数据还消耗标注员。RLAIF：同样训 RM 或直接当 pairwise loss，但偏好来自模型。人的工作上移到写原则、设计比较 prompt、抽查失败。Lee 等人表明，在 summarization 一类任务上，AI 反馈可以接近人反馈的 RLHF，前提是比较指令写清楚。

它不取消奖励模型，也不取消人。答成「无监督对齐」偏题。CAI 是 RLAIF 的一种：比较时显式读 constitution。也可以不用书面宪法，只把「更无害 / 更有用」写进 judge prompt，那是弱原则，更依赖抽查。Helpfulness 仍常走人偏好，harmlessness 走 AI 反馈，两条目标分开，不要塞进一个标量。

自奖励（同一策略给自己打分再更新）是更险的特例。没有隔离时，策略会强化自己已经会的文风和拒答模板，评测数字涨、行为变窄。面试把 RLAIF 和 self-rewarding 分开：前者可以是冻结的教师；后者默认不隔离。

## 批评模型怎么隔离

最低配置：

- **版本隔离。** 批评模型 / judge 冻结，不跟被训策略同步更新。CAI 论文用单独模型（或同家族但固定 checkpoint）做比较。策略更新后，旧 judge 会逐渐 OOD，要定期换 judge 并做人抽查，而不是让 policy 和 judge 一起梯度下降。
- **家族隔离。** 训练用 judge A，验收用 judge B 或人。同一家族既当奖励又当门禁，策略会过拟合 judge 口味：更长、更客气、更像该家族，见 `align-reward-hack`、`align-red-team`。
- **信息隔离。** 比较 prompt 不要泄露「哪条是当前策略」。位置偏差（先出现的赢）要随机交换顺序。原则文本给 critic，不要把「请给高分」写进去。
- **任务隔离。** 被训模型如果同时生成批评和回答，批评会变成自我辩解。监督阶段的 critique-revision 可以同模型，但 RL 阶段的偏好来源应尽量换一套或至少换权重。

隔离不是为了理论漂亮，是为了打断「自己给自己刷分」的环。发现 RM 分涨、人工切片掉，先查 critic 是不是已经和 policy 同源，再查条款是不是被钻空。换 critic 家族后分数崩，说明你在过拟合 judge，不是对齐进步。

## 条款要有反例，否则 critic 会自嗨

原则写成「要无害、要尊重用户」几乎没用。critic 会把过度拒绝当无害，把同意用户错误当尊重。每条原则配 **正例和反例**：

- 「无害」的反例：该答的医疗 / 新闻 / 虚构被拒，见 `align-over-refuse`。
- 「尊重用户」的反例：用户事实错误时仍附和，见 `align-sycophancy`。
- 「诚实」的反例：为了礼貌编造来源。
- 「有帮助」的反例：空话套壳、不解决任务。

抽查集按反例切片，不是随机聊天。条款改版要回归旧反例，防止修 A 坏 B。Constitution 可版本化：记下哪次改条款导致误拒飙升。人抽查的是原则失败模式，不是把 AI 偏好再标一遍——否则 RLAIF 的规模优势没了。条款和抽查集要一起发版，只改原则不改测试，等于没改。

Judge prompt 里列反例，比只列「请更无害」有效。仍要人看一小部分 critic 和人分歧的 pair，分歧往往就是条款漏洞。

## 追问

- **RLAIF 能完全换掉 RLHF 吗？** 在 harmlessness 上可以大幅减人标；helpful / 任务成功通常还要人。叠用比替换更常见。
- **为什么不能让当前策略当唯一 critic？** 会自我强化已有模式，RM 分和真实质量脱钩。至少冻版本，验收换 judge。
- **反例写进 constitution 算过拟合评测吗？** 反例是原则的单元测试，不是把公开 jailbreak 集背进训练。门禁仍要 held-out 失败模式。
- **和 CAI 一句话分？** CAI 是带书面宪法的 RLAIF 流水线（SL 改写 + AI 偏好 RL）。RLAIF 更泛，比较指令可以没有长宪法。
- **helpful 和 harmless 用同一个 critic 行吗？** 不建议。目标冲突时同一个 judge 会倒向更好打分的那一侧，通常是拒答或套话。分开比较、分开抽查。
