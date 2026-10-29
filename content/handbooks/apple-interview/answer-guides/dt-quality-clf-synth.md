---
id: dt-quality-clf-synth
kind: concept
situation: teacher 标签可能偏爱正式英语文风。
task: 避免质量分类器系统性误删。
approach: 按语言领域抽查、calibration，并记录 teacher 版本。
result: small model 下游实验支持阈值，long-tail 仍有覆盖。
---

## 可以这样回答

teacher 标签可能偏爱正式英语文风。

坑在于一个分类器、一个阈值套所有数据：teacher 偏爱正式英文时，论坛内容和 low-resource 语言会被大量误删，和评测同族的分类器还会让 contamination 更容易混进来。所以按语言和领域分别训练或 calibration，代码、数学、对话不用网页教育价值标准；阈值用 small model 下游实验选，teacher 版本和抽查一致率记进 dataset card。
