---
id: apple-token-prune
kind: design
situation: 视觉 token 冗余但关键小区域可能稀有。
task: 减少成本同时保留任务证据。
approach: 剪枝/合并按证据价值比较，保留困难区域。
result: 同预算测细粒度任务和 long-tail 退化。
---

## 可以这样回答

视觉 token 冗余但关键小区域可能稀有。

视觉 token 可以按 attention 剪掉或按相似度合并，减少后续 prefill 和 KV 开销，但小字和定位通常先受损。on-device 要把剩余数量固定为 $K$ 并保留原图索引；分别测 OCR、grounding 和 VQA，再决定压缩比例。
