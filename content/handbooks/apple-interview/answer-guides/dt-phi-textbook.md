---
id: dt-phi-textbook
kind: concept
situation: 高信息密度合成可能提高样本效率。
task: 解释教科书式数据的收益与限制。
approach: 固定规模对照，检查 teacher 偏差和 contamination。
result: 未见知识及语言覆盖支持，不能只看旧榜单。
---

## 可以这样回答

高信息密度合成可能提高样本效率。

Phi 有效是因为提高了每个 token 的信息质量：Phi-1 用过滤代码加合成教材，让 1.3B 模型在 HumanEval 上超过更大的模型。局限在规模和 contamination，世界知识和 multilingual 仍需要足够多的许可网页，后续几代 Phi 也都加了数据量；teacher model 和改写带来的考题 leakage，n-gram deduplication 挡不住，要用新题和私有评测检查。
