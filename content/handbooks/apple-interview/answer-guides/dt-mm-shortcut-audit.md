---
id: dt-mm-shortcut-audit
kind: design
situation: 截图题在新 UI 上突然失效。
task: 区分内容理解与布局捷径。
approach: 布局、文字、区域和证据做 controlled substitution。
result: 未见 UI 表现支持数据干预，模板 near-duplicates 隔离。
---

## 可以这样回答

截图题在新 UI 上突然失效。

用图像、文字与布局的受控干预判断模型是否利用视觉证据，再按组件和模板隔离训练测试。synthetic data 要覆盖未见组合、信息缺失和视觉冲突，验证必须依赖实际渲染内容。
