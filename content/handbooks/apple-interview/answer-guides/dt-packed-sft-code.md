---
id: dt-packed-sft-code
kind: coding
situation: 拼接样本后，监督和 attention boundaries 会混在一起。
task: 只学习助手回复且不跨样本读答案。
approach: loss mask 与文档 attention mask 分别构造。
result: 改变 prompt 或工具 token 不应新增监督项。
---

## 可以这样回答

拼接样本后，监督和 attention boundaries 会混在一起。

SFT 学的是给定上下文时助手怎么回答，所以只对助手回复算 cross-entropy，prompt、padding 和工具返回都不进监督目标。packed 序列里不同样本之间还要切断 attention，不然后一个样本能看到前一个的答案。漏掉 mask，模型就会同时学着重建用户文本和工具返回。

测试还要满足这个条件：改变 prompt 或工具 token 不应新增监督项。
