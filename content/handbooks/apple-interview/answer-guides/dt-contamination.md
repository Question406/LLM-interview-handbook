---
id: dt-contamination
kind: design
situation: 评测可能被直接或间接写入训练。
task: 识别重叠及它对结论的影响。
approach: 精确、n-gram、语义与来源检查相结合。
result: 新题复测支持结论，删命中不等于模型已忘。
---

## 可以这样回答

评测可能被直接或间接写入训练。

把冻结的评测题和训练数据从便宜到贵逐层比对，依次比 URL、n-gram、embedding nearest neighbors，再拿训练截止后才出现的新题作对照，旧题好、新题差就是 leakage 的警报。确认 leakage 后，正式评测换新题，旧题降为 development set，命中的训练文档隔离出下一轮 mix，对外同时报新旧两套结果。
