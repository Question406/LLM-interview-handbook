---
id: pt-cot-monitorability-regression
section: posttrain
order: 40
level: S
title: 强化 Reasoning 后，如何判断 CoT 仍然可被监督，而不是更难审计？
quick: "把可监控性当成后训练的回归验收项：在相同预算下，比较只看答案或动作的监控器和能看分步推理（CoT）的监控器对关键风险的检出率差，评测集里放刻意伪装的对抗样本。准确率上升推不出可监督性也变好，这个差值下降就该停发。"
tags:
  - Chain of Thought
  - Monitoring
  - Safety
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: OpenAI — Evaluating Chain-of-Thought Monitorability
    url: https://openai.com/index/evaluating-chain-of-thought-monitorability/
    type: primary
  - title: Reasoning Models Don't Always Say What They Think
    url: https://arxiv.org/abs/2505.05410
    type: primary
---

我会把可监控性（monitorability）做成后训练的一个发布门槛：在同样的监控预算下，看能读 CoT 的监控器比只看最终答案和工具动作的监控器多抓到多少真实风险。这个差值掉了，主任务分再涨也算回归。「更会推理」和「更好审计」是两件事，CoT 读起来像人话，也说明不了它能帮监控器发现问题。

为什么会退化？强化学习 reasoning 之后，主任务准确率常常上涨，分步推理（CoT）却可能变短、用上难懂的编码、和实际动作对不上，甚至学会对监控器说一套、做的是另一套。比如一道模型能利用奖励规则漏洞的题，CoT 里写「按评分标准诚实作答」，实际输出的是刷分格式；工具题里 CoT 说「只读文件」，函数调用却带了写路径。只看结果的监控器可能漏掉，看 CoT 的监控器理应抓到。post-training 之后抓不住了，就是回归。它和 `pt-safety-capability-regression` 是并列的发布门槛，要在上线前查，别等上线后再找解释。

## 先定风险，再定监控器

先落到具体风险：钻奖励规则的空子、滥用工具、隐藏目标、不安全的计划、对用户撒谎。然后跑两类监控器：只看最终答案和动作的 outcome monitor，以及能看完整或截断 CoT 的 process monitor。在固定的 token、时间和人工复核预算下，比较同一风险标签上的检出差：

$$
\Delta_{\mathrm{mon}} = \mathrm{TPR}_{\mathrm{CoT}} - \mathrm{TPR}_{\mathrm{outcome}}
$$

$\Delta_{\mathrm{mon}}$ 下降就是可监控性退化，哪怕主任务分在涨。FPR 也要报，CoT 变长会让监控器「看起来更忙」，忙不等于准。

监控器可以是规则、分类器，也可以是另一个 LLM judge。关键是它和被测模型不共享训练目标，评测前也不能把具体规则泄露给 policy。如果同时训了过程奖励，监控器更要独立，否则模型和监控器会一起拟合同一套「安全套话」。`pt-prover-verifier-legibility` 问的是 prover 怎么把证据写给能力弱一些的验证器看；这张卡问的是强化后的 CoT 还值不值得给监控器看。

评测集只放普通失败不够，要有诚实的失败、无意的漏检，还有刻意伪装：把危险计划藏进委婉语、外语、符号或者工具参数里。模型不能知道监控规则，否则它会去优化「在监控器面前显得无辜」。要测的退化有三类：简略化，关键决策被删、只剩套话；编码化，用只有模型自己懂的缩写或隐写；脱钩，CoT 里写的是安全计划，实际调用的是危险工具。只凭「看起来有解释」，会把不忠实的 CoT 判成透明。

对抗集要跟着 post-training 配方一起回归，别做成一次性的定性研究。还要测「监控器只看前 $B$ 个 token」的情况：强化学习之后模型要是把关键意图往后挪，固定预算下的 $\Delta_{\mathrm{mon}}$ 会假跌或假涨。

## 发布门槛怎么设

放行看三样：同一监控预算下的 $\Delta_{\mathrm{mon}}$、漏检的高严重度 case 数，以及 CoT-action 一致性，也就是计划里说的工具和真实调用对不对得上。主任务分只当对照，不当放行条件。主任务质量上升、CoT 给监控器的边际信息却下降了，就停发，回头查数据、奖励和工具权限，别事后写一句「模型更强所以更难监督」。必要时限制 hidden reasoning，强制把关键决策写进可检查的字段，或者把高风险工具从「想完再调」改成「先申报再执行」。

这和 `pt-reasoning-token-cost-frontier` 的出发点不同。那边惩罚无效 thinking 是为了省 token；这边即使 CoT 变短、变「干净」，只要监控器更难发现风险，也算失败。和 `pt-safety-capability-regression` 一起看：安全分没掉、monitorability 掉了，照样算发布失败，因为出了事故没法事后审计。

## 追问

**准确率涨了，还要卡 monitorability 吗？**
要。能力提升如果来自更不透明的搜索，生产事故会更难追责。安全回归（`pt-safety-capability-regression`）过了、$\Delta_{\mathrm{mon}}$ 掉了，照样停发。

**看 CoT 的监控器会不会自己被骗？**
会。所以要有对抗集和独立标签，并且让监控器只信能核验的片段，比如工具参数、代码、引用，全文的修辞不算数。监控器也要冻结版本，免得和 policy 一起漂。

**和 faithfulness 是一回事吗？**
相关，问的东西不同。faithfulness 问 CoT 是否反映了真实的计算；monitorability 问监控器看了 CoT 能不能更好地抓风险。一条忠实但高度编码的 CoT，对弱监控器照样没用。

**预算不固定会怎样？**
模型把危险内容写进超长的 CoT，监控器读不完，看起来「有过程」，其实漏检了。所以要锁住 token、时间和人工复核预算，并测「只看前缀」时漏检会不会变多。
