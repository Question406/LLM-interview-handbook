---
id: align-llm-judge
section: alignment
order: 20
level: S
title: 对齐：LLM-as-judge 偏差（位置、自偏好）
quick: "模型裁判会偏好先出现的回答、较长的回答，以及自己家族的文风。我会交换两条回答的顺序、固定评分标准，再用不同家族的裁判和人工抽查做校准；训练奖励模型和最终验收也要分开。"
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

LLM-as-judge 可以用来筛选和回归测试，但要先控制位置、长度和自偏好，否则训练会把裁判的偏见一起学进去。比如两条回答内容没变，只把 A、B 对调，胜负就变了，这个标签就不适合直接拿去训练。MT-Bench 说明 GPT-4 的判断能接近人类；同期的 Large Language Models are not Fair Evaluators 则展示了位置偏差，两件事可以同时成立。

## 裁判会偏在哪里

成对比较时，很多裁判更容易选放在前面的 A，先看或后看也可能影响判断。我会让每对回答正反各判一次，两次不一致就记平局或丢弃。只随机一次顺序只能分散偏差，不能证明这对回答的标签可靠。即使让裁判给单条回答打 1 到 10 分，也可能有阅读顺序的影响。

裁判也会偏好自己家族的文风。例如 GPT-4 更喜欢 GPT-4 家族的排版、客套和安全套话，拿它给 Llama 的训练结果打分，可能把 Llama 的文风推向 GPT。用模型自己给自己做 RLAIF，又可能强化原有偏见。所以训练和验收的 judge 要换家族，至少也要换 checkpoint。

长回答、列表和「根据研究」这样的空引用也更容易赢，这和奖励模型（RM）的长度偏好类似。引用是否真的支持结论，需要另查证据。系统提示还会影响裁判对英语、自信语气以及拒答程度的偏好。

这些偏差会叠加：同家族的长回答放在 A 位，优势可能更明显。因此报告 GPT-4 win-rate 时，还要说明比较协议和回答长度的变化。

## 怎么组织评测

我会先把正确、完整、安全、简洁拆成独立评分项，再按固定权重合并，避免「谁更好」被长度主导。事实题把金标和证据放进提示；没有金标时，裁判也不能自行补出标准答案。工具题还要冻结模拟器版本。

然后对调回答顺序，两次一致才给胜负，不一致就记平或重判。这样成本会翻倍，但可以减少错误金标。训练反馈、选择 checkpoint、对外报告分别用三套裁判，至少也要用三套提示，并用 canary 题检查裁判污染。

上线后定期拿人工标注子集算同意率、位置对称性和长度偏回归系数。发现漂移就冻结版本，排查原因；每次更换底层模型都要记录。

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

报告要固定并记录 `judge@sha`、提示和解码配置，因为温度、最大 token 数、是否允许思维链（CoT，即分步推理过程）都会改分。不同模型的点式绝对分也不能直接比较。

单条打分便宜但校准较差，适合粗筛；成对比较更稳，也更贵，我会用成对比较加人工抽查做最终门禁。Best-of-N 把裁判当 RM 来挑答案时，还会放大过优化和位置偏差。

人工抽查按安全、法律、医疗和工具写操作等风险分层，也要抽查平局。如果裁判和人对不齐，我会先检查评分指南和位置协议，再判断是否要改被测模型。Constitutional / RLAIF 的价值评估模型（critic）也要遵守这套隔离。

相关：`align-arena`、`align-length-bias`、`align-rlaif`、`align-reward-hack`、`design-prod-rag`、`design-eval-platform`、`align-eval-contam`、`align-best-of-n`、`align-cai`。

## 追问

**换更强裁判能消自偏好吗？**
能减弱能力误判，消不掉文风和位置。协议还要做。
**一条回答自己打 1-10 行吗？**
粗筛可以。发版和 强化学习（RL） 奖励不要只靠它，尺度漂、长度偏。
**裁判 CoT 要不要给被测模型看？**
不要。泄漏会变成新的作弊方式：模仿裁判推理腔。
**和 Arena 人点有何不同？**
人都有长度偏，但不是同一家族自偏好。人贵、慢、可当校准；裁判便宜、必须防协议作弊。

## 相关题

- [[align-length-bias]]：单独展开长度偏见，从人标、RM 到 DPO 损失，长度差是怎么进到每一环的。
- [[align-arena]]：人投票的在线榜，和模型裁判对照着看：人没有家族自偏好，但同样偏长、偏文风。
- [[xai-lmarena]]：xAI 版的 Arena 题，侧重 BT 全局 MLE 和在线、离线榜的差别。
- [[anthropic-pref-collect]]：人工对比里的双盲和随机左右，和裁判协议里的交换顺序是同一个思路。
- [[align-cai]]：RLAIF 用模型给训练反馈，裁判的偏差会直接写进奖励。
