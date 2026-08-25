---
id: pt-self-rewarding-idpo
section: posttrain
order: 35
level: S
title: 让同一个 LLM 当 Judge、产生偏好并做 Iterative DPO，如何避免自证循环？
quick: 不能把“自己给高分”当真值。隔离 judge 与 policy 版本，做位置交换和长度偏差校准，周期性接入人工或外部 judge，并始终用未参与偏好生成的独立评测集做 regression gate。
tags:
  - Self-Rewarding
  - DPO
  - Judge
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Self-Rewarding Language Models
    url: https://arxiv.org/abs/2401.10020
    type: primary
---

Self-rewarding / Iterative DPO 用同一模型家族当 judge，给自己的候选打偏好，再做 DPO（或同类目标）更新 policy，从而扩大标注供给。Self-Rewarding Language Models 展示了这条回路可行，但没有自动保证 judge 是真值。这块容易直接答成把「本轮 self-judge win rate 上涨」当成对齐成功。judge、数据生成器和被训 policy 若同步更新，模型会强化自己的措辞、长度和立场，形成自证循环。这和 `pt-online-preference-loop` 的在线偏好闭环同类，只是反馈源更不安全。

## 先隔离版本，再量偏差

每轮至少 pin 住 judge 版本：用上一轮冻结的模型（或独立 judge）标本轮候选，而不是用正在更新的 $\pi_\theta$。候选顺序必须随机交换，并测量：

- **position bias**：同一 pair 对调先后，胜者是否跟着位置走。
- **verbosity bias**：更长答案是否系统胜出。
- **self-preference**：judge 是否偏爱自己风格的回复。

DPO 的 $\beta$（见 `pt-dpo-beta`）管的是相对参考策略的偏移，管不住 judge 本身的系统误差。位置 / 长度校准做不好，迭代只会把偏差写进数据。

对 judge 不确定或分歧大的 pair，不要强制硬标签：丢弃、降权，或送去外部 verifier。高影响样本（安全、医疗、法律、工具副作用）必须有人工锚点或多个独立 judge。位置交换的协议要写进训练：每个 pair 正反各判一次，不一致则丢弃。只在推理时「注意位置」而训练数据没洗过，偏差会进 DPO。

## 记录从哪一轮进入偏差

每轮保留 prompt、候选、rubric、judge rationale 和版本号。没有这条链，下一轮 win rate 涨了也无法回答「是质量好了还是 judge 更自恋了」。Rubric 要写可观察标准，避免「更有帮助」这种会被长度和客套话劫持的词。把 rationale 留下来还能做二次审计：judge 是否引用了未出现的事实、是否先选边再编理由。

实现上可把生成、打分、训练拆成三个 job，禁止训练中的 policy 立刻回头当本 batch 的 judge。这和 `pt-dpo-derive` 的公式正确性无关，是数据闭环的工程约束。迭代轮数也不要当超参盲加：每轮先看外部门，过了再生成下一轮偏好。

白板例子：第 2 轮起回复平均长度明显上升，本轮 judge win rate 同步上升，外部短答案金标下降。这是 verbosity 自证，不是能力。修复是长度校准、rubric 禁止「更详细更好」，以及用冻结的外部 judge 重打本轮数据。

## 评估禁止再用同一个 self-judge

Regression gate 必须是未参与偏好生成的集合：外部质量集、对抗集、跨风格 / 跨模型 judge。一旦 win rate 只在本轮 judge 上涨、外部持平或下降，停止迭代并重校准 judge，而不是再跑一轮 DPO。还要盯安全与过度拒答：self-judge 很容易把「更像自己」标成更好，把不熟悉的正确风格标成更差。跨模型 judge 不一致时，优先信更强或与训练无关的那个，并抽样给人。

若必须继续迭代，交替插入外部金标或可执行奖励，把 self-judge 限制在低风险、易验证的子集上。能走 `pt-r1zero` 可执行奖励的任务，不要降级成自我打分。Self-rewarding 的正当用途是扩大「尚无金标、但有清晰 rubric」的偏好供给，不是替代真值。

每轮放行条件写成三道门：位置 / 长度偏差在阈值内、外部集不降、高风险 pair 有锚点。少一门就停迭代。

## 追问

- **Judge 和 policy 能不能同权重？** 同权重几乎必然自偏好。至少滞后一个版本，更好是独立模型。同权重还让你无法回答「偏差从哪一轮进来」，因为生成器和打分器同时在变。
- **长度偏差校准一次就够吗？** 不够。每轮政策变长 / 变短后，verbosity 会重新出现，要当回归项反复测。Rubric 里写死「同等正确时不因更长而胜」比事后调长度惩罚更干净。
- **和 RLVR 比哪个更怕自证？** Self-judge 没有外部环境当真值，更怕。有可执行 verifier 的任务应优先走 `pt-r1zero` 路线，而不是让模型给自己打分。Self-rewarding 只适合尚无金标、但 rubric 可观察的偏好供给。
- **不确定的 pair 怎么办？** 不进 DPO。硬标签会把噪声放大成下一轮的「偏好真理」。分歧大就丢弃、降权或送外部，宁可本轮数据少，不要把 judge 方差写成偏好。
