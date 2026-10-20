---
id: pt-grounded-rlvr-reward-staging
section: posttrain
order: 37
level: S
title: RAG / Grounded QA 的 RLVR 如何同时奖励答案正确、引用充分、证据一致和恰当拒答？为什么适合分阶段训练？
quick: 不要把所有子目标粗暴相加。分别验证检索是否覆盖必要证据、引用是否支持声明、答案是否正确，以及是否应当拒答，先建立可靠引用/拒答行为，再优化端到端答案；否则模型容易用伪引用或过度拒答刷总分。
tags:
  - Grounded QA
  - RLVR
  - RAG
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Lessons from Training Grounded LLMs with Verifiable Rewards
    url: https://arxiv.org/abs/2506.15522
    type: primary
---

有证据支撑的问答（Grounded QA）/ 检索增强生成（RAG）中的可验证奖励强化学习（RLVR） 要同时满足：检索证据覆盖关键事实、引用蕴含声明、最终答案正确、证据不足时拒答或标不确定。这些目标互相冲突，不能当成一个标量随便加。常见误区是：写成 $r = r_{\mathrm{ans}} + r_{\mathrm{cite}} + r_{\mathrm{refuse}}$ 直接相加：模型会堆假引用刷 citation 分、或遇难就拒答刷安全分，答案质量反而坏。`pt-reward-design` 讲奖励可验证；`pt-reward-ood-failure` 讲代理奖励在超出训练数据覆盖范围后失效。本题把这两点落到 grounded 场景的分阶段训练。

## 四层信号必须分开定义

先为每一层设计独立的正确性判定和负例，而不是「看起来引用了网页」：

| 层 | 可验证问题 | 典型负例 |
| --- | --- | --- |
| retrieval coverage | 关键事实是否出现在检索集 | 漏掉唯一支撑句 |
| citation entailment | 被引片段是否蕴含该句 | 伪引用、张冠李戴 |
| answer correctness | 答案相对金标 / 执行结果是否对 | 引用对、结论错 |
| abstention | 证据不足时是否拒答 | 该答却拒、不该拒却答 |

只奖 citation count 会堆无关链接；只奖拒答会让系统保守到不可用；只奖答案会鼓励无依据编造。冲突是结构性的，不是调 $\lambda$ 能一次性消掉的。Entailment 应用 NLI / 规则 / 执行，而不是「模型自己觉得引用相关」。检索 coverage 也要用题面关键事实列表对齐，避免「检索了很多、但唯一支撑句不在」。

## 为什么要 staged，而不是加权求和

早期策略还不会把引用与声明对应起来时，端到端答案奖励会主导梯度，citation 变成装饰。反过来，先猛训拒答，后面很难把可答问题救回来。更稳的顺序：

1. 引用绑定与 answerability：会不会引用、会不会判断「当前证据够不够答」。
2. 在引用约束下优化答案正确。
3. 再微调拒答阈值，用独立的 false refusal / missed refusal 集。

每个阶段保留前一能力的 regression test。约束优化（先满足 citation / 拒答，再最大化答案）比线性加权更不容易被单一项劫持。阶段之间不要换掉 oracle 定义，否则回归曲线不可比。若必须合成标量，也要用门槛：citation / entailment 未过则答案项为零，防止「答对但不引用」成为最优。

白板反例：加权求和后，模型给每句都挂上三个片段号，precision 崩、答案碰巧还对，总分上涨。或模型学会「不确定就拒」，可答集上正确率下降但拒答分把总奖励 托住。分阶段时这两种都应在对应回归检查中判为失败，而不是被总分稀释。

## 评测不能只报总分

必须同时报：answer correctness、citation precision / recall、unsupported-claim rate、false refusal、retrieval miss。任一安全失败被总分掩盖都不算过。切片看：证据充足的题、证据冲突的题、检索全空的题。全空集上仍「自信作答且引用幻觉」，是 grounded RLVR 的红灯。冲突集上应引用双方证据，避免强行给出单一结论，而不是挑一句好引用硬答。

还要防评测与训练共用同一检索器漏洞：训练时能检索到的金标句，线上换库就没了。换 retrieval 后端、换语料版本做一次破坏性测试。奖励出支撑后的表现，按 `pt-reward-ood-failure` 的 proxy-gold 相关来盯。Grounded QA 的分布外评测（OOD） 不只是新题，还包括新语料库、新引用格式和更长的多跳证据链。

阶段门可以写成：先过 citation / answerability 回归，再开答案奖励；答案阶段用「引用未过则答案项为零」的门槛，最后单独调拒答，四张切片表一起看。

## 追问

- **为什么加权求和常失败？** 模型会找最容易涨的项（多引用或乱拒答），梯度不保证四层同时变好。冲突是结构性的，调 $\lambda$ 只是换一种劫持方式。
- **拒答应放在第几阶段？** 先有可靠的 answerability 判断，再调阈值；一上来奖拒答，会学成「不会就拒」。false refusal 与 missed refusal 必须分集，不能合成一个「谨慎分」。
- **citation 用计数可以吗？** 只能当辅助。必须有 entailment，否则伪引用是最优策略。计数还会激励堆无关链接，precision 先崩。
- **和普通数学 RLVR 差在哪？** 数学常有单一可执行终局；grounded QA 有「对但无依据」和「有依据但拒答」两种不可接受的成功，必须分阶段和分指标。检索后端一换就 OOD，还要按 `pt-reward-ood-failure` 盯 proxy-gold。
