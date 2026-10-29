---
id: dt-value-drift
kind: concept
situation: fine-tuning 后分布变化可能有益也可能有害。
task: 证明变化发生在预期行为上。
approach: 配对比较行为 evaluation slices、KL 和分维度 human evaluation。
result: 目标改善、regression tasks 稳定，不以 KL 大小定好坏。
---

## 可以这样回答

fine-tuning 后分布变化可能有益也可能有害。

漂本身不坏，要证明的是偏离发生在声明的轴上、已有能力还在。用同一批固定 prompt 对比 base model 和 fine-tuned model：按 evaluation slices 算 KL，跑行为套件，分开报安全与有用性，再做分维度 human evaluation。KL 大只说明分布变了，好坏要靠行为套件和 human evaluation 判断，总 loss 和 Arena 赢率给不出这些信息。对照数据用研究集和 frozen evaluation set。
