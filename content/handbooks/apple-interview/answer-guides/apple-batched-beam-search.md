---
id: apple-batched-beam-search
kind: coding
situation: "同一请求的两个新候选可能都来自同一条旧 beam。"
task: "为 B 条请求完成独立 K-beam 搜索，保证输出状态与 cache 指向同一历史。"
approach: "只在各自 K*V 内选择；恢复 parent 后同步 gather cache、mask、prefix 与状态，再 decode 新 token。"
result: "用手算转移与独立完整前缀搜索比对 tokens/score，测试重复 parent、EOS、tie 和不足 K 个合法候选。"
---

## 可以这样回答

假设本轮两个最好的 child 都来自 beam 0。它们不仅需要相同的 token 前缀，还必须从 beam 0 的 K/V 继续计算。

我会把每个请求自己的 K*V 候选排序，整除和取模得到 parent 与新 token，再加请求 offset 重排整个 cache。已结束候选只携带旧分数，不重复生成 EOS；候选不足时保留明确的 invalid 空位。

最后按题目约定做 length penalty 重排，并与逐条重算完整前缀的参考搜索比较。搜索中的剪枝与最终重排是两件事，不能混用。
