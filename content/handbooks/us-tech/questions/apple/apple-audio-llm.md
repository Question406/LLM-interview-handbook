---
id: apple-audio-llm
section: apple
order: 18
level: S
title: Apple：语音进 LLM，流式 ASR 文本还是音频 token？
quick: >-
  Siri 主路径仍是流式 ASR 出文本再进 LLM：ANE 友好、工具槽是字符串、事实可等最终 hypothesis。音频 token 保留韵律和重叠说话，但前缀长、静态
  shape 难、不好接地。闲聊可以部分上音频；日历、身份、写操作必须等 ASR 稳定。
tags:
  - Apple
  - Speech
  - Streaming ASR
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Omni-Router — Sharing Routing Decisions in Sparse MoE for Speech Recognition
    url: https://machinelearning.apple.com/research/omni-router
    type: primary
  - title: Bring advanced speech-to-text to your app with SpeechAnalyzer (WWDC25)
    url: https://developer.apple.com/videos/play/wwdc2025/277/
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)
    url: https://arxiv.org/abs/2212.04356
    type: secondary
---

Siri / 端侧语音岗容易把题答成「上个音频 LLM」。公开层 Apple 把流式 ASR 做成一等公民：研究侧有 Omni-router 的流式检查点，系统侧 WWDC25 的 SpeechAnalyzer 在设备上转写并已用于备忘录一类应用。Foundation model 公开叙事仍是语言核心加工具，语音链路的延迟拆解见 `apple-siri-latency`。音频离散 token 是业界对照（Whisper 编码器、codec tokenizer），不要说成 AFM 内部架构。

## 两条进 LLM 的契约

记波形 $x_{1:t}$。两条路：

- ASR 文本。流式编码器出 partial 文本 $w_{\le t}$，端点后再出最终 $w$。LLM 条件是 $(w, E)$，$E$ 是工具证据。形状按文本 token，和 `apple-ane` 的静态档位一致。工具槽、TTS、接地全是字符串，见 `apple-siri-grounded`。
- 音频 token。波形量化成离散单元或连续帧 $a_{1:T_a}$，$T_a$ 大约每秒 25–75。前缀长，韵律、笑声、重叠说话还在。LLM 要另训音频嵌入。ANE 必须预分配 $T_a^{\max}$，说话长短一变就要 pad，和视觉档位同一痛，见 `apple-vision-edge`。

Siri 产品约束偏向第一条。日历、发消息、读验证码，错一个数字的代价高于少听一点情绪。Partial ASR 可以提前做意图分类或预取工具，事实槽位等最终 hypothesis，否则 TTS 读出去撤回成本极高，见 `apple-siri-latency`。

第二条的正当场景：副语言（生气 / 犹豫）、音乐、多人叠音、ASR 必错的专名用声学记忆。即使做，也常常是短窗口音频 token 加 ASR 文本双通道，而不是丢掉转写。

## 错误会沿哪条管道放大

ASR 路径：词错误变成 LLM 的「事实」。评测要拆 WER 和下游槽准确，不要只报 ASR。数字、人名、App 名单独切。流式还要报 partial 到 final 的改写率：改写太猛，LLM 已经按旧词调了工具。

音频 token 路径：没有字面 span，引用「用户说了下午三点」对不回波形索引。工具 API 仍要文本参数，等于最后还得解码一层。隐私上，原音频比转写更敏感，默认不出设备，更不能当基础模型训练数据，见 `apple-personalize`。

延迟账：

$$
T_{\mathrm{first\_audio}} \approx T_{\mathrm{VAD}}+T_{\mathrm{ASR,partial}}+T_{\mathrm{LLM,TTFT}}+T_{\mathrm{TTS,first}}.
$$

音频 LLM 把 $T_{\mathrm{ASR}}$ 换成 $T_{\mathrm{encode}}(T_a)$。$T_a$ 随说话变长，静态图只能按最坏窗口跑，短指令也会付长前缀税。Whisper 式 30 秒块不是 Siri 交互；Omni-router 公开提供流式权重，面试用它当「Apple 认真做流式 ASR」的证据，不编端到端音频 AFM。

产品上我通常双通道：ASR 文本进工具和接地；短窗口音频 token 只给「情绪 / 叠音 / 专名」分类头，不单独驱动写操作。融合在 CPU 上做，避免给 ANE 再加一条变长音频图。

错法：一开口就端到端语音 LLM；partial 文本直接写日历；把非流式 Whisper 块模型当成手机听写。

## 追问

- **为什么工具不吃音频 token？** 系统 API 是文本和 App Intent 参数。音频条件生成补的是理解，不是替代 schema。
- **流式 ASR 一直改词怎么办？** 只读预取可并行；写操作绑 final。UI 上可以显示「正在听」，不能显示已经发出去的消息。
- **离线？** SpeechAnalyzer 公开就是端上转写。没网时这条比要上云的音频 LLM 更像 Apple。
- **和视觉 token 同构吗？** 都占 $S_{\max}$。视觉一次一帧网格；音频随时间涨。语音更不能动态 `cat`，见 `apple-ane`。
