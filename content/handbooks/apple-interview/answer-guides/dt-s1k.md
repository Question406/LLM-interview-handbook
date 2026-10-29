---
id: dt-s1k
kind: concept
situation: 少量高质数据的收益依赖 student 已有能力。
task: 判断条数、难度与质量的关系。
approach: 控制预算比较可学示范，decoding 预算另记。
result: 新题和 long-tail 有效，不能只模仿超长推理。
---

## 可以这样回答

少量高质数据的收益依赖 student 已有能力。

1000 条够不够，取决于 student model 已经会多少，以及示范是否同时兼顾难度、多样性和质量。s1K 是在已指令对齐的 32B 上补一点推理，条数没法和别的配方横比；多堆 59k，质量和难度跟不上就只是加噪声。Budget forcing 是 inference 时控制思考长度的 decoding 方法，不算训练数据；student 学不会的超长推理要过滤，分布一偏还得靠 RLVR。
