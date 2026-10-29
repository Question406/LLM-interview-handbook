---
id: afm-rm-rm-pooling-truncation
kind: concept
situation: 模板或 padding 可能成为训练捷径。
task: 确认实际打分位置与有效回答。
approach: 逐 token 核对 pooling、截断和 mask。
result: 相同内容换 padding 不应改变判断，截断对需复核。
---

## 可以这样回答

我会先把一个 batch 打印出来，看看 token、mask、截断位置和实际取来打分的位置。比如右侧补了 padding，却直接取最后一个位置，那读到的可能已经不是回答结束的位置。

训练准确率高并不能排除这种错误。假如好回答普遍更长，模型可能只学了长度或模板特征。我会先用同一条回答换不同 padding 长度，看分数会不会变；再查两条回答是不是截断以后已经一样，却仍然带相反标签。实现和数据先对上，再讨论模型容量。
