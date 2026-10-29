---
id: dt-code-bench-bleed
kind: concept
situation: 代码改名和改写可绕过简单 deduplication。
task: 判断涨分是否来 self-training 评测重叠。
approach: 题意、规范代码、issue 和测试来源联合扫描。
result: 新时间窗任务支持收益，旧题涨分不冒充泛化。
---

## 可以这样回答

代码改名和改写可绕过简单 deduplication。

先查涨分是不是 leakage，再谈质量。拿固定的评测题和参考解，用精确匹配、13-gram、规范化后的代码和 embedding nearest neighbors 跟 training set 比对，再用训练截止后的 LiveCodeBench 新题看泛化。旧题涨、新题不动，这个涨分就算不上能力提升；SWE 类还要查 issue、PR 和测试文件。
