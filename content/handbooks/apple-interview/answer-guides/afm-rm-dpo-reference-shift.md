---
id: afm-rm-dpo-reference-shift
kind: concept
situation: chosen 与 rejected 概率可能同时下降。
task: 解释 DPO 改善的相对目标。
approach: 拆开策略和 reference 的两侧 logprob。
result: 检查实际生成质量与新策略覆盖。
---

## 可以这样回答

因为它优化的不是单独把 chosen 概率推高。比如 chosen 的 logprob 从负10变成负12，rejected 从负11变成负18，两条都降了，但它们的差距反而从1变成6。reference 固定时，DPO 目标仍然可能改善。

所以只看 loss 下降或 chosen 概率变化都不够。我会检查两边的概率、reference 是不是固定、回答长度和实际生成质量。如果模型在旧 preference pairs 上越学越好，当前回答却变差，还要查数据是不是已经跟不上新策略。
