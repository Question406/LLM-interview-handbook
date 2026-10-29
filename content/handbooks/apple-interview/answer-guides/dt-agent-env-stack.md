---
id: dt-agent-env-stack
kind: design
situation: 评测与训练需要共享可复现环境。
task: 打包完整任务而非零散容器。
approach: 版本化初态、工具、依赖、reset 和 verifier。
result: 干净实例可反复 replay，训练看不到隐藏真值。
---

## 可以这样回答

评测与训练需要共享可复现环境。

打包成一个能 pip install 的任务环境，里面有任务说明和初始资源、把 tool calls 接到真实系统的 harness、给结果打分的 rubric。三样都要能安装、能版本化，训练和评测共用同一套执行和评分逻辑，两边的目标才一致。只有 prompt 模板、没有可执行动作和 scorer，撑不起 Agent RL。
