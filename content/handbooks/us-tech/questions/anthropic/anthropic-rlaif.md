---
id: anthropic-rlaif
section: anthropic
order: 10
level: S
title: Anthropic：RLAIF 和 RLHF 的人在环里位置差在哪？
quick: "基于人类反馈的强化学习（RLHF） 的人标每一对 chosen/rejected。RLAIF 的人写原则、抽查失败模式，对比标签由模型按条款生成。后面的 PM 和 PPO 几乎一样。人仍参与，只是从逐条标注改为制定原则和审计结果。"
tags:
  - Anthropic
  - RLAIF
  - RLHF
  - Constitutional AI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: https://arxiv.org/abs/2212.08073
    type: primary
  - title: Constitutional AI (Anthropic research)
    url: https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback
    type: primary
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: https://arxiv.org/abs/2204.05862
    type: primary
---

RLAIF 这个词是 CAI 论文里带出来的：强化学习（RL） from AI Feedback。对齐岗常把它和 InstructGPT 式 基于人类反馈的强化学习（RLHF） 对打。我会先画人站在哪，再讲哪一段还完全一样，避免答成「CAI 没人了」或「CAI 没有奖励模型」。

## 人从「逐对标注」挪到「写原则 + 抽查」

HH-RLHF（`anthropic-hh-rlhf`）里，helpful 和 harmless 的对比都来自人。Harmless 尤其贵：标注员要反复看红队内容，吞吐低，心理负担大，一致性也差。

CAI 把 harmlessness 的监督改成：

1. 人写 constitution。可版本化的条款列表（人权、非歧视、别过度拒绝、遵守法律）。冲突写进文本：无害优先，同时单列条款压过度拒绝。
2. SL 阶段。模型按条款批评自己的有害回答，再改写。人几乎不标这对数据；用改写做监督微调。
3. RL 阶段（RLAIF）。对同一输入提示 采两条回答，让另一个模型按某条原则做选择题，得到 AI 对比。用这些对比训 PM，再 PPO。论文里 helpful 对比仍可混入人类数据，harmless 对比用 AI。

人还在环里的位置：改条款、看评测仪表盘、抽查原则失效的 case（自嗨、讨好、条款漏洞）。不是消失，是带宽从「每条偏好」变成「原则工程」。

## 管道后半截几乎是 RLHF

对比一旦变成 $(x, y_w, y_l)$，后面和 RLHF 相同：

- 用 Bradley-Terry 训 $r_\phi$，见 `anthropic-pref-bt`；
- PPO 的奖励仍是 $r_\phi(x,y) - \beta \log(\pi_\theta/\pi_{\mathrm{ref}})$，锚在 SL 模型上；
- 照样会 钻奖励规则的空子、长度膨胀、讨好评委。

所以「RLAIF 没有 RM」是错的。CAI 论文写得很清楚：AI 反馈被蒸馏进 preference model，再 RL。换成「完全没有奖励模型」就答偏了。

评委模型和被训模型要隔离版本。用正在优化的 $\pi_\theta$ 给自己打分，等于 self-rewarding，会塌。批评模型冻结，条款固定，人抽查的是原则失败模式。Google 后来的 RLAIF 工作把「AI 标注 + 人写原则」做成更通用的配方；面试声明你讲的是 Anthropic CAI 原设定即可。

## 和 system 输入提示（prompt）、蒸馏的差别

推理时把 constitution 贴进 system prompt，只改变这一次 $p(y\mid x,C)$。RLAIF 改变的是权重里的偏好分布，离线后不必每次带上长条款。`anthropic-context-distill` 是第三条路：用 KL 把「带 $C$ 的教师」压进学生，也不等于 RLAIF——蒸馏没有对比数据和 PPO。

人写的原则会漏。漏了就规模化地错。RLHF 的漏是标注员口味；RLAIF 的漏是条款没覆盖的有害类型。补救是改 constitution 再生成反馈，而不是指望模型「自己悟」。公开 Claude constitution 就是给人审的，不是藏起来的系统提示。

评测不要只看「红队胜率涨了」。CAI 论文强调 harmless 但非 evasive：有害请求上解释为什么不帮，无害请求上照常帮。只优化拒答率，helpful 会塌，HH 那条 Pareto 又回来了。我会同时报有害完成率、过度拒绝率、helpful Elo。

## 追问

- **Helpful 为什么还用人？** 有用性更主观、更依赖产品，条款难写全。CAI 原论文是 hybrid：helpful 人标，harmless AI 标。不要说全部反馈都是 AI。
- **AI 对比要不要 CoT？** 论文用思维链让评委先引条款再选。CoT 提高人评一致，但也暴露推理，可能被拿来攻击评委。生产要把评委藏在离线。
- **和 RLHF 能叠吗？** 能，而且应该叠。人标解决条款写不清的域（代码风格、产品语气），AI 标解决规模化无害。
- **标注员不看有害内容了，对齐就算自动了？** 没有。人改去看原则失败和红队评测。责任上移，不是消失。
