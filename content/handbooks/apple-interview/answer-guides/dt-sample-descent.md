---
id: dt-sample-descent
kind: concept
situation: 样本增加不保证误差单调下降。
task: 避免凭条数判断 mix 价值。
approach: 相同预算比较 data mix 和学习曲线。
result: 固定评价支持收益，非单调现象不代替 ablation study。
---

## 可以这样回答

样本增加不保证误差单调下降。

意味着增加样本不保证评测一直变好：在插值区附近，测试误差可能先升再降，同类数据翻倍也可能变差。所以调 data mix 时，在相同计算预算下对比新旧 data mix 在固定 evaluation set 上的表现，同时看目标任务和旧能力。double descent 只是提醒结果可能非单调，比例还是由 ablation study 来定。
