---
id: dt-utility-select
kind: concept
situation: 高质量不能只靠一个模糊形容词。
task: 把选择标准转成可讨论的效用。
approach: 明确收益目标，再选阈值、配额或加权 sampling。
result: 效用排序需要下游实验支持而非自证。
---

## 可以这样回答

高质量不能只靠一个模糊形容词。

可以。先给样本定义效用 $u(x)$，说明它为什么值得训练，再决定按阈值筛、按桶分配额，还是按分数加权 sampling。Albalak 等 2024 年的综述就是这样拆成两步的。启发式、ppl、分类器、EL2N 和 RL sampling，区别主要在效用怎么估。
