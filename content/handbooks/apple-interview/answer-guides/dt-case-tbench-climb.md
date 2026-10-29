---
id: dt-case-tbench-climb
kind: concept
situation: 训练环境涨分可能不迁移到终端基准。
task: 选择更有效的环境与反馈。
approach: 先查真实性、可学难度和 verifier 质量。
result: 独立终端任务收益与单位成本共同确认。
---

## 可以这样回答

训练环境涨分可能不迁移到终端基准。

几篇公开工作放在一起看，结论是环境要贴近真实任务、难度卡在中间、verifier 靠得住，环境数量排在最后。Endless Terminals 在自己的 development set 上涨了很多，到 Terminal-Bench 几乎不动；River 只用不到三成的环境，过滤掉坏 verifier 后增益更大。
