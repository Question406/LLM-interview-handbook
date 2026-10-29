---
id: apple-ondevice-agent
section: apple
order: 19
level: S
title: Apple：on-device agent，工具本地跑、写操作确认、离线怎么收？
quick: >-
  on-device agent 由模型输出结构化调用，再由 App 的 `Tool` 或系统 App Intent
  执行；发、删、付款等副作用要经过确认。离线时只暴露本地工具，宿主程序限制轮数、耗时和资源，工具失败也要按真实状态返回。
tags:
  - Apple
  - Agent
  - On-device
  - Tool Use
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Foundation Models framework
    url: 'https://developer.apple.com/documentation/foundationmodels'
    type: primary
  - title: Meet the Foundation Models framework (WWDC25)
    url: 'https://developer.apple.com/videos/play/wwdc2025/286/'
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
---

on-device 可以做 agent：模型负责决定调用什么工具，执行仍交给 App 或系统，并由宿主限制预算、权限和确认。比如查本地日历可以自动执行，发消息则要确认；没网时工具列表也应只留下本地能力。

2025 年 Foundation Models 框架公开了 Swift API、约 3B on-device 模型、guided generation 和 `Tool` 协议。WWDC 说明框架能处理串并行调用图，系统级跨 App 能力仍走 App Intent。它与把 MCP 接到 Siri 的设计不同，on-device 模型的 capability limits 见 `apple-foundation-models`。

## 执行域：本地、确认、可离线

我会先说明执行位置、写操作确认和离线行为：

1. 谁执行。自定义 `Tool` 在本进程跑：查本地数据库、MapKit、当前 App 状态。系统能力走 App Intent。模型不出网替你打 HTTP，除非工具自己请求网络。PCC 是更大语言模型，不是默认工具运行时。
2. 副作用。只读（搜本地邮件、列日历）可自动。发消息、删文件、付款、改系统设置必须确认或系统权限框。确认是 UI 契约，不是 prompt 里写「请谨慎」。这和 `apple-siri-grounded` 同一句：状态以系统记录为准。
3. 离线。没网时工具列表要裁成本地子集。天气、网页、PCC 从 schema 中移除，而不是调失败后再让模型编。公开叙事里 on-device 就要能在私有上下文上工作。

预算写在宿主，不写在 system prompt：

```python
def run_local_agent(step, *, max_rounds=4, max_wall_s=8):
    t0 = time.time()
    for r in range(max_rounds):
        if time.time() - t0 > max_wall_s:
            return {"status": "budget"}
        out = step(r)
        if out.get("needs_confirm") or out.get("done"):
            return out
    return {"status": "max_round"}
```

手机还有热和电。连续多轮工具加生成会降频，见 `apple-afm-eval`。`max_rounds` 取 4 量级比云端 20 更像 Siri。

## 失败、注入、观测

工具结果是不可信输入：网页、邮件正文可以带「忽略之前的指令」。进下一轮前当数据截断，不要和系统策略糊成一段。写操作失败要结构化回给模型（权限拒绝 / 不存在 / 可重试），禁止把超时说成「已经发了」。

观测：每步记录 tool 名、参数哈希、是否确认、是否离线降级。用户隐私：完整邮件不要进长期日志，见 `apple-diff-privacy`。评测拆：任务成功、误调（不该发却发）、拒答、离线成功率、确认后的取消率。不要报「对话自然」。

设计时要分清 `Tool` 和 App Intent，并根据联网状态裁剪云端搜索与 PCC。更大的 server 模型也无法补足本地权限，权限不足需要由系统流程处理。

和视觉 / 语音同样需要检查证据：工具证据 $E$ 为空就问，不靠参数记忆补日历，见 `apple-siri-grounded`。延迟上多一跳工具就是多一次 TTS 等待，见 `apple-siri-latency`。

## 追问

**并行 tool on-device 能做吗？**
框架公开说能处理并行和串行图。只读可并行；有依赖（先查再写）必须串。写默认不自动重试。
**为什么还要确认框？**
3B 会误调。确认流程由产品负责，需要防住误调用造成的副作用。
**和 PCC 怎么分工？**
难推理、long context 上云；工具副作用仍在本地落地。不要把发件箱 API 暴露给云端会话。
**没实现的工具？**
schema 里不出现。模型看见「能订餐厅」却 404，会 hallucination 成功。
