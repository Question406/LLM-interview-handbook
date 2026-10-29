---
id: dt-dpo-batch-code
kind: coding
situation: 偏好目标依赖策略与 reference policy 的相对差。
task: 实现稳定且 gradient 方向正确的 DPO loss。
approach: 构造两组 log-ratio 差，reference 保持冻结。
result: 相对差相同时为 log(2)，检查 chosengradient 方向。
---

## 可以这样回答

偏好目标依赖策略与 reference policy 的相对差。

DPO 比较策略与 reference policy 对 chosen/rejected 的序列 log probability 差，用稳定的负 log-sigmoid 求 loss。参考分数不应收到 gradient；当两组相对差相同时 loss 为 log(2)。

测试还要满足这个条件：相对差相同时为 log(2)，检查 chosengradient 方向。
