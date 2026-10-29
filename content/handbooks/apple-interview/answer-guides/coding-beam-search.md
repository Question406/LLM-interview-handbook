---
id: coding-beam-search
kind: coding
situation: 局部最大不一定是最好完整序列。
task: 维护多个前缀并正确终止和评分。
approach: 扩展累计 logprob，EOS 停止，length penalty 按约定使用。
result: beam=1对齐 greedy，核对完成序列和 length bias。
---

## 可以这样回答

局部最大不一定是最好完整序列。

Greedy 每步取 $\arg\max$，beam 保留 $k$ 条前缀按累计 log-prob 扩展，$k=1$ 就退化为 greedy，sampling 则按指定分布随机选 token。beam 要让 EOS 后停止扩展、按 parent 重排 KV，并用 length penalty 缓解短句分数偏高；最后重排与搜索中使用惩罚也要分清。

测试还要满足这个条件：beam=1对齐 greedy，核对完成序列和 length bias。


本题是单 prompt 的完整搜索，width=1 只得到单请求 greedy；不包含 batch KV 推理。完整 `[B,K,V]` 搜索和 cache 重排见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-beam-search)。
