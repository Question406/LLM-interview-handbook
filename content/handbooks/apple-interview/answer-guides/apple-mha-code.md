---
id: apple-mha-code
kind: coding
situation: 多头、padding 与 cache 容易造成形状错位。
task: 实现完整 attention 并保持位置语义一致。
approach: 先明确 Q/K/V 形状，再计算得分、mask 和合并 heads。
result: 整段与逐 tokendecoding 对齐，检查输出和 gradient。
---

## 可以这样回答

多头、padding 与 cache 容易造成形状错位。

我会先把 $[B,T,d]$ 的输入投影并拆成 $[B,H,T,d_h]$ 的 Q/K/V，计算 $QK^\top/\sqrt{d_h}$，在 softmax 前加 causal 和 padding mask，再乘 V、合并 heads。比如带 cache decoding 时，新 query 的绝对位置从旧 cache 长度开始，完整序列与逐 token 结果应一致。

测试还要满足这个条件：整段与逐 tokendecoding 对齐，检查输出和 gradient。
