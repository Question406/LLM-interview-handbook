---
id: apple-decoding-guide
kind: guide
situation: '会对 [V] 选一个 token，不等于能让不同长度的多条请求完成生成。'
task: 分清批量 token selection、完整生成循环和 serving 调度的范围。
approach: 先写批量 selector，再维护 EOS、mask、positions 和 KV，最后处理 beam parent 重排。
result: 用手算样例、随机频率、完整前缀 logits 与独立搜索参考验证实现。
---

## 可以这样回答

我会先写 [B,V] 到 [B] 的 token selection，再接入完整生成循环。不同请求要独立处理 EOS 和长度，left padding 后的逻辑 position 也不能直接用矩阵列数。

先完成 [[apple-batched-token-selection]] 和 [[apple-batched-generation]]，确认 greedy、multinomial、Gumbel 都能多步运行，再做 [[apple-batched-beam-search]]，验证 parent 改变时 cache 与状态一起移动。

原来的单请求入门题仍然保留。新版本是 static batch generation；continuous batching、speculative serving 和 grammar compiler 没有被悄悄算作已实现。
