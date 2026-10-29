---
id: pt-grounded-rlvr-reward-staging
section: posttrain
order: 37
level: S
title: RAG / Grounded QA 的 RLVR 如何同时奖励答案正确、引用充分、证据一致和恰当拒答？为什么适合分阶段训练？
quick: >-
  四个子目标别直接相加：分别验证检索是否覆盖必要证据、引用是否支持声明、答案是否正确、该不该拒答。先训出可靠的引用和拒答判断，再在引用约束下优化答案，最后单独调拒答阈值；直接加权求和，模型会用伪引用或
  over-refusal 刷总分。
tags:
  - Grounded QA
  - RLVR
  - RAG
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Lessons from Training Grounded LLMs with Verifiable Rewards
    url: 'https://arxiv.org/abs/2506.15522'
    type: primary
---

## 可以这样回答

我会把四个目标分开验证、分阶段训：先教会模型引用和判断「证据够不够答」，再在引用约束下优化答案正确，最后单独调拒答阈值。把它们写成 $r = r_{\mathrm{ans}} + r_{\mathrm{cite}} + r_{\mathrm{refuse}}$ 直接相加，模型会挑最容易涨的那项去刷，比如堆假引用刷 citation 分，或者遇到难题就拒答刷安全分，答案质量跟着变差。

只奖 citation count，模型会堆无关链接；只奖拒答，系统会保守到没法用；只奖答案，会鼓励没依据的编造。这种冲突是结构性的，调一次 $\lambda$ 消不掉。entailment 要用 NLI、规则或执行来判，模型自己觉得引用相关不算。检索 coverage 也要拿题面的关键事实列表去对，免得出现「检索了很多，唯一的支撑句却不在里面」。

## 技术备查

我会把四个目标分开验证、分阶段训：先教会模型引用和判断「证据够不够答」，再在引用约束下优化答案正确，最后单独调拒答阈值。把它们写成 $r = r_{\mathrm{ans}} + r_{\mathrm{cite}} + r_{\mathrm{refuse}}$ 直接相加，模型会挑最容易涨的那项去刷，比如堆假引用刷 citation 分，或者遇到难题就拒答刷安全分，答案质量跟着变差。

有证据支撑的问答（Grounded QA）/ 检索增强生成（RAG）中的可验证奖励 RL（RLVR） 要同时满足四件事：检索到的证据覆盖关键事实、引用能蕴含它支撑的那句话、最终答案正确、证据不够时拒答或者标出不确定。这几件事互相冲突。举个白板上的反例：加权求和以后，模型给每句话都挂上三个片段号，precision 崩了，答案碰巧还对，总分在涨；或者模型学会了「不确定就拒」，可答题上的正确率下降了，拒答分却把总奖励托住了。`pt-reward-design` 讲奖励怎么做到可验证，`pt-reward-ood-failure` 讲代理奖励出了训练覆盖范围就失效，这张卡把两点落到 grounded 场景的分阶段训练上。

## 四层信号分开定义

每一层都要有独立的正确性判定和负例，「看起来引用了网页」不算数：

| 层 | 可验证问题 | 典型负例 |
| --- | --- | --- |
| retrieval coverage | 关键事实是否出现在检索集 | 漏掉唯一支撑句 |
| citation entailment | 被引片段是否蕴含该句 | 伪引用、张冠李戴 |
| answer correctness | 答案相对金标 / 执行结果是否对 | 引用对、结论错 |
| abstention | 证据不足时是否拒答 | 该答却拒、不该拒却答 |

只奖 citation count，模型会堆无关链接；只奖拒答，系统会保守到没法用；只奖答案，会鼓励没依据的编造。这种冲突是结构性的，调一次 $\lambda$ 消不掉。entailment 要用 NLI、规则或执行来判，模型自己觉得引用相关不算。检索 coverage 也要拿题面的关键事实列表去对，免得出现「检索了很多，唯一的支撑句却不在里面」。

## 为什么要分阶段

早期策略还不会把引用和声明对上的时候，端到端的答案奖励会主导梯度，citation 就成了装饰。反过来，一上来猛训拒答，后面很难把可答的问题救回来。所以顺序是：先训引用绑定和 answerability，让模型会引用、会判断当前证据够不够答；再在引用约束下优化答案正确；最后用独立的 false refusal 和 missed refusal 集微调拒答阈值。

每个阶段都保留前一阶段能力的 regression test，前面那两种反例在对应的回归检查里就会被判失败，不会被总分稀释掉。约束优化（先满足 citation 和拒答，再最大化答案）比线性加权更不容易被某一项劫持。阶段之间别换 oracle 的定义，否则回归曲线没法比。实在要合成一个标量，也要加 threshold：citation / entailment 没过，答案项就记零，免得「答对但不引用」成了最优解。阶段门可以这样写：先过 citation 和 answerability 的回归，再开答案奖励；答案阶段用「引用没过、答案项为零」的 threshold；最后单独调拒答，四张切片表一起看。

评测时 answer correctness、citation precision / recall、unsupported-claim rate、false refusal、retrieval miss 要同时报，任何一项安全失败被总分盖住都不算过。再按切片看：证据充足的题、证据冲突的题、检索全空的题。检索全空的集合上模型还在自信作答、引用还是 hallucination 出来的，就是 grounded RLVR 的红灯。证据冲突的集合上，模型应该把双方的证据都引出来，别挑一句好引用硬给一个结论。

还要防训练和评测共用同一个检索器的漏洞：训练时能检索到的金标句，线上换了库可能就没了。换 retrieval 后端、换语料版本，做一次破坏性测试。奖励超出支撑范围以后的表现，按 `pt-reward-ood-failure` 里的 proxy-gold 相关性去盯。Grounded QA 的 out-of-distribution 评测（OOD） 除了新题，还包括新语料库、新的引用格式和更长的多跳证据链。

## 追问

**为什么加权求和常常失败？**
模型会找最容易涨的那项（多挂引用或者乱拒答），梯度保证不了四层一起变好。冲突是结构性的，调 $\lambda$ 只是换一种被劫持的方式。

**拒答放在第几阶段？**
先有可靠的 answerability 判断，再调阈值。一上来就奖励拒答，模型会学成「不会就拒」。false refusal 和 missed refusal 要分开建集，别合成一个「谨慎分」。

**citation 用计数可以吗？**
只能当辅助，必须有 entailment，否则伪引用就是最优策略。计数还会激励堆无关链接，precision 最先崩。

**和普通数学 RLVR 差在哪？**
数学题通常有单一的、可执行的终局；grounded QA 有两种不可接受的「成功」：答对了但没有依据，有依据却拒答了。所以要分阶段、分指标。检索后端一换就是 OOD，还要按 `pt-reward-ood-failure` 盯 proxy-gold。
