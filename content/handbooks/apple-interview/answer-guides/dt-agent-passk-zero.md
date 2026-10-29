---
id: dt-agent-passk-zero
kind: design
situation: 某些任务的整组 rollout 奖励都相同。
task: 判断保留、降难度还是冷启动。
approach: 区分题太难、题太易和 scorer 没区分力。
result: 有效学习信号提高且任务覆盖没有被清空。
---

## 可以这样回答

某些任务的整组 rollout 奖励都相同。

全 0 或全 1 的组分不出好坏，组内优势为零，可以丢掉或降权。预算优先给当前模型偶尔能做对、多数时候还做错的中间带任务；从来没解出过的先查环境是不是坏了，再决定要不要搁置。policy update 后要重算 pass@$k$，难度分组不能一直冻着。
