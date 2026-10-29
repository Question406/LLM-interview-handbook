---
{
  "id": "afm-web-dpo-beta",
  "kind": "concept",
  "situation": "DPO 有 reference policy 和 β，但常被误说成直接控制 sampling temperature。",
  "task": "从 objective 解释 β，并说明它与数据和优化共同作用。",
  "approach": "先看相对 log-prob margin，再区分理论 regularization 与实际 gradient scale。",
  "result": "能给出检查 KL、preference 和任务质量的 tuning 实验。"
}
---

## 可以这样回答

β 不是生成时的 temperature。DPO 关注的是 preferred answer 相对 rejected answer 的 log-probability，以及这个差值相对 reference policy 改了多少；β 会缩放进入 logistic loss 的这个 margin。

从推导里的 KL-regularized objective 看，更大的 β 对偏离 reference 的约束更强。但在实际训练里，它也改变 gradient 和饱和区间，所以不能只说 β 越大，模型实际 KL 就一定越小。

例如从 reference 初始化时，relative margin 是零，gradient 对 margin 的系数是负 β 除以二。β 很小，初始更新信号也会变小；β 较大，已经分对的 pair 可能更快进入饱和，但分错的 pair 仍可能产生较大的更新。这也说明 β 和 learning rate 不能分开看。

我会用相同数据、训练预算和 reference 比较几个 β，同时看独立 preference win rate、任务正确性、实际 KL 和长度变化。离线 preference pairs 是否覆盖当前模型的错误，也会影响选择，不能只靠一个超参数补救数据不匹配。
