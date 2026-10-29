---
id: dt-frontier-ctx-mm
kind: design
situation: 长输入和 multimodal 得分含多个因素。
task: 确认任务要求模型用到了哪种证据。
approach: 控制长度、位置、语言与视觉信息做对照。
result: 按 evaluation slice 报告收益，不能只看总上下文容量。
---

## 可以这样回答

长输入和 multimodal 得分含多个因素。

long context 要看模型能不能在长输入里找对信息，「支持 1M」只说明收得下。MRCR v2 在长文里放多个相似目标，要求按指令取 backpointer 定那段，同一模型在 128k 和 1M 下可能差很多。MMMU-Pro 尽量去掉不看图也能答对的题，multilingual 榜要先查题目是不是英语翻译来的。
