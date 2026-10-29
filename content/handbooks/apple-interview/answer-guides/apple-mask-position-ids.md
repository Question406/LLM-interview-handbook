---
id: apple-mask-position-ids
kind: coding
situation: padding 可能在左侧、右侧或中间。
task: 给每行有效 token 连续编号。
approach: 累计有效位置再减一，最后单独覆盖无效位。
result: 用空维度、全 padding 和中间空位检查编号。
---

## 可以这样回答

padding 可能在左侧、右侧或中间。

对每行有效位置做 cumsum 后减一，再把无效位置设为 -1。按位置是否有效计数，不根据 token ID 猜 padding；同一实现支持左 padding、右 padding 及中间空位。

测试时，我会用空维度、全 padding 和中间空位检查编号。
