---
id: align-rft
section: alignment
order: 22
level: S
title: 对齐：Reinforcement Fine-Tuning / RLVR，可验证奖励接到策略
quick: >-
  RFT 不是再做一遍偏好 RLHF。你写 grader（代码或模型），对同题多样本打分，用策略梯度把高分轨迹抬起来。RLVR
  把奖励钉在可检查的对错上：单测、数学核对、schema。grader 会被刷，验收不能用同一套打分器。
tags:
  - OpenAI
  - DeepSeek
  - RFT
  - RLVR
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Reinforcement fine-tuning (OpenAI)
    url: https://developers.openai.com/api/docs/guides/reinforcement-fine-tuning
    type: primary
  - title: DeepSeek-R1 — Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Tulu 3 — Pushing Frontiers in Open Language Model Post-Training
    url: https://arxiv.org/abs/2411.15124
    type: primary
---

OpenAI 把 Reinforcement Fine-Tuning 做成推理模型上的产品面：你不训 RM，你提供 grader。DeepSeek-R1 / 开源后训练把同一思路叫可验证奖励上的 RL（常写作 RLVR）。对齐岗问的是「和 SFT、和 RLHF 差在哪、grader 坏了会怎样」，不是让你背平台按钮。不是某次现场逐字题。组相对实现见 `align-grpo`；过程密化见 `align-process-reward`。

## 循环：采样、打分、更新

对每个 prompt $x$，从当前策略抽 $G$ 条 $y_i$，grader 给标量 $r_i$，再做 policy gradient（常见就是组标准化优势 + clip，KL 到参考策略仍在）。和 SFT 的差别：没有唯一「正确文本」，只有「更高分的完成更该出现」。和经典 RLHF 的差别：奖励尽量来自**程序或规则**，不是人偏好蒸馏出的 $r_\phi$。

OpenAI 公开叙述里强调：先把任务做成 eval。若基座已经在该 eval 上顶格或全错，RFT 帮不上忙——没有可爬的坡。这和「成功率 0 时 GRPO 组内全零」是同一句话。grader 可以是确定性代码（单测、数值容差、JSON schema），也可以是模型打分。后者立刻退化成 LLM-as-judge / 弱 RM，过优化曲线见 `align-overopt-rm`。

```python
def rft_batch(prompts, sample_fn, grade_fn, G):
    # ys: [B, G]  completions; rs: [B, G]  grader scores
    ys = sample_fn(prompts, n=G)
    rs = grade_fn(prompts, ys)
    adv = (rs - rs.mean(dim=-1, keepdim=True)) / (rs.std(dim=-1, keepdim=True) + 1e-6)
    return ys, adv
```

RLVR 的公开定义就是：$r$ 由可自动核对的性质给出，数学最终答案、代码单测、结构化抽取字段。它不承诺开放对话变好。Tulu 3 一类开源栈把可验证 RL 和偏好 RL 分开写，面试不要说「RLVR 取代了 DPO」。

## grader 也是奖励函数，也会被 hack

可验证不等于不可刷。空实现、硬编码样例、把答案 `print` 出来骗检查器、格式分刷满内容错，都是旧问题，见 `align-reward-hack`。模型 grader 会偏长、偏客气、偏本家族文风，见 `align-llm-judge`。纪律：

- **训练 grader 和验收 grader 分开。** 验收用另一套单测、另一张 held-out 题、或人抽查。同一 grader 既优化又发版，就是 Gao 曲线的推理版。
- **eval 先于 RFT。** 分数已经 0 或 1 的集不要拿去训。
- **隐藏推理。** 若模型有内部思考预算，grader 应打最终可见答案，不要把隐藏链当监督标签，见 `align-cot-leak`。
- **KL / 参考。** 仍要限制跑出可用语言；RFT 不是「可以不要参考策略」。

成本按训练机时和采样条数走，比 SFT 贵一截。面试别报单价；说 $G$、平均完成长度、grader 本身是不是还要调一个大模型。

## 面试怎么选

有自动对错、基座已经会一点：RFT / RLVR 是正道，数据比写满示范便宜。只有偏好、没有核对：回到 RM / DPO / CAI，见 `align-dpo`、`align-cai`。工具环上「可验证」常常是任务成功而不是单次 API 200，见 `align-tool-rl`。白板我会写：SFT 拟合 $y^\star$，RFT 拟合 $r(x,y)$ 的高分区域；然后画一条 grader 分涨、held-out 单测掉的分叉，说明你知道 Goodhart。

## 追问

- **和 PPO + RM 是一回事吗？** 算法可以同一族。差在 $r$ 的来源：可验证核对 vs 学到的偏好。
- **模型 grader 算不算 RLVR？** 算弱验证。它把噪声和偏见写进 $r$，要当 proxy，并另备 gold。
- **为什么官方说 eval 先做？** 没坡就没有策略梯度。顶格是过拟合风险，全错是零学习。
- **能替代红队吗？** 不能。grader 覆盖的是你写得出检查的性质；未知有害见 `align-red-team`。
