---
id: dt-verifier-counterfactual
kind: design
situation: 高通过率可能来自宽松或被钻漏洞的检查。
task: 检验 verifier 是否奖励真正推理。
approach: 保持结果标签可比，对过程和 counterfactual 变化审计。
result: 高分错例减少且独立任务变好才继续扩量。
---

## 可以这样回答

高通过率可能来自宽松或被钻漏洞的检查。

通过率取决于 verifier 测了什么，不能替代数据有效性。检查答案 leakage、测试覆盖、过程正确性和重复模板，并用 counterfactual 样本审计 verifier；再用等预算 ablation study 区分过滤质量与任务难度。
