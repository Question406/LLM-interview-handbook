---
id: apple-audio-llm
section: apple
order: 18
level: S
title: Apple：语音进 LLM，流式 ASR 文本还是音频 token？
quick: >-
  我会让 ASR 文本负责工具参数和事实核对，写操作等最终识别稳定再执行。音频 token 能保留韵律、叠音等信息，但前缀更长、静态 shape
  和证据对齐更难，适合在需要这些信息时补一条短窗口通道。
tags:
  - Apple
  - Speech
  - Streaming ASR
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: >-
      Omni-Router — Sharing Routing Decisions in Sparse MoE for Speech
      Recognition
    url: 'https://machinelearning.apple.com/research/omni-router'
    type: primary
  - title: Bring advanced speech-to-text to your app with SpeechAnalyzer (WWDC25)
    url: 'https://developer.apple.com/videos/play/wwdc2025/277/'
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)
    url: 'https://arxiv.org/abs/2212.04356'
    type: secondary
---

面向 Siri 这类 on-device 任务，我会优先让流式 ASR 产出文本，再交给 LLM 和工具；涉及日历、身份或写操作，等最终 hypothesis 稳定再执行。比如 partial 里的人名或数字后来被改写，模型若已调工具或 TTS 已读出去，撤回成本很高。partial 可以提前判断意图、预取只读工具。

这是设计选择，公开材料能支持的是 Apple 重视流式 ASR：Omni-router 提供流式检查点，WWDC25 的 SpeechAnalyzer 在设备上转写，已用于备忘录等应用；foundation model 仍公开为语言核心加工具。Whisper 编码器、codec tokenizer 和音频离散 token 是业界对照，不能据此编造 AFM 内部音频架构。

记波形为 $x_{1:t}$。文本路线先出 partial $w_{\le t}$，端点后出最终 $w$，LLM 条件为 $(w, E)$，其中 $E$ 是工具证据。文本 token 容易按静态档位处理，工具槽、TTS 和证据核对也都能以字符串衔接。

音频路线把波形变成离散单元或连续帧 $a_{1:T_a}$，$T_a$ 大约每秒 25–75。它保留韵律、笑声和多人叠音，也能帮助处理 ASR 易错的专名，但要另训音频 embedding，ANE 预分配 $T_a^{\max}$，长短变化都需要 padding。闲聊可以用部分音频，实用方案常是短窗口音频加 ASR 双通道。

评测也要沿两条路径拆。ASR 的错词会变成 LLM 的输入事实，所以 WER 之外还测下游槽位准确率，数字、人名、App 名单独统计，并记录 partial 到 final 改写率。音频 token 没有直接的字面 span，“用户说下午三点”难以映射回波形索引，工具参数最终仍要解成文本。原音频比转写更敏感，设计上默认留在设备，也不当基础模型训练数据。

首包音频的延迟可以拆成：

$$
T_{\mathrm{first\_audio}} \approx T_{\mathrm{VAD}}+T_{\mathrm{ASR,partial}}+T_{\mathrm{LLM,TTFT}}+T_{\mathrm{TTS,first}}.
$$

音频 LLM 把 $T_{\mathrm{ASR}}$ 换成 $T_{\mathrm{encode}}(T_a)$，但 $T_a$ 随说话变长，静态图按最坏窗口运行，短指令也会付长前缀成本。Whisper 式 30 秒块不能直接当 Siri 流式交互。

如果做双通道，我会用 ASR 文本驱动工具和核对事实，短窗口音频只补情绪、叠音、专名分类，不独立驱动写操作；在 CPU 融合，避免给 ANE 再加一条变长音频图。

## 追问

**为什么工具不直接吃音频 token？**
系统 API 需要文本和 App Intent 参数。音频改善理解，最终仍需满足字段和类型 schema。

**识别一直改词怎么办？**
只读预取可以并行，写操作绑定 final。UI 可以显示“正在听”，不能提前声称消息已发出。

**离线能用吗？**
SpeechAnalyzer 公开支持 on-device 转写，这条链路比依赖上云的音频 LLM 更适合离线。

**和视觉 token 有什么相似处？**
两者都占 $S_{\max}$，但视觉是一帧网格，音频会随时间增长，静态图里更要避免动态 `cat`。

相关：`apple-siri-latency`、`apple-ane`、`apple-siri-grounded`、`apple-vision-edge`、`apple-personalize`
