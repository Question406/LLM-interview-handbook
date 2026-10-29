---
id: dt-wrap-rephrase
kind: concept
situation: 原网页有内容价值但表达不利于学习。
task: 判断改写是否提高样本效率。
approach: 保留原文和来源，验证改写事实与覆盖。
result: 固定预算比较，不把新措辞当新增知识。
---

## 可以这样回答

原网页有内容价值但表达不利于学习。

算一种有用的 data augmentation，前提是和原文一起用：清理后的原文和改写版本一起训，再验证样本效率有没有提高。WRAP 在 C4 上公开报告过约 3 倍样本效率，但改写不增加新事实，也解决不了许可、evaluation contamination 和 teacher 错误，所以要保留原文，记下 teacher 和来源。
