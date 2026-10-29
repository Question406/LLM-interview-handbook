---
id: dt-trigger-ood
kind: concept
situation: 海量流量不能都当训练 gold labels。
task: 发现值得复现的失败类型。
approach: 用验证失败或分歧触发，再合法采集研究样本。
result: long-tail 收益真实，影子输出和沉默不直接当认可。
---

## 可以这样回答

海量流量不能都当训练 gold labels。

把车队 trigger 的思路换成「评测失败触发收集」：固定评测失败、judge 或人与 RM 的分歧、工具验证失败和低置信步骤，才值得进 feedback loop，再用许可或 synthetic data 复现。影子模式的输出当不了 gold labels，用户没改摘要也不等于认可。可验证样本自动扩，主观 hard examples 按人工预算处理。
