---
id: apple-batched-generation
kind: coding
situation: "两条不同长度的 prompts 同批生成，一条先出现 EOS，另一条还要继续。"
task: "完成 greedy 与两种 sampling 的生成循环，正确维护长度、mask、positions 和 KV。"
approach: "Left padding 后 prefill 一次，只给 active rows 选 token，随后按有效 token 数设置位置并用单 token decode。"
result: "逐步比较 cached 与完整前缀 logits，检查独立 EOS、pad=EOS、零步数及 batch/单条 greedy 一致。"
---

## 可以这样回答

假设两条请求的 prompt 长度分别是 1 和 3，第一条生成 EOS 后，第二条还需要继续。共同的矩阵宽度不能决定它们各自的逻辑 position。

我会先 prefill 一次，之后只送新 token 更新 KV；每条请求独立记录 finished 和 lengths。Finished 请求保留 static batch slot，后续 filler 被 mask，既不 sampling，也不增加真实长度。

先验证 cached logits 与完整前缀重算一致，再验证 greedy、multinomial 和 Gumbel 的完整生成。这里实现 static batch，不把它说成 continuous batching 服务。
