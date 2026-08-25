---
id: align-llm-judge
section: alignment
order: 20
level: S
title: 对齐：LLM-as-judge 偏差（位置、自偏好）
quick: >-
  用模型当裁判会稳定地偏位置、偏长度、偏自家文风。MT-Bench 证明它能接近人，不证明它无偏。交换顺序、换家族、
  钉 rubric，不能让训练 RM 和验收 judge 是同一套权重。
tags:
  - LMSYS
  - OpenAI
  - LLM-as-judge
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
    url: https://arxiv.org/abs/2306.05685
    type: primary
  - title: Large Language Models are not Fair Evaluators
    url: https://arxiv.org/abs/2305.17926
    type: primary
  - title: Chatbot Arena — An Open Platform for Evaluating LLMs by Human Preference
    url: https://arxiv.org/abs/2403.04132
    type: primary
---

LMSYS 的 MT-Bench 把 GPT-4 当裁判，和人对得上，于是全行业开始用 LLM-as-judge。同一时期「not Fair Evaluators」把位置偏差画出来：先出现的回答更容易赢。对齐 / 评测岗问这题，不是「能不能用 GPT-4 打分」，是你会不会把裁判偏差训进策略。人偏好活榜见 `align-arena`；长度见 `align-length-bias`；RLAIF 隔离见 `align-rlaif`。

## 三类面试要能点名的偏差

**位置。** Pairwise 提示里 A 在前、B 在后，很多裁判给 A 更高。不是随机噪声，是位置头 + 近因/首因。缓解：每个 pair 正反各判一次，不一致当平局或丢弃；不要只随机一次顺序就当真金。点式打分（1 到 10）同样有「先看谁」效应，只是藏在绝对分里。

**自偏好。** GPT-4 更爱 GPT-4 家族的排版、客套、安全套话。用 Llama 训、用 GPT 验收，会把文风往裁判家族推。反过来用自己当裁判做 RLAIF，就是自己给自己刷分。训练 judge 和验收 judge 必须换家族或至少换 checkpoint，见 `align-reward-hack`。

**长度与权威感。** 更长、有列表、有「根据研究」这类空引用更容易赢，和 RM 同一条缝。有引用不等于接地，见 `design-prod-rag`。裁判还会偏英语、偏自信语气、偏不拒答或偏过度拒答，取决于系统提示怎么写。

这三类可以叠：长的自己人写的回答放在 A 位，几乎锁定。所以「GPT-4 win-rate 涨了」单独报没有信息。

## 协议：交换、rubric、隔离

我会把裁判当有噪声的标注员，不当 oracle：

- **交换顺序。** 胜负取两次一致；不一致记平或重判。成本翻倍，比错的金标便宜。
- **Rubric。** 正确、完整、安全、简洁分开打，再加权。一条「谁更好」会塌缩到长度。参考答案能写就写，减少开放偏好。
- **参考与证据。** 事实题把金标塞进裁判提示；无金标就别让裁判编。工具题冻模拟器版本，见 `design-eval-platform`。
- **隔离。** 训练信号、选 checkpoint、对外数字三套裁判或至少三套提示。Canary 题看裁判自己有没有被污染，见 `align-eval-contam`。
- **校准。** 定期拿人标子集算同意率、位置对称性、长度偏回归系数。漂移了就冻版本，不要默默换底层模型。

```python
def pairwise_judge(model, x, a, b):
    w1 = model.vote(x, first=a, second=b)
    w2 = model.vote(x, first=b, second=a)
    if w1 == "A" and w2 == "B":
        return "A"
    if w1 == "B" and w2 == "A":
        return "B"
    return "tie"
```

点式分不要跨模型比绝对值。温度、max token、是否允许 CoT 都会改分。报告必须钉 `judge@sha` + 提示 + 解码。

点式还是成对：成对更稳、更贵；点式便宜但校准差，适合粗筛。最终门禁用成对 + 人抽查。BoN 用裁判当 RM，过优化和位置偏差一起爆，见 `align-best-of-n`。

## 面试怎么收

LLM-as-judge 是筛子和回归探针，不是发版金标。人抽查按风险分层：安全、法律、医疗、工具写操作。发现和人对不齐，先改指南和位置协议，再改被测模型。Constitutional / RLAIF 的 critic 遵守同一套隔离，见 `align-rlaif`、`align-cai`。

白板画：两个回答、左右对调两发、不一致进平局桶、人抽查平局和安全切片。评委要听的是你不把单一裁判当真理。

## 追问

- **换更强裁判能消自偏好吗？** 能减弱能力误判，消不掉文风和位置。协议还要做。
- **一条回答自己打 1–10 行吗？** 粗筛可以。发版和 RL 奖励不要只靠它，尺度漂、长度偏。
- **裁判 CoT 要不要给被测模型看？** 不要。泄漏会变成新的黑客面：模仿裁判推理腔。
- **和 Arena 人点有何不同？** 人都有长度偏，但不是同一家族自偏好。人贵、慢、可当校准；裁判便宜、必须防协议作弊。
