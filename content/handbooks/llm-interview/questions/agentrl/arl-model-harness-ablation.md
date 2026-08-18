---
id: arl-model-harness-ablation
section: agentrl
order: 11
level: S
title: 怎么判断提升来自 Model，还是 Harness / Tool / Budget？
quick: >-
  必须做 controlled ablation：固定 model、tools、token
  budget、environment、scaffold，只替换一个变量；最好做 model×harness 交叉矩阵，分离 main effect 和
  interaction。
tags:
  - Eval Design
  - Harness
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>必须做 controlled ablation：固定 model、tools、token budget、environment、scaffold，只替换一个变量；最好做 model×harness 交叉矩阵，分离 main effect 和 interaction。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>最小 2×2 设计：A+X、A+Y、B+X、B+Y。若 B 只在 Y harness 上强，说明存在 interaction；不能把 B+Y 相比 A+X 的全部差异归因给 model。</p><p>工具集也要固定：更强 search、更多 retries、更大 context、更多 sub-agents 都相当于 test-time compute。应报告成功率与 cost/latency 的 Pareto curve。</p><p>如果目标是评 model intrinsic capability，可以使用 standardized harness；如果目标是产品 system capability，则可以优化全栈，但结论应写“system improves”而不是“model improves”。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Leaderboard 为什么常无法回答模型能力？</summary><div class="follow-answer"><p>不同提交可能使用不同 scaffold、tool budget、retry、prompt、parallelism；分数是 system property。</p></div></details><details class="followup"><summary>Harness 本身也需要训练怎么办？</summary><div class="follow-answer"><p>做 joint ablation 或冻结其中一侧；报告训练数据/compute，并测试 cross-model/cross-harness transfer。</p></div></details></div>
