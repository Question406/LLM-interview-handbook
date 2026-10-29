---
id: afm-web-attention-code
kind: coding
situation: 多个序列带 padding，并要求 causal attention。
task: 输出数值正确且全 padding 行不产生 NaN 的 attention。
approach: 先推导 mask 的 query/key 方向，再安全地处理无可见 key 的行。
result: 通过手算、独立循环对照、future invariance 和 finite-gradient 检查。
---

## 可以这样回答

我会先确认形状和 mask 的语义：每个有效 query 只能看当前和之前的有效 keys。算完 scaled dot-product 后，用这三个条件构造 keep mask。

全 padding 行是最容易漏掉的 edge case。如果直接对全负无穷做 softmax，会产生 NaN。我会先把这种行的 scores 替换为零，softmax 后再把所有不可见位置的 weights 置零，所以无效 query 的最终输出也是零。

测试先用零 scores 得到可手算的平均值，再用显式循环对照不规则 padding，检查 future values 不影响较早输出，同时检查 backward 没有非有限值。
