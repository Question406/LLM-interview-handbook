---
id: dt-synth-bench-trap
kind: concept
situation: 合成集声称大幅涨公开分可能含 leakage。
task: 先确认结果是否代表泛化。
approach: 检查改写、翻译和 teacher 提示，再用新题验证。
result: 去 contamination 后仍有独立收益，才讨论扩大使用。
---

## 可以这样回答

合成集声称大幅涨公开分可能含 leakage。

先查 contamination，再谈质量。对照冻结评测做精确匹配、n-gram 和 embedding nearest neighbors 检索，抽查改写题、翻译题，再用按时间切出的新题验证增益；质量过滤和 MinHash deduplication 证明不了没训到测试题。排除 contamination 后，才检查答案和推理过程；自己 synthetic data 时，生成提示里也不能放评测题。
