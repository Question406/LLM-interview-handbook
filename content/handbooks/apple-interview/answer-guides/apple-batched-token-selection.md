---
id: apple-batched-token-selection
kind: coding
situation: "B 条请求的 logits 是 [B,V]，每行可能有不同温度和合法集合。"
task: "返回每条请求的下一 token，保留确定性 tie rule 与正确 sampling 分布。"
approach: "逐行 mask、temperature、top-k，再在重新 normalization 后做 top-p；只让随机行消耗 RNG。"
result: "手算 greedy 与跨阈值样例，再用固定 seed 和频率检查两种随机实现。"
---

## 可以这样回答

我会先把单步选择与完整生成分开。这里每行是一条独立请求，所有排序和累计概率都沿 vocabulary 维进行，不能让其他请求影响本行候选。

确定性行直接返回合法最大值；随机行完成 temperature、top-k 和 top-p 后，再用 multinomial 或 Gumbel-max 选择。Top-p 保留跨阈值的 token，排序结果还要 gather 回原始 token ID。

我会用三行不同配置手算结果，再检查 mask、seed replay 和长期频率。下一张卡才负责 EOS、padding 与 cache。
