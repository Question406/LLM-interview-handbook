---
id: apple-topk-sample
kind: coding
situation: on-device sampling 既要合法也受延迟约束。
task: 正确组合温度、top-k 与 top-p。
approach: 先屏蔽再调温度，筛候选后重新 normalization。
result: 检查全 mask、零温度、固定 seed 与候选数。
---

## 可以这样回答

on-device sampling 既要合法也受延迟约束。

sampling 先屏蔽非法 token，再除温度、做 top-k、在 renormalization 后的分布上做 nucleus，最后 sampling。比如温度为 0 直接选合法 token 中的最大值，全 mask 则报错；on-device top-k 候选数固定，便于控制延迟和 ANE 静态 shape。

测试时，我会检查全 mask、零温度、固定 seed 与候选数。


本题保留单请求 `[V]` 入门接口。完整 batched greedy / sampling、独立 EOS 与 KV cache 版本见[新增 batch 实现](?book=apple-interview&section=decoding&question=apple-batched-generation)。
