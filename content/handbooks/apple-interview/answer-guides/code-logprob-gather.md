---
id: code-logprob-gather
kind: coding
situation: 当前位置 logits 预测的是下一个 token。
task: 只累计回答部分的 token 概率。
approach: 先 shift，再 gather，最后应用同样 shift 的 mask。
result: 用两三个 token 手算，确认 prompt 和 pad 不计分。
---

## 可以这样回答

当前位置 logits 预测的是下一个 token。

取 `logits[:, :-1]` 做 `log_softmax`，用 `token_ids[:, 1:]` 去 `gather`，再乘 shift 后的 response mask，prompt 和 pad 位都是 0。SFT、DPO、GRPO 都用这个原语，最容易错的是忘了 shift 和 prompt 没 mask 掉。

测试时，我会用两三个 token 手算，确认 prompt 和 pad 不计分。
