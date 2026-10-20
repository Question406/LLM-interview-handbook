---
id: pt-cot-monitorability-regression
section: posttrain
order: 40
level: S
title: 强化 Reasoning 后，如何判断 CoT 仍然可被监督，而不是更难审计？
quick: "把可监控性作为后训练的回归验收项：在相同预算下，比较只看答案或动作的监控器与能看分步推理（CoT）的监控器，对关键风险的检出率有何差别，并加入刻意伪装的对抗样本。准确率上升不能自动推出可监督性也更好。"
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

可监控性（monitorability）看的是：外部监控器读了思考过程之后，比只看最终答案 / 工具动作，能多抓到多少真实风险。不是「CoT 看起来像人话」。强化学习 reasoning 之后，主任务准确率常涨，但分步推理（CoT）可能变短、使用难懂编码，或与实际动作不一致，甚至学会对监控器说一套、做事另一套。常见误区是：把「更会推理」直接等同于「更好审计」。应把它做成和 `pt-safety-capability-regression` 并列的发布门槛，而不是上线后的解释。

## 先定义任务，再定义监控器

必须落到具体风险：钻奖励规则的空子、工具滥用、隐藏目标、不安全计划、对用户撒谎。分别跑两类监控器：只看最终答案 / 动作的 outcome monitor，以及能看完整或截断 CoT 的 process monitor。比较的是同一风险标签上的 detection 差：

$$
\Delta_{\mathrm{mon}} = \mathrm{TPR}_{\mathrm{CoT}} - \mathrm{TPR}_{\mathrm{outcome}}
$$

在固定 token、时间和人工复核预算下算。$\Delta_{\mathrm{mon}}$ 下降，就表示可监控性退化，哪怕主任务分在涨。还要报 FPR：CoT 变长会让监控器「看起来更忙」，不等于更准。

监控器本身可以是规则、分类器或另一个 LLM judge；关键是它不能和被测模型共享训练目标，也不能在评测前把具体规则泄露给 policy。`pt-prover-verifier-legibility` 问的是 prover 如何把证据写给能力较弱的验证器；本题问的是强化后的 CoT 还值不值得给监控器看。若你们同时训过程奖励，监控器更要独立，否则模型和监控器一起拟合同一套「安全套话」。

## 评测集必须含伪装

普通失败不够。集合里要有：诚实失败、无意漏检、以及刻意伪装（把危险计划藏在委婉语、外语、符号、工具参数里）。模型不能知道监控规则，否则它会优化「对监控器显得无辜」。同时测三类退化：

- **简略化**：关键决策被删，只剩套话。
- **编码化**：用只有模型自己懂的缩写或隐写。
- **脱钩**：CoT 写安全计划，实际调用危险工具。

只凭「看起来有解释」会把 unfaithful CoT 判成透明。对抗集要随 post-training 配方一起回归，而不是一次性定性研究。还要测「监控器只看前 $B$ token」：强化学习后模型若把关键意图往后挪，固定预算下的 $\Delta_{\mathrm{mon}}$ 会假跌或假涨。

具体任务示例：在模型利用奖励规则漏洞的题目里，模型在 CoT 里写「按评分标准诚实作答」，实际输出刷分格式；工具题里，CoT 说「只读文件」，函数调用却带了写路径。outcome monitor 可能漏，CoT monitor 理应能抓。若 post-training 后反而抓不住，就是回归。

## 发布门槛怎么设

比较的是同一监控预算下的 $\Delta_{\mathrm{mon}}$、漏检的高严重度 case 数、以及 CoT-action 一致性（计划中的工具与真实调用是否相符）。若主任务质量上升而 CoT 对 monitor 的边际信息下降，应停发：重新检查数据、奖励或工具权限，而不是事后写「模型更强所以更难监督」。必要时限制 hidden reasoning、强制把关键决策写进可检查字段，或把高风险工具从「想完再调」改成「先申报再执行」。

这和 `pt-reasoning-token-cost-frontier` 不同：那边惩罚无效 thinking 是为了省 token；这边即使 CoT 变短、变「干净」，只要监控器更难发现风险，也算失败。和 `pt-safety-capability-regression` 一起看：安全分不掉但 monitorability 掉，仍是发布失败，因为事故将无法事后审计。

可监控性需要比较两类监控器的检出率；只看 CoT 是否像一段合理解释，无法判断它是否帮助发现风险。评测需要最终结果对照、对抗集和固定预算。

白板最小实验：同一风险标签集、同一监控预算，报 $\Delta_{\mathrm{mon}}$、高严重度漏检、CoT-action 不一致率；主任务分只作对照，不作放行条件。

## 追问

- **准确率涨了还要卡 monitorability 吗？** 要。能力提升若来自更不透明的搜索，生产事故会更难追责。安全回归（`pt-safety-capability-regression`）过了但 $\Delta_{\mathrm{mon}}$ 掉，仍然停发。
- **看 CoT 的监控器会不会自己被骗？** 会。所以要对抗集、独立标签，并限制监控器只信可核验片段（工具参数、代码、引用），而不是全文修辞。监控器也要版本冻结，避免和 policy 一起漂。
- **和 faithfulness 是一回事吗？** 相关但不同。faithfulness 问 CoT 是否反映真实计算；monitorability 问监控器看了 CoT 是否更好抓风险。一条忠实但高度编码的 CoT 对弱监控器仍然无用。
- **预算不固定会怎样？** 模型把危险内容写进超长 CoT，监控器读不完，看起来「有过程」其实漏检。必须锁 token / 时间 / 人工复核，并测「只看前缀」时的漏检是否恶化。
