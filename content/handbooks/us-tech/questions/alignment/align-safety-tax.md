---
id: align-safety-tax
section: alignment
order: 17
level: A
title: 对齐：安全对齐掉能力，怎么测
quick: "Safety tax 是安全训练带来的能力或有用性损失。我会固定提示和解码，对齐前后分别测能力、误拒和攻击成功率，再看安全与能力的 Pareto 取舍，避免把一律拒答当成安全进步。"
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

测 safety tax，要同时知道安全改善多少、能力损失多少，以及误拒是否增加。比如模型开始拒绝「kill 一个进程」，攻击成功率可能下降，但编程助手也变得不好用了。InstructGPT 讨论了 RLHF 后能力剖面的变化，XSTest 专门测过度拒绝，Safety-Tuned LLaMAs 则记录了安全 SFT 对有用性的影响。

## 固定条件后对比三组指标

安全对齐改的是策略支撑：抬无害峰、压有害峰，见 `align-rlhf-kl`。伴随的能力损失包括：拒答覆盖到 benign 双关、推理链被套话打断、代码/数学变短且错、多语言安全头硬、工具该调用时改道歉。这些叫 tax。拒答率本身不是 tax，也不是安全。

我会固定温度、最大 token 数和工具开关，在对齐前后各跑三组评测：

1. **能力。** 内部私有集 + 公开集去污染后，见 `align-eval-contam`。含数学、代码、多步指令、长上下文。解码明确固定下来：温度、最大 token 数、工具开关。
2. **过度拒绝。** XSTest 一类：看起来危险、实际无害（「kill 一个进程」、虚构犯罪小说）。按类别切片，不要一个拒答率。
3. **真实安全。** 红队 / jailbreak / 政策类有害遵从。攻击集要 held-out，不能和训练拒答模板重合。

再把能力或 helpful 盲测放在横轴、安全指标放在纵轴，攻击成功率越低越好。报告各 checkpoint 相对 SFT 基线的移动，才能看清安全改善付出了什么代价。

```python
def tax_report(before, after):
    # each dict: capability, over_refuse, attack_success  (same decode)
    cap = after["capability"] - before["capability"]
    over = after["over_refuse"] - before["over_refuse"]
    atk = after["attack_success"] - before["attack_success"]
    return {"d_capability": cap, "d_over_refuse": over, "d_attack": atk}
```

如果能力下降、误拒增加、攻击成功率下降，说明安全改善伴随明显代价。攻击没降而能力掉了，就没有得到预期收益。理想情况是攻击下降，误拒不升，能力基本持平。

## 排除混淆，再决定怎么改

解码不一致：对齐后 max token 更长或更短，能力差是长度不是对齐。提示不一致：系统提示加了长宪法，基线没有，税算在提示上。污染：安全示范进了能力集，或能力题进了拒答训练。评测 judge 偏爱拒答套话，会把 tax 估低。

helpful 和 harmless 用同一个 奖励模型（RM） / 同一个 LLM judge，judge 会倒向更好打分的一侧，通常是拒答或空话，见 `align-rlaif`、`align-llm-judge`。能力验收换家族或人；安全验收用攻击成功率，不要用「看起来无害」的 Likert。

还要看切片。英语聊天持平，可能掩盖医疗建议全拒和代码能力下降。按领域、语言、是否需要双用途知识（化学实验课 vs 武器）拆开。双用途题要单独指南：该答的教学部分 vs 该拒的操作细节，见 `align-over-refuse`。

线上还存在不容易在离线发现的能力损失：用户改写、越狱、延迟导致的截断。离线 Pareto 过了仍要小流量看「该完成的任务完成率」。

要减小损失，我会先改数据配比：安全 SFT 混入足够的 should-answer 反例；同题比较有害回答和安全且有用的回答，避免所有偏好对都以拒绝获胜。强化学习（RL）里把 helpful / harmless 分头或分阶段处理，检查 KL 是否连能力模式也一起压掉。推理侧也可以用分类器门禁，让主模型少做一刀切拒答，但分类器本身仍可能被绕过。

选择 checkpoint 时看 Pareto，不能只追 harmlessness 新高。代价过大时先回滚安全数据配比，排查损失来源。

相关：`align-over-refuse`、`align-red-team`。

## 追问

**能力掉 1 分换攻击成功率腰斩值不值？**
产品问题。面试给测量，给切片，让评委看到你不会单指标决策。
**宪法 / 系统提示算对齐吗？**
算一层，税算在提示上时要单独 ablating 权重训练。
**推理模型很长的推理过程会不会看起来像 tax？**
延迟和长度上升不是 safety tax。看可验证正确率和过度拒绝，不要看 token 数。
**和 red team 怎么分工？**
红队找漏拒；tax 测误拒和能力。两套集，两套门禁。
