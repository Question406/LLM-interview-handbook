---
id: dt-pretrain-pack-code
kind: coding
situation: 文档长度不同，需要填满固定训练块。
task: 高效打包并明确跨文档语义。
approach: 保留 document offsets，按训练契约决定 attention 隔离。
result: token 守恒、尾块和跨文档位置的 loss 均需检查。
---

## 可以这样回答

文档长度不同，需要填满固定训练块。

把文档贪心装进长度为 `seq_len` 的序列，文档之间插 BOS/EOS，在 document boundaries 切断 attention，padding 不算 loss。这样算力不浪费在 pad 上，模型也不会跨篇续写。pre-training 一般监督文档里的大部分 token，SFT 还要按角色限制监督范围，见 `dt-packed-sft-code`。

测试还要满足这个条件：token 守恒、尾块和跨文档位置的 loss 均需检查。
