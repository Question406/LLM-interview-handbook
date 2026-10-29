---
id: pt-self-rewarding-idpo
section: posttrain
order: 35
level: S
title: 让同一个 LLM 当 Judge、产生偏好并做 Iterative DPO，如何避免自证循环？
quick: >-
  自己给的高分不能当真值。judge 至少滞后 policy 一个版本，每个 pair 正反各判一次，量位置和 length bias，定期接入人工或外部
  judge；每轮放行前，用没参与偏好生成的独立评测集做 regression gate。
tags:
  - Self-Rewarding
  - DPO
  - Judge
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Self-Rewarding Language Models
    url: 'https://arxiv.org/abs/2401.10020'
    type: primary
---

我会从三处防自证循环：judge 和 policy 的版本隔开，每轮量位置、长度和自偏好这几种偏差，放行只看没参与偏好生成的外部评测。本轮 self-judge 的 win rate 涨了，说明不了对齐成功。

Self-rewarding / Iterative DPO 的做法，是用同一模型家族当 judge，给自己的候选打偏好，再用 DPO（或同类目标）更新 policy，这样标注供给就大了。Self-Rewarding Language Models 证明了这条回路能跑，但不保证 judge 是真值。judge、数据生成器和被训的 policy 同步更新时，模型会一轮轮强化自己的措辞、长度和立场。比如从第 2 轮起，回复平均长度明显变长，本轮 judge win rate 跟着涨，外部的短答案金标却在下降，这就是 verbosity 自证，和能力无关。它和 `pt-online-preference-loop` 的 online preference feedback loop 是同一类，只是反馈源更不可靠。

所以第一步是隔离版本。每轮至少把 judge pin 住，用上一轮冻结的模型（或独立 judge）给本轮候选打分，别用正在更新的 $\pi_\theta$。工程上可以把生成、打分、训练拆成三个 job，禁止训练中的 policy 立刻回头当本 batch 的 judge。这条约束和 `pt-dpo-derive` 里公式对不对无关，是 data feedback loop 的工程约束。

接着量偏差。position bias 看同一个 pair 对调先后，胜者是不是跟着位置走；verbosity bias 看长答案是不是系统性地胜出；self-preference 看 judge 是不是偏爱自己风格的回复。位置交换要写进训练协议：每个 pair 正反各判一次，不一致就丢掉，光在推理时「注意位置」、训练数据没洗过，偏差照样进 DPO。DPO 的 $\beta$（见 `pt-dpo-beta`）管的是相对 reference policy 偏多远，管不了 judge 自己的系统误差，calibration 没做好，迭代只会把偏差写进数据。judge 拿不准或分歧大的 pair，别强行给 hard labels，丢掉、降权或送外部验证器（verifier）都行。安全、医疗、法律、工具副作用这类高影响样本，必须有 human-verified reference examples 或多个独立 judge。

然后每轮留好记录：prompt、候选、rubric、judge rationale 和版本号。没有这条链，下一轮 win rate 涨了，你答不上来是回答变好了，还是评委更偏爱自己的风格了。rubric 写可观察的标准，「更有帮助」这种词很容易被长度和客套话劫持。留下 rationale 还能做二次审计，看 judge 有没有引用不存在的事实、是不是先选边再编理由。

最后是评估。regression gate 用没参与偏好生成的集合：外部质量集、对抗集、跨风格或跨模型的 judge。win rate 只在本轮 judge 上涨、外部持平或下降，就停下来重 calibration judge，别再跑一轮 DPO。安全和 over-refusal 也要盯，self-judge 很容易把「更像自己」标成更好，把不熟悉但正确的风格标成更差。跨模型 judge 意见不一致时，优先信更强、或者和训练无关的那个，再抽样给人看。迭代轮数也别当超参往上加，每轮先过外部评测，再生成下一轮偏好。前面那个变长的例子，修法就是做长度 calibration、rubric 里禁止「更详细更好」，再用冻结的外部 judge 把本轮数据重打一遍。

如果必须继续迭代，就穿插外部金标或可执行奖励，把 self-judge 限制在低风险、易验证的子集。能走 `pt-r1zero` 可执行奖励的任务，别降级成自我打分。self-rewarding 适合的场景，是还没有金标、但 rubric 写得清楚的偏好供给，它替代不了真值。每轮放行我会看三条：位置和 length bias 在阈值内、外部集不降、高风险 pair 有 reference policy，少一条就停。

## 追问

**judge 和 policy 能不能用同一套权重？**
同权重几乎必然自偏好，至少滞后一个版本，最好是独立模型。同权重还让你说不清偏差是哪一轮进来的，因为生成器和打分器同时在变。

**length bias calibration 一次就够了吗？**
不够。policy 每轮变长或变短，verbosity 都会重新冒出来，要当回归项反复测。在 rubric 里写死「同等正确时，不因更长而胜」，比事后调长度惩罚干净。

**和 RLVR 比，哪个更怕自证？**
self-judge 更怕，它没有外部环境当真值。有可执行 verifier 的任务应该优先走 `pt-r1zero` 那条路。

**拿不准的 pair 怎么处理？**
不进 DPO。hard labels 会把噪声放大成下一轮的「偏好真理」，分歧大就丢弃、降权或送外部，宁可本轮数据少一点，也别把 judge 的方差写成偏好。
