---
id: dt-agent-verified-stale
kind: design
situation: 公开评测会随可解性和 contamination 审计变化。
task: 理解基准失效对训练选择的影响。
approach: 回到公开说明核对问题，不只记一个排名。
result: 使用可审计的新任务，历史成绩保留 version scope。
---

## 可以这样回答

公开评测会随可解性和 contamination 审计变化。

不能直接算赢。分数涨了先查两件事：测试是不是在考题面没写的要求，题目和标准补丁有没有进训练。Verified 人审过 500 题，仍然有测试质量和 leakage 问题，OpenAI 2026-02 已停报。训练池和评测池要隔开，并留一份按时间划分、能刷新的 holdout。
