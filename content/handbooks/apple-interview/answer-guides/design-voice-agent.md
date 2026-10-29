---
id: design-voice-agent
kind: design
situation: ASR、推理、工具与 TTS 互相影响。
task: 设计可打断且可靠的语音流程。
approach: 状态机管理流式结果、取消与动作确认。
result: 语义成功、首响应和打断恢复均测。
---

## 可以这样回答

ASR、推理、工具与 TTS 互相影响。

语音 agent 要能在用户开口时停止播放，并从生成状态退回听取新输入，同时区分可取消查询和已发出的写操作。先定首包音频、打断后静音间隔的 SLO，再分配 ASR、LLM、TTS 预算；金额、药名等低置信槽位要确认，避免识别错误沿工具链放大。
