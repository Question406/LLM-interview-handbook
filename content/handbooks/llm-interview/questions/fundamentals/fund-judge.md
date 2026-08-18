---
id: fund-judge
section: fundamentals
order: 17
level: S
title: LLM-as-Judge 有哪些常见 Bias？怎么缓解？
quick: >-
  常见 position bias、verbosity bias、style bias、self/family preference、prompt
  sensitivity。可做 swap consistency、random position、rubric 分维度、multiple
  judges、human calibration 与 adversarial examples。
tags:
  - Eval
  - LLM Judge
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>常见 position bias、verbosity bias、style bias、self/family preference、prompt sensitivity。可做 swap consistency、random position、rubric 分维度、multiple judges、human calibration 与 adversarial examples。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p><b>Position bias：</b>A/B 交换顺序结论改变；<b>verbosity：</b>更长更详细被偏爱；<b>self-preference：</b>judge 偏爱同 family 风格；<b>style：</b>标题/自信语气替代 correctness。</p><p>缓解：pairwise swap 两次、随机顺序、隐藏 model identity、长度匹配、先抽取 evidence 再评分、多 judge majority/aggregation、用 human-labelled calibration set 估 judge-human agreement。</p><p>如果 judge 直接作为 RL reward，风险更大，因为 policy 会主动学 judge 的偏好；需要持续 red-team。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Pairwise 一定比 pointwise 稳吗？</summary><div class="follow-answer"><p>常见情况下相对比较更容易，但会有 position/order bias；pointwise 可独立标量化，但 calibration更难。</p></div></details><details class="followup"><summary>如何测 verbosity bias？</summary><div class="follow-answer"><p>构造内容等价但长度不同的 controlled pairs，或对同一答案加冗余段，看 judge score 变化。</p></div></details></div>
