---
id: dt-packed-attention-code
kind: coding
situation: padding query 与真实 query 契约不同。
task: 实现题目指定的安全 packed 可见性。
approach: 真实位置同文档且 causal，padding 按约定处理。
result: padding 输出和 loss 丢弃，避免全屏蔽 NaN。
---

## 可以这样回答

padding query 与真实 query 契约不同。

真实 query 只能看到同文档、不晚于自己的真实 key。padding query 本题只允许看自身以避免全屏蔽行，且其输出与 loss 必须丢弃；注意不同 PyTorch attention 接口的 bool mask 语义可能相反。

测试还要满足这个条件：padding 输出和 loss 丢弃，避免全屏蔽 NaN。
