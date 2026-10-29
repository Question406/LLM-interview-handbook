---
id: dt-canary-leak
kind: concept
situation: 内容重叠与分数被抬高是两个问题。
task: 分别确认暴露和实际记忆收益。
approach: 扫描与金丝雀发现线索，变式新题检验影响。
result: 翻译和 teacher leakage 不只靠字面扫描排除。
---

## 可以这样回答

内容重叠与分数被抬高是两个问题。

分两步测：先查训练内容和评测有没有重叠，再查这种重叠有没有把分数抬高。重叠用 n-gram 扫描和金丝雀字符串查，是否虚高就把题目改数字、改变量名再测一遍。teacher model 间接 leakage n-gram 扫不到，要靠 embedding nearest neighbors 和私有评测。
