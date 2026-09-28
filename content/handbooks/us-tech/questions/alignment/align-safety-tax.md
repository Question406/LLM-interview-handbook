---
id: align-safety-tax
section: alignment
order: 17
level: A
title: 对齐：安全对齐掉能力，怎么测
quick: >-
  safety tax 是安全训练之后能力 / 有用性掉了多少，不是「拒答越多越安全」。要画安全 vs 能力的 Pareto：同解码、同提示，
  对齐前后比能力集、过度拒绝集、攻击集。只报 harmlessness 会把过度拒绝当进步。
tags:
  - Anthropic
  - OpenAI
  - Safety
  - Alignment Tax
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: XSTest — A Test Suite for Identifying Exaggerated Safety Behaviours
    url: https://arxiv.org/abs/2308.01263
    type: primary
  - title: Safety-Tuned LLaMAs — Lessons From Improving the Safety of Large Language Models
    url: https://arxiv.org/abs/2309.07875
    type: primary
---

OpenAI / Anthropic 对齐岗会问「安全训完 MMLU 掉了算不算成功」。InstructGPT 已经写过 RLHF 会改能力剖面；XSTest 专门打过度拒绝；Safety-Tuned LLaMAs 记录安全 SFT 伤有用性。过度拒绝专卡见 `align-over-refuse`；红队见 `align-red-team`。本题讲怎么测税。

## 税是 Pareto，不是一个数

安全对齐改的是策略支撑：抬无害峰、压有害峰，见 `align-rlhf-kl`。旁观损伤包括：拒答覆盖到 benign 双关、推理链被套话打断、代码/数学变短且错、多语言安全头硬、工具该调用时改道歉。这些叫 tax。拒答率本身不是 tax，也不是安全。

我会要三组数，对齐前后、同一解码：

1. **能力。** 内部私有集 + 公开集去污染后，见 `align-eval-contam`。含数学、代码、多步指令、长上下文。解码钉死：温度、max token、工具开关。
2. **过度拒绝。** XSTest 一类：看起来危险、实际无害（「kill 一个进程」、虚构犯罪小说）。按类别切片，不要一个拒答率。
3. **真实安全。** 红队 / jailbreak / 政策类有害遵从。攻击集要 held-out，不能和训练拒答模板重合。

画图：横轴能力（或 helpful 盲测），纵轴安全（攻击成功率越低越好）。报告的是曲线上的点，以及相对 SFT 基线移动了哪。只报安全升、不报能力，评委会当成刷拒答。

```python
def tax_report(before, after):
    # each dict: capability, over_refuse, attack_success  (same decode)
    cap = after["capability"] - before["capability"]
    over = after["over_refuse"] - before["over_refuse"]
    atk = after["attack_success"] - before["attack_success"]
    return {"d_capability": cap, "d_over_refuse": over, "d_attack": atk}
```

符号：能力掉、过度拒绝升、攻击成功率降，才是「买了安全、付了税」。攻击没降、能力掉，是训废了。攻击降、过度拒绝不升、能力持平，税接近零，那是目标。

## 测的时候容易骗自己

解码不一致：对齐后 max token 更长或更短，能力差是长度不是对齐。提示不一致：系统提示加了长宪法，基线没有，税算在提示上。污染：安全示范进了能力集，或能力题进了拒答训练。评测 judge 偏爱拒答套话，会把 tax 估低。

helpful 和 harmless 用同一个 RM / 同一个 LLM judge，judge 会倒向更好打分的一侧，通常是拒答或空话，见 `align-rlaif`、`align-llm-judge`。能力验收换家族或人；安全验收用攻击成功率，不要用「看起来无害」的 Likert。

切片比总分重要。英语 chat 持平、医疗建议全拒、代码 drop，平均能力可以假装没税。按领域、语言、是否需要双用途知识（化学实验课 vs 武器）拆开。双用途题要单独指南：该答的教学部分 vs 该拒的操作细节，见 `align-over-refuse`。

线上税更阴：用户改写、越狱、延迟导致的截断。离线 Pareto 过了仍要小流量看「该完成的任务完成率」。

## 怎么减税，面试说到可执行

数据：安全 SFT 混足够的 should-answer 反例，不要只喂拒答。对比学习用「同一问，有害答 vs 安全且有用答」，避免「有害 vs 拒绝」让模型学到拒绝万能。RL 把 helpful / harmless 分头或分阶段，KL 别把能力峰一起罚掉。推理：分类器门禁 + 主模型少做一刀切拒答，有时比把全部安全写进权重税更小，但要防分类器可绕过。

Checkpoint 选择对着 Pareto，不对着单一 harmlessness 新高。税过大就回滚安全数据配比，而不是加大学习率「冲回去」。

## 追问

- **能力掉 1 分换攻击成功率腰斩值不值？** 产品问题。面试给测量，给切片，让评委看到你不会单指标决策。
- **宪法 / 系统提示算对齐吗？** 算一层，税算在提示上时要单独 ablating 权重训练。
- **推理模型长链会不会看起来像 tax？** 延迟和长度上升不是 safety tax。看可验证正确率和过度拒绝，不要看 token 数。
- **和 red team 怎么分工？** 红队找漏拒；tax 测误拒和能力。两套集，两套门禁。
