---
id: p3a-apple-cvml-image-evaluation
kind: design
situation: 生成图像好看不等于满足指令。
task: 分别评质量、条件一致和局部正确。
approach: 客观检查与分维度 human evaluation 结合。
result: 困难指令与偏差 evaluation slices 可靠，不用单一美学分。
---

## 可以这样回答

生成图像好看不等于满足指令。

把图像质量、文本遵循、组合关系、多样性与安全分开测。用成对提示控制颜色、数量、位置等因素，自动评分先与盲评 calibration；FID 不能证明某条提示被满足，单个相似度总分也会掩盖属性绑定错误。
