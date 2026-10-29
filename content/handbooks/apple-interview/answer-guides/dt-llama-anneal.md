---
id: dt-llama-anneal
kind: concept
situation: pre-training 末期仍可用 data mix 补能力。
task: 解释 annealing 数据的阶段作用。
approach: 高质量域 data mix 与 learning rate 一起记录并控制变量。
result: 新能力与旧任务复测，公开配方不直接照搬。
---

## 可以这样回答

pre-training 末期仍可用 data mix 补能力。

Annealing 在主 pre-training 末段降 learning rate、上 sampling 高质量数学和代码，补可验证的能力，格式和工具行为留给 post-training。Llama 3 最后约 40M token 是它自己的公开配方，换模型要重新定，常用基准的 training set 不能混进来。它还能拿来低成本评估新数据源。
