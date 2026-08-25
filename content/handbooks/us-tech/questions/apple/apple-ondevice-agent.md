---
id: apple-ondevice-agent
section: apple
order: 19
level: S
title: Apple：端侧 agent，工具本地跑、写操作确认、离线怎么收？
quick: >-
  工具在 App / 系统 Intent 里执行，模型只出结构化调用。写、发、删要确认。离线只保留本地工具，不要假装能搜网。步数、墙钟、热是硬顶。Foundation
  Models 的 Tool 协议是公开面，不是云端 ReAct 搬到手机。
tags:
  - Apple
  - Agent
  - On-device
  - Tool Use
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Foundation Models framework
    url: https://developer.apple.com/documentation/foundationmodels
    type: primary
  - title: Meet the Foundation Models framework (WWDC25)
    url: https://developer.apple.com/videos/play/wwdc2025/286/
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
---

Apple Intelligence / 框架岗会问「端上能不能当 agent」。公开层 2025 把 Foundation Models 框架做成 Swift API：约 3B 端侧模型、guided generation、`Tool` 协议。WWDC 写明模型可以自主决定调你在 App 里实现的工具，框架处理串并行调用图。系统级跨 App 仍走 App Intent，不是把 MCP 接到 Siri。端侧模型公开 **不是开放世界 chatbot**，见 `apple-foundation-models`。不是逐字真题。

## 执行域：本地、确认、可离线

我会先画三列，避免答成云端 Bedrock Agents：

1. **谁执行。** 自定义 `Tool` 在本进程跑：查本地数据库、MapKit、当前 App 状态。系统能力走 App Intent。模型不出网替你打 HTTP，除非工具自己请求网络。PCC 是更大语言模型，不是默认工具运行时。
2. **副作用。** 只读（搜本地邮件、列日历）可自动。发消息、删文件、付款、改系统设置必须确认或系统权限框。确认是 UI 契约，不是 prompt 里写「请谨慎」。这和 `apple-siri-grounded` 同一句：状态以系统记录为准。
3. **离线。** 没网时工具列表要裁成本地子集。天气、网页、PCC 从 schema 里拿掉，而不是调失败后再让模型编。公开叙事里端侧就要能在私有上下文上工作。

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

错法：把云端搜索当端侧默认工具；`Tool` 和 App Intent 说成同一个 API；离线还去调 PCC；用更大 server 模型补本地权限不足。权限不足是系统设计，不是能力问题。

和视觉 / 语音同一套接地：工具证据 $E$ 为空就问，不靠参数记忆补日历，见 `apple-siri-grounded`。延迟上多一跳工具就是多一次 TTS 等待，见 `apple-siri-latency`。

## 追问

- **并行 tool 端上能做吗？** 框架公开说能处理并行和串行图。只读可并行；有依赖（先查再写）必须串。写默认不自动重试。
- **为什么还要确认框？** 3B 会误调。确认是产品所有权，Bar 在失败模式，不在少一次点击。
- **和 PCC 怎么分工？** 难推理、长上下文上云；工具副作用仍在本地落地。不要把发件箱 API 暴露给云端会话。
- **没实现的工具？** schema 里不出现。模型看见「能订餐厅」却 404，会幻觉成功。
