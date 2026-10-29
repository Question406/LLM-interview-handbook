---
id: align-rft
section: alignment
order: 22
level: S
title: 对齐：Reinforcement Fine-Tuning / RLVR，可验证奖励接到策略
quick: >-
  RFT 对同一道题 sampling 多个回答，用 grader 打分，再提高高分回答出现的概率。RLVR
  的奖励来自单测、数学核对等可自动验证的性质；我会先确认基座有对有错，再用独立测试验收，避免把 grader 的漏洞学进去。
tags:
  - OpenAI
  - DeepSeek
  - RFT
  - RLVR
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Reinforcement fine-tuning (OpenAI)
    url: 'https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning'
    type: primary
  - title: >-
      DeepSeek-R1 — Incentivizing Reasoning Capability in LLMs via Reinforcement
      Learning
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: Tulu 3 — Pushing Frontiers in Open Language Model Post-Training
    url: 'https://arxiv.org/abs/2411.15124'
    type: primary
---

## 可以这样回答

RFT 先让当前策略生成回答，再由 grader 打分，用 policy gradient 提高高分轨迹的概率。例如代码题可以跑单测，不必为每题写唯一的标准代码。OpenAI 的 Reinforcement Fine-Tuning 由用户提供 grader；DeepSeek-R1 和开源后训练中的 RLVR，则强调奖励来自可自动核对的性质。

对每个 prompt $x$，从当前策略抽 $G$ 条 $y_i$，grader 给标量 $r_i$，再做 policy gradient（常见就是组 standardization 优势 + clip，KL 到 reference policy 仍在）。和 SFT 的差别：没有唯一「正确文本」，只有「更高分的完成更该出现」。和经典 RLHF 的差别：奖励尽量来自**程序或规则**，不是人偏好 distillation 出的 $r_\phi$。

## 技术备查

RFT 先让当前策略生成回答，再由 grader 打分，用 policy gradient 提高高分轨迹的概率。例如代码题可以跑单测，不必为每题写唯一的标准代码。OpenAI 的 Reinforcement Fine-Tuning 由用户提供 grader；DeepSeek-R1 和开源后训练中的 RLVR，则强调奖励来自可自动核对的性质。

## 先确认任务有可学习的信号

对每个 prompt $x$，从当前策略抽 $G$ 条 $y_i$，grader 给标量 $r_i$，再做 policy gradient（常见就是组 standardization 优势 + clip，KL 到 reference policy 仍在）。和 SFT 的差别：没有唯一「正确文本」，只有「更高分的完成更该出现」。和经典 RLHF 的差别：奖励尽量来自**程序或规则**，不是人偏好 distillation 出的 $r_\phi$。

OpenAI 公开叙述里强调：先把任务做成 eval。若基座已经在该 eval 上顶格或全错，RFT 帮不上忙——没有可爬的坡。这和「成功率 0 时 GRPO 组内全零」是同一句话。grader 可以是确定性代码（单测、数值容差、JSON schema），也可以是模型打分。后者立刻退化成 LLM-as-judge / 弱 RM，过优化曲线见 `align-overopt-rm`。

```python
def rft_batch(prompts, sample_fn, grade_fn, G):
    # ys: [B, G]  completions; rs: [B, G]  grader scores
    ys = sample_fn(prompts, n=G)
    rs = grade_fn(prompts, ys)
    adv = (rs - rs.mean(dim=-1, keepdim=True)) / (rs.std(dim=-1, keepdim=True) + 1e-6)
    return ys, adv
```

RLVR 的奖励 $r$ 来自可自动核对的性质，如数学最终答案、代码单测和结构化抽取字段。它的提升不自动扩展到开放对话。Tulu 3 等开源栈也把可验证 RL 和偏好 RL 分开，两类方法适用的信号不同。

## 怎么防止模型利用 grader 的漏洞

可验证不等于不可刷。空实现、硬编码样例、把答案 `print` 出来骗检查器、格式分刷满内容错，都是旧问题，见 `align-reward-hack`。模型 grader 会偏长、偏客气、偏本家族文风，见 `align-llm-judge`。我会按下面的方式隔离训练与验收：

- **训练 grader 和验收 grader 分开。** 验收用另一套单测、另一张 held-out 题、或人抽查。同一 grader 既优化又发版，就是 Gao 曲线的推理版。
- **eval 先于 RFT。** 分数已经 0 或 1 的集不要拿去训。
- **隐藏推理。** 若模型有内部思考预算，grader 应打最终可见答案，不要把隐藏链当监督标签，见 `align-cot-leak`。
- **KL / 参考。** 仍要限制跑出可用语言；RFT 不是「可以不要 reference policy」。

成本取决于训练机时和 sampling 条数，通常比 SFT 高。估算时要报 $G$、平均完成长度，以及 grader 是否还要调用大模型。

任务能自动判对错、基座也已经会一点时，可以考虑 RFT / RLVR，收集奖励信号可能比写满示范更便宜。只有偏好、无法核对对错时，则考虑 RM / DPO/ CAI。工具任务要验证业务终态，单次 API 200 不代表成功。可以把区别写成：SFT 拟合 $y^\star$，RFT 拟合 $r(x,y)$ 的高分区域。grader 分上升而 held-out 单测下降，就是需要停下来检查的分叉。

相关：`align-grpo`、`align-process-reward`、`align-dpo`、`align-cai`、`align-tool-rl`。

## 追问

**和 PPO + RM 是一回事吗？**
算法可以同一族。差在 $r$ 的来源：可验证核对 vs 学到的偏好。
**模型 grader 算不算 RLVR？**
算弱验证。它把噪声和偏见写进 $r$，要当 proxy，并另备 gold。
**为什么官方说 eval 先做？**
没坡就没有 policy gradient。顶格是 overfitting 风险，全错是零学习。
**能替代红队吗？**
不能。grader 覆盖的是你写得出检查的性质；未知有害见 `align-red-team`。
