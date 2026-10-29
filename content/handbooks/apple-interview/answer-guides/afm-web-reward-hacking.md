---
{
  "id": "afm-web-reward-hacking",
  "kind": "concept",
  "situation": "Policy 的 reward score 持续上升，但回答更冗长，独立质量没有提高。",
  "task": "区分 reward model 学错、policy distribution shift 与真正的能力提升。",
  "approach": "用同 prompt 的 preference 数据训练，再用独立评价检查 score 与行为是否一致。",
  "result": "真实质量提高，而非只提高被优化的 proxy。"
}
---

## 可以这样回答

我会用同一个 prompt 下的可比回答收集 preference labels，让 reward model 学习哪个回答更好，而不是把不同难度任务的答案随意配对。标签需要明确 rubric，也要保留 disagreement，不能假设所有人都偏好同一种风格。

如果训练时 reward 上升，但回答越来越长，我会先检查独立 human evaluation 和可执行任务结果有没有同步改善。然后按长度、任务类型和 policy checkpoint 分析，看看 reward model 是不是把冗长当成质量，或者遇到了训练时没有见过的回答分布。

确认问题后，我会补充能区分内容质量与表面风格的对照数据，例如同样正确但长度不同的答案，以及很流畅但实际上错误的答案。再限制继续优化的幅度，必要时回滚到独立质量尚未退化的 checkpoint。KL constraint 可以帮助限制漂移，但不能修复一个学错的 reward。

我会用新的 held-out prompts 和独立评审验收。如果只有 reward model 自己给分更高，我不会把它报告成 alignment 改善。
