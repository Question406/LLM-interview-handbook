---
id: dt-token-accum-code
kind: coding
situation: 不同 microbatch 有效 token 数不同。
task: 让累积 gradient 等价于按 token 平均。
approach: 各批 loss 总和除以整个窗口 token 数，只更新一次。
result: 与合并 batch 的 gradient 比较，覆盖空监督批。
---

## 可以这样回答

不同 microbatch 有效 token 数不同。

当每个 microbatch 的有效 token 数不同，应把各批 token loss 总和除以整个累积窗口的有效 token 总数，再分别 backward；直接平均各批均值会把短批放大。一次窗口只清 gradient 和更新一次。

测试还要满足这个条件：与合并 batch 的 gradient 比较，覆盖空监督批。
