---
id: xai-realtime
section: xai
order: 18
level: A
title: xAI：低延迟语音 / 对话（公开层）怎么拆预算？
quick: >-
  公开 Voice Agent 走 WebSocket，服务端 VAD，宣传亚秒级轮次。预算拆成端点、上行音频、模型 TTFT、首包下行。打断要停 TTS
  并丢掉未播完的词。工具在说话中途会拉长静音，只读可并行，写要确认。不编车舱或未文档化的端到端语音模型。
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

## 题怎么来的

xAI 应用岗会问语音怎么做到「像打电话」。公开层是 Voice / Speech-to-Speech API：WebSocket、`session.update` 配声音和 `turn_detection`（文档示例是 `server_vad`）、工具列表可含 `web_search`。宣传是亚秒级轮次和全双工。没有公开毫秒表或车舱声学细节。本题只拆公开预算和失败模式。Siri 端侧对照见 `apple-siri-latency`，不要把 iPhone ANE 故事搬过来。`realInterview: false`。

## 时钟要切开

用户停口到喇叭出声，至少四段：

$$
T_{\mathrm{first\_audio}} \approx T_{\mathrm{VAD}}+T_{\mathrm{uplink}}+T_{\mathrm{model,TTFT}}+T_{\mathrm{tts,first}}.
$$

- VAD / 端点。停太早截句，停太晚直接加几百毫秒。这是产品阈值。
- 上行。网络抖动在尾巴上。SLO 看 p99，不看平均。
- 模型。语音进模型可以是 ASR 文本或语音到语音；公开没钉死内部是否离散音频 token。面试讲合同：首包音频才是体感，整段结束是工具契约。
- TTS 首包。流式播；完整波形结束用户已经在听。

打断：用户插话要停播、丢未播出的词、取消未完成的工具（只读可丢，写要看幂等）。半句话当指令会误调搜索。搜索工具在语音里特别危险：一次 `web_search` 可能比 VAD 还长，用户听见长静音。只读搜索可在「我查一下」的垫话后跑；写操作必须确认，见 `xai-tool-use`。

工具和语音同一条 session。文档允许 `web_search` / `x_search` / 自定义 function。自定义函数仍是你本地执行，语音只是通道。失败不要用嘴说「已经办了」，见 `xai-agent-loop`。

## 观测和评测

分别打点：VAD 触发、首 token / 首音频、工具开始结束、TTS 首包、用户打断。混成一个「语音延迟」无法排障。限流见 `xai-rate-limiter`：突发说话会打满连接数，要排队或拒新会话，不要在同一 socket 里叠两个 agent。

评测：任务是否听懂（槽准确）、是否该搜却没搜、打断后是否停播、写操作误触发率。不要用 Arena 文风评语音，见 `xai-lmarena`。时效问题仍走搜索工具，见 `xai-search-agent`。

错法：编一个未公开的端到端音频 MoE；把亚秒宣传当成 p99 SLA；工具超时还在播「已经帮你订好了」。公开兼容 OpenAI Realtime 的说法以文档为准，面试以事件名和预算切分为主，不背 SDK 方法。

语音会话的配额按连接数和分钟计，和文本 RPM 不是同一道门。

## 追问

- **为什么不把所有工具在开口前跑完？** 有的槽位要听完整句。可以预取只读，写绑最终 turn。
- **静音是模型慢还是在搜？** 日志要标 tool span。没有 span 就不要猜是 GPU。
- **多语言？** 公开宣传多语种声音。评测按 locale 切片，不要只测英文短句。
- **和文本聊天同一套工具循环吗？** 合同一样：schema、确认、预算。语音只是更不能忍受长静音。
