---
id: apple-spec-edge
kind: design
situation: 草稿模型本身也消耗 on-device 资源。
task: 判断 speculative decoding 是否有净收益。
approach: 合并 acceptance rate、草稿成本、验证与内存测量。
result: 同设备净延迟和能耗提高，分布要求保持。
---

## 可以这样回答

草稿模型本身也消耗 on-device 资源。

on-device speculative decoding 是否值得，要看草稿成本、平均接受长度、KV 回滚和稳态功耗；草稿很便宜、acceptance rate 高时才可能省时。草稿宜与目标同设备、同静态档位，TTS 只能读已验证 token；Apple 公开的 30 token/s 是投机之前的数字。
