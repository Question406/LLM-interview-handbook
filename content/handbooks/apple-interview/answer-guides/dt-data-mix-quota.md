---
id: dt-data-mix-quota
kind: concept
situation: 大来源容易挤掉稀缺但重要的能力。
task: 把 token 预算对应到能力需求。
approach: 小规模 data mix 实验，保留来源独立测试。
result: target evaluation slices 提高，来源替换和旧能力仍稳定。
---

## 可以这样回答

大来源容易挤掉稀缺但重要的能力。

按能力类别分配 token 预算，预算来自冻结评测上的缺口，初值用小规模 data mix 实验或 mixing law 来定。要证明没背某个源，每个来源都留去过污的独立 test set，做 leave-one-source-out，并报 near-duplicates contamination rate。只看总 loss，或凭经验定 1:1:1，都说明不了问题。
