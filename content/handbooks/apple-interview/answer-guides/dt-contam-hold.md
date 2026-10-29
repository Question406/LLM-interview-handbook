---
id: dt-contam-hold
kind: concept
situation: 被 contamination 的 evaluation gate 已无法支持可靠发布判断。
task: 暂停依赖旧分数的决策并恢复评价。
approach: 估影响、查来源，换独立新题复测。
result: 结论重建可信度，删数据不自动修复旧模型。
---

## 可以这样回答

被 contamination 的 evaluation gate 已无法支持可靠发布判断。

先停所有依赖这份评测的模型比较和发布，它的分数已经不可信。然后按类别估计 contamination 影响，旧结论保留但降低可信度，再换训练截止后的新题或私有题重测。只从 training set 删掉命中内容，证明不了已训练模型的评测又可靠了。
