---
id: pt-prover-verifier-legibility
section: posttrain
order: 36
level: S
title: 强 Prover 怎样在不牺牲正确性的前提下，生成弱 Verifier 也能检查的推理？
quick: "把「正确」和「弱检查者能查」分开优化：先用可信的 correctness gate 丢掉错解，再在正确解里训练 prover 写出弱 verifier 能逐步核对的证据。直接拿「说服弱 judge」的分数当奖励，会训出看起来对、实际错的 sneaky proof。"
tags:
  - Verifier
  - Legibility
  - Alignment
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: OpenAI — Prover-Verifier Games Improve Legibility
    url: https://openai.com/index/prover-verifier-games-improve-legibility/
    type: primary
---

做法是先保正确，再在正确的解里优化可读：用可信的 correctness gate 把错解丢掉，剩下的解里再奖励弱 verifier 能逐步核对的写法。顺序反过来，直接让 prover 最大化「verifier 接受的概率」，会训出伪装。

先说设定。prover 更强，负责出解答；验证器（verifier）更弱，负责检查。Legibility 指推理写到弱检查者也读得懂、核得了：每一步局部可验证，引用充分，不靠「相信我」。OpenAI 的 prover-verifier games 就把「让弱模型也能查」当成训练目标。

顺序为什么不能反，看一个例子。prover 写出一份格式完整、引用编号齐全的证明，弱 verifier 接受了，独立计算一核，关键等式不成立，引用指向的是不相干的行。这就是 sneaky proof：内容是错的，弱 judge 却很容易接受。如果奖励写成

$$
r = \mathbf{1}[\mathrm{verifier\ accepts}]
$$

优化的就是这种伪装。弱 verifier 的接受率代理不了正确性，prover 知道 verifier 的能力边界时尤其如此。这份证明应该在 correctness gate 就被丢掉，拿不到任何「写得清楚」的加分。gate 用可执行检查、更强的独立 oracle 或人工，过了 gate，再在正确集合里优化简洁、引用和步骤可检查这些指标。

verifier 的边界要写清楚：查哪些局部事实、能不能调工具和计算器、看不看完整过程、一次读多少 token。边界不清，prover 会把关键跳跃藏在 verifier 读不到的段落。步长也要卡住，每一步小到弱 verifier 能局部核对，别出现「由引理 3 显然得证」。训练时让 prover 面对多个强度、规则不同的 verifier，免得只适配一个 judge 的用词习惯。

合作和对抗两种 verifier 都要有。合作的那类让 prover 给诚实 verifier 写清楚的证明，减少误拒；对抗的那类专门抓伪装和引用幻觉。只有合作，模型会写得又长又客套；只有对抗，又可能变得过度隐晦。评估时两类分开报，「连对抗 verifier 也说服了」往往是 sneaky 成功，别当成好消息写进报告。过程奖励如果也来自同一个弱 verifier，会和训练目标共享同样的误判。更稳的是正确性走独立 gate，legibility 看弱 verifier 能不能复现关键步骤，它主观上喜不喜欢不算数。OpenAI 那篇强调的也是让弱者能查，弱者点不点赞不重要。

评估时四件事一起报：correctness、verifier acceptance、人工可审计性，以及 adversarial persuasion gap，也就是错解被弱 verifier 接受的比例。acceptance 升、correctness 降，说明 reward 已经被说服技巧劫持，应该马上停。人工抽检时，要试着只根据写出来的证据、不靠对 prover 的信任去复现结论。再报一个「局部可检查步的比例」：通篇只有一头一尾能核、中间全是叙事，不算可读。放行条件是正确性不降、弱 verifier 对正确解的接受率升、人工可复现率升、错解被说服的 gap 不升，最后一项单独变红就停。

放到生产里，弱 verifier 可能是用户、审核员或小模型，所以可读性是一个安全接口，算不上文案需求。和 `pt-prm-orm-critic` 比，PRM / ORM 是打分器，legibility 要求分数来自可检查的证据，跟文风无关。`pt-cot-monitorability-regression` 问的是监控器还能不能抓风险，这题问证据能不能写给比自己弱的检查者；就算分步推理（CoT）对监控器有用，用户或弱审核员读不懂，产品仍然不可审计。

## 追问

**为什么不能把说服弱 judge 当唯一 reward？**
弱 judge 会被修辞、长度和选择性引用骗，优化它等于优化伪装。必须先过独立的 correctness gate，legibility 只在正确集合里优化。

**correctness gate 可以用同一个 verifier 吗？**
尽量不要。gate 应该更强或者可执行，弱 verifier 只负责「人能不能查」。同一个弱模型既当真值又当读者，就回到 self-judge 循环了。

**和 monitorability 冲突吗？**
不冲突。legibility 让证据好查，monitorability（`pt-cot-monitorability-regression`）测的是查了以后能不能更好地抓坏行为。两者都可能被 unfaithful 文本骗，都要有对抗集。

**prover 很强、verifier 很弱时怎么办？**
缩小单步跨度，强制引用可执行检查，限制 verifier 一次只看局部，别指望弱模型读懂跨度很大的长证明。步长过大是伪装最常藏身的地方。
