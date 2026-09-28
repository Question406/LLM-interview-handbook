---
id: pt-prover-verifier-legibility
section: posttrain
order: 36
level: S
title: 强 Prover 怎样在不牺牲正确性的前提下，生成弱 Verifier 也能检查的推理？
quick: 把“正确”与“可检查、可说服”分开优化。先用可信 correctness gate 排除错解，再训练 prover 产生 verifier 能检查的证据；不能直接以说服弱 judge 的分数为 reward，否则会激励伪装而非真正确。
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

Prover-verifier 设定里，prover 更强，负责出解答；verifier 更弱，负责检查。Legibility 指证明 / 推理弱检查器也读得懂、核得了：步骤局部可验证、引用充分、不依赖「相信我」。OpenAI 的 prover-verifier games 把「让弱模型也能查」当成目标。这块容易单看最终答案（丢掉过程），或单让 prover 最大化「verifier 相信的概率」。后者会训出 sneaky proof：错的但对弱 judge 很香。正确性与可说服性必须拆开。`pt-cot-monitorability-regression` 问监控器还能不能抓风险；本题问证据能不能写给比自己弱的检查者。

## 先正确，再在正确集合里优化可读

安全顺序：用可信 correctness gate（可执行检查、更强独立 oracle、人工）丢掉错解，再在正确集合内优化简洁、引用、步骤可检查等指标。把顺序反过来，reward

$$
r = \mathbf{1}[\mathrm{verifier\ accepts}]
$$

会激励伪装。弱 verifier 的接受率不是正确性的代理，尤其当 prover 知道 verifier 的能力边界时。

Verifier 要写清边界：查哪些局部事实、能否调用工具 / 计算器、是否看完整过程、一次看多少 token。边界不清，prover 会把关键跳跃藏在 verifier 读不到的段落。训练时可让 prover 面对多个 verifier（不同强度、不同规则），避免只适配一个 judge 的用词习惯。步长也要受约束：每一步应小到弱 verifier 能局部核对，而不是「由引理 3 显然得证」。

## 合作与对抗都要有

合作：prover 为诚实 verifier 写清楚的证明，降低误拒。对抗：另一些 verifier 专门抓伪装、抓引用幻觉。只有合作，模型会写得又长又客套；只有对抗，又可能变得过度隐晦。评估要把两类 verifier 分开报，防止「把对抗 verifier 也说服了」被写成成功。那往往是 sneaky 成功。

过程奖励若来自同一个弱 verifier，会和训练目标共谋。更稳的是：正确性走独立 gate，legibility 走「弱 verifier 能否复现关键步骤」，而不是「弱 verifier 主观喜欢」。OpenAI 的 prover-verifier games 强调的正是：把「让弱者能查」当成目标，而不是「让弱者点赞」。

白板反例：prover 写出格式完整、引用编号齐全的证明，弱 verifier 接受，独立计算发现关键等式不成立，引用指向的是不相干行。这是伪装，不是 legibility。正确训练应在 correctness gate 就丢掉它，它不该获得任何「写得清楚」的加分。

## 评估四件事一起看

必须同时报：correctness、verifier acceptance、人工可审计性、adversarial persuasion gap（错解被弱 verifier 接受的比例）。Acceptance 升而 correctness 降，说明 reward 已被说服技巧劫持，应立刻停。人工抽检应尝试「只根据写出的证据、不靠对 prover 的信任」能否复现结论。还要报「局部可检查步的比例」：通篇只有一头一尾能核，中间是叙事，不算可读。

这和 `pt-prm-orm-critic` 的关系：PRM / ORM 是打分器；legibility 要求分数来自可检查证据，而不是来自文风。和 `pt-cot-monitorability-regression` 一起：即使 CoT 对监控器有用，若用户或弱审核员读不懂，产品仍不可审计。生产上，弱 verifier 可以是用户、审核员或小模型，因此可读性是安全接口，不是文案需求。放行时一起看：正确性不降、弱 verifier 对正确解的接受升、人工可复现升、错解被说服的 gap 不升；后一项单独红就停。

## 追问

- **为什么不能把说服弱 judge 当唯一 reward？** 弱 judge 可被修辞、长度、选择性引用欺骗，优化它等于优化伪装。必须先过独立 correctness gate，legibility 只在正确集合里优化。
- **正确性 gate 可以是同一个 verifier 吗？** 尽量不要。gate 应更强或可执行；弱 verifier 只负责「人能不能查」。同一弱模型既当真值又当读者，会回到 self-judge 循环。
- **和 monitorability 冲突吗？** 不冲突。legibility 让证据好查；monitorability（`pt-cot-monitorability-regression`）测查了是否更能抓坏行为。两者都可能被 unfaithful 文本骗，都要对抗集。
- **prover 很强、verifier 很弱时怎么办？** 缩小单步跨度、强制引用可执行检查、限制 verifier 一次只看局部，而不是指望弱模型读懂天书长证明。步长过大是伪装最常见的藏身处。
