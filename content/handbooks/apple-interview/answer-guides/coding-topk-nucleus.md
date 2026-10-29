---
id: coding-topk-nucleus
kind: coding
situation: 变换顺序会改变最终候选分布。
task: 实现题目规定的 sampling 流程。
approach: 温度先改变概率，再做 top-k 和累计概率截断。
result: 手算小 vocabulary，测试 p 的极端取值与保留首个越界项。
---

## 可以这样回答

变换顺序会改变最终候选分布。

sampling 先屏蔽非法 token，再除温度 $T$，做 top-k，随后在剩余质量重新 normalization 的分布上做 nucleus 并 sampling。温度会改变 top-p 的累计质量，所以这一步必须在温度化之后；$T=0$ 或 $p=0$ 直接走 greedy。

测试时，我会手算小 vocabulary，测试 p 的极端取值与保留首个越界项。


本题的函数只接收一条请求的 `[V]` logits，返回一个 token。支持 `[B,V]`、逐行参数与两种随机实现的版本见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-token-selection)。
