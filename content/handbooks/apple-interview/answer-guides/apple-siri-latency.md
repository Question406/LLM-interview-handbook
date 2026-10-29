---
id: apple-siri-latency
kind: design
situation: 语音助手多阶段等待会累积。
task: 分配可测的端到端延迟预算。
approach: 识别关键路径，比较流式输出与完整结果等待。
result: 首响应、最终完成及误打断质量一起测。
---

## 可以这样回答

语音助手多阶段等待会累积。

我会分段记录端点检测、流式 ASR、工具与 LLM 首句、TTS 首包，再决定哪些阶段可以重叠。改写和已确认的长摘要可流式播报，时间、金额、身份和工具事实要等证据齐全再读；公开 on-device 约 0.6 ms/prompt-token、30 token/s，不能直接当整条语音链路的延迟。
