---
id: design-voice-agent
section: design
order: 18
level: S
title: 设计：语音 agent 的打断、端到端延迟、ASR 错误传播
quick: >-
  语音 agent 要能在用户开口时停止播放，并从生成状态退回听取新输入，同时区分可取消查询和已发出的写操作。先定首包音频、打断后静音间隔的 SLO，再分配
  ASR、LLM、TTS 预算；金额、药名等低置信槽位要确认，避免识别错误沿工具链放大。
tags:
  - Voice
  - Apple
  - Amazon
  - Latency
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Robust Speech Recognition via Large-Scale Weak Supervision
    url: 'https://arxiv.org/abs/2212.04356'
    type: primary
  - title: Introducing Apple Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Function calling
    url: 'https://platform.openai.com/docs/guides/function-calling'
    type: primary
---

## 题目描述

本题是手册归纳的系统设计练习。流量、数据量和具体 SLO 未给定时，请先列出可调整的假设，不把假设当成已披露事实。

### 场景与目标

设计一个可以实时听用户说话、生成回答并播放语音的助手，用户可以在播放过程中打断。语音识别可能产生会变化的中间文本。

### 需要满足的功能

- 接收音频流与会话状态，返回文本/音频回答，并处理停顿、改口和打断。
- 支持只读问答和需要外部操作的语音任务。
- 明确当前识别文本、已确认意图、在途工具及输出音频各自的有效范围。

### 约束与交付物

需要给出首包音频延迟、打断后的停播目标、识别 confidence 与工具授权要求。涉及金额、药名等关键内容时，错误识别不能未经必要确认直接变成外部写入。

请说明 scope 和 constraints、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

系统正在播报时，用户说“不是十二，是二十”，旧音频应停止，新一轮应采用修正内容；尚未发出的旧任务动作不能继续执行。

## 可以这样回答

我会先定义首包音频延迟和打断后的静音间隔，再设计能从「说」退回「听」的状态机。比如把「二十」听成「十二」，错误会进入工具参数并修改外部状态，所以金额、药名等高风险槽位要等稳定识别并确认后才执行。Apple Siri、Amazon Alexa / Bedrock 语音和 Google Assistant 都涉及这些问题。Whisper 论文讨论识别，完整产品还要处理状态机、延迟预算和错误传播。on-device 延迟见 `apple-siri-latency`；证据支持见 `apple-siri-grounded`；multimodal 时钟见 `design-multimodal-prod`。

四个态够讲：听、想、说、被打断。用户在 TTS 播放时说话：立刻停播、丢弃未发出的音频、取消或降级未完成的 LLM / 工具、把新 ASR 前缀接到当前会话。不要等这轮工具返回再听；那是电话客服最讨厌的「请稍候」死锁。

## 技术备查

## 解题思路与参考答案

我会先定义首包音频延迟和打断后的静音间隔，再设计能从「说」退回「听」的状态机。比如把「二十」听成「十二」，错误会进入工具参数并修改外部状态，所以金额、药名等高风险槽位要等稳定识别并确认后才执行。Apple Siri、Amazon Alexa / Bedrock 语音和 Google Assistant 都涉及这些问题。Whisper 论文讨论识别，完整产品还要处理状态机、延迟预算和错误传播。on-device 延迟见 `apple-siri-latency`；证据支持见 `apple-siri-grounded`；multimodal 时钟见 `design-multimodal-prod`。

## 会话怎样处理打断

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

## 拆开延迟并控制识别错误

粗算用户感知的 TTFA（听到第一段回复音频）：

$$
t_{\mathrm{TTFA}} \approx t_{\mathrm{endpt}} + t_{\mathrm{asr}} + t_{\mathrm{ttft}} + t_{\mathrm{tts}}.
$$

四项里任何一项的 p95 都能单独毁掉体验。流式 ASR 让 $t_{\mathrm{asr}}$ 变小，但实体替换常出现在最后几个词。投机：用部分假设先起 LLM，终稿不一致就停 TTS 改口。改口必须先停播，再来一句纠正，避免两个声音打架。

预算写法：先定 TTFA 和打断后静音间隔，再反推模型大小和是否上云。别在面试报美元单价；说 token 数、首包、设备电量。on-device small model 保首包，云端 large model 保难查询，切换要有口播，不要静默升级。

「二十」听成「十二」、药名、联系人、金额，是语音 agent 的一等事故。传播路径：错槽 → 错工具参数 → 外部状态被错误修改。缓解：

- 高风险槽位（金额、电话、地址、药）走 n-best + 口头回读 + 确认框；文本 UI 若存在，同时展示识别结果让用户改。
- 工具侧校验：通讯录模糊匹配、药名词典、金额范围。校验失败问一句，不要「智能纠正」成另一个实体。
- 日志把 ASR 假设和最终参数分开存，否则事故复盘分不清是识别错还是模型改槽。
- 评测不要用 BLEU。拆：唤醒后 TTFA、打断成功率、槽位错误率、任务成功、误唤醒、过度确认（用户嫌烦）。

失败模式：把 ASR 1-best 当真理写进 prompt；LLM 用 pre-training 知识「补」没听清的词；TTS 念出尚未确认的金额；打断后旧工具结果晚到，插进新一轮。内容安全对音频同样要同步轻量审核，见 `design-moderation`。

## 追问

**为什么不永远等 ASR 终稿再调 LLM？**
TTFA 会被终稿拖死。部分假设可起生成，终稿只锁高风险槽。
**打断时工具已经发出去了？**
只读丢弃；写入走 idempotency key 和补偿，不能假装没发生。
**n-best 会不会更慢？**
decoding 侧可以并行。确认只在低置信或高风险槽触发，不是每句话复读。
**和纯文本 chat 比多了什么 quality checks？**
时间轴、不可撤回的声波、识别不确定度。权限和预算仍要硬顶，见 `design-agent-budget`。
