---
id: apple-multimodal
kind: design
situation: OCR 文本未必能表达空间与像素证据。
task: 选择可核查的视觉 grounding 表示。
approach: 按任务保留区域、文字与出处。
result: 引用区域真正支持结论，换布局仍有效。
---

## 可以这样回答

OCR 文本未必能表达空间与像素证据。

屏幕 grounding 要同时保留像素区域和 OCR 文本：点击、高亮依赖框或 mask，朗读、复制和填槽依赖文本 span。比如模型读出「下午三点」还要指向对应控件，两种输出必须共用能对齐的 id，避免说对内容却点错按钮。
