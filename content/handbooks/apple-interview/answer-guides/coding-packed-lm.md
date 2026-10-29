---
id: coding-packed-lm
kind: coding
situation: 变长样本需要压紧存放。
task: 记录每段起止并保持文档隔离。
approach: 用长度 prefix sum 建立 cu_seqlens，配合分段 causal attention。
result: 检查零长段、最后一个 document offset 和跨文档位置。
---

## 可以这样回答

变长样本需要压紧存放。

先按真实长度拼接有效 token，用长度为 $B+1$ 的 `cu_seqlens` prefix sum 标出各段起止。同一行放多篇独立文档时，要用块对角 causal mask，或把每篇当 varlen 序列，防止跨文档 attention。

测试时，我会检查零长段、最后一个 document offset 和跨文档位置。
