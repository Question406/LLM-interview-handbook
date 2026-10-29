---
id: dt-ondevice-distill-data
kind: design
situation: distillation 预算不足以重放全部 pre-training。
task: 选择 on-device 最需要的监督。
approach: 目标任务、困难 evaluation slices 和语言覆盖优先。
result: 同成本 student 收益与 teacher 事实正确性均检查。
---

## 可以这样回答

distillation 预算不足以重放全部 pre-training。

AFM 公开的 on-device 配方没有从头蒸：先用 1T 高质量数据把 dense on-device 模型 sparse-upcycle 成 MoE teacher，再只在 dense student 最后约 10% 的 token（约 1.4T）上加 distillation 损失，teacher 训练成本因此降了约 90%。蒸什么还要看 3B student 学不学得会、对不对得上产品任务，server 的长 RL trajectories 不宜原样蒸。
