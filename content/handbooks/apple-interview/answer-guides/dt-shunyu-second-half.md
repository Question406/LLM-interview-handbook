---
id: dt-shunyu-second-half
kind: design
situation: Agent 改进依赖环境和交互，不只是静态文本。
task: 把公开观点转成可操作数据职责。
approach: 围绕任务分布、环境反馈与 verifiable reward 解释。
result: 用一个可执行任务说明职责，限定公开结论。
---

## 可以这样回答

Agent 改进依赖环境和交互，不只是静态文本。

Yao 的配方按重要性排是语言 pre-training 给的先验、可执行环境和能自动计算的 outcome reward，最后才是算法。数据岗该听的是「任务定义比算法难」，定义任务、构造环境、降低评分噪声都是数据岗的活。只把 PPO 换成 GRPO 变体，解决不了任务和奖励本身的问题。
