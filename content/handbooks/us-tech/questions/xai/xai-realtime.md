---
id: xai-realtime
section: xai
order: 18
level: A
title: xAI：低延迟语音 / 对话（公开层）怎么拆预算？
quick: "我会把首包音频延迟拆成 VAD 端点、上行、模型 TTFT 和下行 TTS 首包，分别看尾延迟。公开 Voice Agent 使用 WebSocket 和服务端 VAD，亚秒级是宣传口径；打断要停播并丢弃未播词，工具调用单独计时，只读可预取，写操作仍需确认。"
tags:
  - xAI
  - Voice
  - Latency
  - Realtime
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: xAI Voice API
    url: https://docs.x.ai/developers/model-capabilities/audio/voice
    type: primary
  - title: Grok Voice Agent API
    url: https://x.ai/news/grok-voice-agent-api
    type: primary
  - title: xAI voice agent
    url: https://docs.x.ai/developers/model-capabilities/audio/voice-agent
    type: primary
  - title: xAI function calling
    url: https://docs.x.ai/docs/guides/function-calling
    type: secondary
---

我会把用户停口到听见首包音频的时间拆开测，再单独处理打断和工具等待。例如长静音可能是 VAD 端点太晚，也可能是搜索还没返回，不能都归到模型。公开 Voice / Speech-to-Speech API 走 WebSocket，用 `session.update` 配声音与 `turn_detection`，示例为 `server_vad`，工具可含 `web_search`；亚秒级轮次、全双工属于公开宣传，没有完整毫秒表或车舱声学细节。Siri 端侧对照见 `apple-siri-latency`，iPhone ANE 细节不能直接套用。

## 首包音频的时间花在哪里

用户停口到喇叭出声，至少四段：

$$
T_{\mathrm{first\_audio}} \approx T_{\mathrm{VAD}}+T_{\mathrm{uplink}}+T_{\mathrm{model,TTFT}}+T_{\mathrm{tts,first}}.
$$

- VAD / 端点。停太早截句，停太晚直接加几百毫秒。这是产品阈值。
- 上行。网络抖动在尾巴上。SLO 看 p99，不看平均。
- 模型。语音进模型可以是 ASR 文本或语音到语音；公开材料没有明确说明内部是否离散音频 token。面试讲合同：首包音频才是体感，整段结束是工具契约。
- TTS 首包。流式播；完整波形结束用户已经在听。

用户插话时，要停止播放、丢弃没播出的词，并取消尚未完成的工具。只读结果可以丢弃，已发出的写入要按幂等状态处理。半句话当指令会误调搜索。搜索工具在语音里特别危险：一次 `web_search` 可能比 VAD 还长，用户听见长静音。只读搜索可在「我查一下」的垫话后跑；写操作必须确认，见 `xai-tool-use`。

工具和语音同一条 session。文档允许 `web_search` / `x_search` / 自定义 function。自定义函数仍是你本地执行，语音只是通道。失败不要用嘴说「已经办了」，见 `xai-agent-loop`。

## 观测和评测

我会分别记录 VAD 触发、首 token 或首音频、工具起止、TTS 首包和用户打断。这样能看出是哪一段拖慢，只有一个总延迟无法排障。限流见 `xai-rate-limiter`：突发说话会打满连接数，要排队或拒新会话，不要在同一 socket 里叠两个 agent。

评测：任务是否听懂（槽准确）、是否该搜却没搜、打断后是否停播、写操作误触发率。不要用 Arena 文风评语音，见 `xai-lmarena`。时效问题仍走搜索工具，见 `xai-search-agent`。

常见误区是：编一个未公开的端到端音频 MoE；把亚秒宣传当成 p99 SLA；工具超时还在播「已经帮你订好了」。公开兼容 OpenAI Realtime 的说法以文档为准，面试以事件名和预算切分为主，不背 SDK 方法。

语音会话的配额按连接数和分钟计，和文本 RPM 不是同一道门。

## 追问

**为什么不把所有工具在开口前跑完？**
有的槽位要听完整句。可以预取只读，写绑最终 turn。

**静音是模型慢还是在搜？**
日志要标 tool span。没有 span 就不要猜是 GPU。

**多语言？**
公开宣传多语种声音。评测按 locale 切片，不要只测英文短句。

**和文本聊天同一套工具循环吗？**
调用约定一样：schema、确认和预算。语音只是更不能忍受长静音。

本卡依据公开材料整理，标记为 `realInterview: false`。
