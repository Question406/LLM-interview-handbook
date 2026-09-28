---
id: apple-siri-latency
section: apple
order: 6
level: A
title: Apple：Siri 语音链路延迟预算，流式 TTS vs 等完整答案？
quick: >-
  把 p95 拆成端点检测、流式 ASR、LLM 首 token、TTS 首包音频。公开端侧大约 0.6 ms/prompt-token 和 30
  token/s。闲聊 / 长摘要可以流式开口；涉及时间、身份、工具结果的事实要等接地完成再读，否则撤回成本极高。
tags:
  - Apple
  - Siri
  - Latency
  - TTS
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Apple Intelligence Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-intelligence-foundation-language-models
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

Exponent 写 Apple MLE 会盯 latency 和 on-device 限制；Siri 岗把同一约束放到语音管道上。公开材料没有一份「Siri 内部毫秒表」可以背，现场用自己拆的预算和 Apple 已经公开的生成速度，比编造几十毫秒的 SLA 安全。接地契约见 `apple-siri-grounded`，量化 / ANE 见 `apple-ondevice-quant`、`apple-ane`。

## 链路按阶段拆，不要只报一个「模型很快」

用户停口到喇叭出声，至少四段，串行里有重叠：

1. 端点 / VAD。停得太早会截句，停得太晚直接加几百毫秒。这是产品阈值，不是 transformer 超参。
2. 流式 ASR。部分假设可以在用户还在说时就往下送。最终 hypothesis 在端点后才稳定。NLU / LLM 若吃 partial，后面要能修正。
3. 规划 + 模型。工具（日历、消息、本地检索）和生成。端侧 AFM 公开数字：iPhone 15 Pro 上大约 0.6 ms 每个 prompt token 的首 token 路径、约 30 token/s 的生成（投机解码之前）。Prompt 300 token 的 prefill 大约 180 ms 量级，还不含工具。
4. TTS。关心的是首包音频，不是整句波形结束。神经网络 TTS 可以按音素 / 词片流式。

白板给一条 p95 例子（这是面试算法，不是泄密）：端点 250 ms，ASR final 150 ms，工具 200 ms，LLM 首句 300 ms，TTS 热身 150 ms，加起来已经过秒。要压到「对话还能接上」，必须让 3 和 4 与 2 重叠，并且工具能跳过。平均延迟没意义，语音看的是尾部和下一次抢话。

30 token/s 大约每秒两三个英文词，和语速同量级。所以只要首句 token 到得快，流式 TTS 能咬住；瓶颈通常是 prefill、工具和「不敢开口」。采样还要便宜，见 `apple-topk-sample`：端上偏小 $k$、低温度，既稳又省。

## 什么时候流，什么时候等

流式 TTS：模型一边 decode 一边把已提交的词送进 vocoder。用户更早听到声音，但读出去的词几乎不能改。

我会按命题风险分闸：

- 可以流：改写、摘要、头脑风暴、已经接地且槽位不再变的长回答。策略：先生成并提交第一句（或到第一个句号），TTS 开工；后面 token 继续补。采样偏贪心，减少中途改口。
- 必须等：时间、金额、人名、开关设备、工具尚未返回。`apple-siri-grounded` 的契约是答案来自证据 $E$。$E$ 不齐就开口，等于把幻觉读进耳朵。日历「三点」和「下午三点」差一个限定词，流式切句会把限定词留在第二包，第一包已经错了。工具错了也不能靠更大模型补，监控要打在工具层。
- 混合：先播一句无损的过渡（「我查一下日历」），工具并行，结果到了再读事实。过渡句是产品文案，不要让模型自由发挥出另一个事实。

投机解码能抬 token/s，但对语音是双刃：拒绝草稿时若 TTS 已经读了草稿前缀，就要停播或补丁，体验比屏上删 token 差得多。面试里说「语音通路默认不用未验证的草稿」比「我们上了 speculative」加分。

## 评测不要只看 WER

离线：工具金标下的首包音频时间、完整正确率、接地率、打断后的恢复。把「快但读错日期」单列成事故，不要和 BLEU 平均。长上下文工具结果从 1 条涨到 50 条，看的是首包是否仍稳，这和 `apple-siri-grounded` 的 context scaling 是同一条曲线。线上再看打断率、用户重说率和「你说错了」类反馈，不要只报离线 WER。

设备侧还要报功耗和热。30 token/s 是瞬时能力，连续对话会降频。设计里留「短答 adapter / 长答才上 PCC」的分支，PCC 的 RTT 必须进 p95，不能假装和本地一样。私有上下文怎么切见 `apple-personalize`。

## 追问

- **用户抢话怎么办？** 停 TTS、作废未提交 token、ASR 新片段当新 turn。KV cache 回滚到打断前的前缀，不要在脏续写上接着说。
- **为什么不把整段 LLM 答完再 TTS？** 长摘要会让静音超过一轮对话。等完整答案只留给高风险槽位。
- **流式和温度？** 流式一旦开口，多样性的代价是不可撤回。语音默认低 $T$、小 $k$。
- **端上 3B vs PCC 大模型？** 本地首 token 更稳；PCC 质量高但多一跳网络。路由规则要写进设计：隐私敏感且短的留本地。p95 要按这条路由分别报，不要混成一个平均数。
