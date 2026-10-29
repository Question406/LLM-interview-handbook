---
id: apple-ondevice-agent
kind: design
situation: 离线执行与私有状态限制 on-deviceagent。
task: 选择本地工具与 on-device / server 分工。
approach: 按权限和可用性规划，写入前核对状态。
result: 离线和失败条件下不编造完成，设备成本达标。
---

## 可以这样回答

离线执行与私有状态限制 on-deviceagent。

on-device agent 由模型输出结构化调用，再由 App 的 `Tool` 或系统 App Intent 执行；发、删、付款等副作用要经过确认。离线时只暴露本地工具，宿主程序限制轮数、耗时和资源，工具失败也要按真实状态返回。
