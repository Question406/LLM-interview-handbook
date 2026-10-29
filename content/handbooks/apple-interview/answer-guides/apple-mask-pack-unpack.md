---
id: apple-mask-pack-unpack
kind: coding
situation: 有效 token 被 padding 分散在不同位置。
task: 压紧数据后还能按原位置恢复。
approach: 有效位 prefix sum 提供全局下标，配合 scatter 和 gather。
result: 恢复有效特征，检查空输入、全空和 gradient。
---

## 可以这样回答

有效 token 被 padding 分散在不同位置。

将 valid 展平做 cumsum，得到每个真实 token 的全局紧凑下标；scatter 写入 packed，gather 按下标还原。用额外的零行处理无效位置，避免 -1 索引误读最后一个 token。

测试还要满足这个条件：恢复有效特征，检查空输入、全空和 gradient。
