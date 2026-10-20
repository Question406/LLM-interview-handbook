---
id: design-voice-agent
section: design
order: 18
level: S
title: 设计：语音 agent 的打断、端到端延迟、ASR 错误传播
quick: >-
  端到端不是「ASR 加 LLM 加 TTS」三个 p95 相加那么简单。用户开口要能打断播放；槽位错误会顺着工具链放大。
  状态机从听到说必须可退回。首包音频和确认框比完整正确率更先定 SLO。
tags:
  - Voice
  - Apple
  - Amazon
  - Latency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Robust Speech Recognition via Large-Scale Weak Supervision
    url: https://arxiv.org/abs/2212.04356
    type: primary
  - title: Introducing Apple Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Function calling
    url: https://platform.openai.com/docs/guides/function-calling
    type: primary
---

Apple Siri、Amazon Alexa / Bedrock 语音、Google Assistant 都会问 barge-in 和「听错一个药名之后怎么办」。Whisper 论文给的是识别；白板要的是状态机、延迟预算、错误如何进工具。端侧延迟专项见 `apple-siri-latency`；有实际证据支持见 `apple-siri-grounded`；多模态时钟见 `design-multimodal-prod`。

## 打断是状态机，不是把麦克风一直打开

四个态够讲：听、想、说、被打断。用户在 TTS 播放时说话：立刻停播、丢弃未发出的音频、取消或降级未完成的 LLM / 工具、把新 ASR 前缀接到当前会话。不要等这轮工具返回再听；那是电话客服最讨厌的「请稍候」死锁。

端点检测（endpointing）和打断是一对：太敏，用户换气被当成说完，LLM 抢跑；太钝，首包音频晚半拍。流式 ASR 部分假设可以先出词，但开工具要等稳定的槽位，或对低置信实体口头确认。

```python
class VoiceLoop:
    def on_barge_in(self):
        self.tts.cancel()
        self.llm.cancel_if_safe()  # 无副作用的生成可丢；已发出的支付不可丢
        self.state = "listen"
```

已发出的不可逆工具不能因为打断而自动撤回，要走补偿或确认，见 `design-tool-prod`。只读查询可以丢。

## 延迟怎么拆，别只报一个「大约一秒」

粗算用户感知的 TTFA（听到第一段回复音频）：

$$
t_{\mathrm{TTFA}} \approx t_{\mathrm{endpt}} + t_{\mathrm{asr}} + t_{\mathrm{ttft}} + t_{\mathrm{tts}}.
$$

四项里任何一项的 p95 都能单独毁掉体验。流式 ASR 让 $t_{\mathrm{asr}}$ 变小，但实体替换常出现在最后几个词。投机：用部分假设先起 LLM，终稿不一致就停 TTS 改口。改口必须先停播，再来一句纠正，避免两个声音打架。

预算写法：先定 TTFA 和打断后静音间隔，再反推模型大小和是否上云。别在面试报美元单价；说 token 数、首包、设备电量。端侧小模型保首包，云端大模型保难查询，切换要有口播，不要静默升级。

## ASR 错误会沿工具放大

「二十」听成「十二」、药名、联系人、金额，是语音 agent 的一等事故。传播路径：错槽 → 错工具参数 → 外部状态被错误修改。缓解：

- 高风险槽位（金额、电话、地址、药）走 n-best + 口头回读 + 确认框；文本 UI 若存在，同时展示识别结果让用户改。
- 工具侧校验：通讯录模糊匹配、药名词典、金额范围。校验失败问一句，不要「智能纠正」成另一个实体。
- 日志把 ASR 假设和最终参数分开存，否则事故复盘分不清是识别错还是模型改槽。
- 评测不要用 BLEU。拆：唤醒后 TTFA、打断成功率、槽位错误率、任务成功、误唤醒、过度确认（用户嫌烦）。

失败模式：把 ASR 1-best 当真理写进 输入提示（prompt）；LLM 用预训练知识「补」没听清的词；TTS 念出尚未确认的金额；打断后旧工具结果晚到，插进新一轮。内容安全对音频同样要同步轻量审核，见 `design-moderation`。

## 追问

- **为什么不永远等 ASR 终稿再调 LLM？** TTFA 会被终稿拖死。部分假设可起生成，终稿只锁高风险槽。
- **打断时工具已经发出去了？** 只读丢弃；写入走幂等键和补偿，不能假装没发生。
- **n-best 会不会更慢？** 解码侧可以并行。确认只在低置信或高风险槽触发，不是每句话复读。
- **和纯文本 chat 比多了什么闸门？** 时间轴、不可撤回的声波、识别不确定度。权限和预算仍要硬顶，见 `design-agent-budget`。
