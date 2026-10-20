---
id: apple-siri-grounded
section: apple
order: 2
level: S
title: Apple Siri：工具结果必须接地的回复，怎么设计生成和评测？
quick: "答案只能来自工具 / 检索结果，不许靠参数记忆补事实。语音还有长度预算。分别评测证据支持、正确性、语音可读性和拒答；证据支持检查关键事实能否在来源中定位。上下文变长时仍要可评，不能只看 BLEU。"
tags:
  - Apple
  - Siri
  - Grounding
  - RAG
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Siri Grounded Response Generation (1Point3Acres question bank)
    url: https://www.1point3acres.com/interview/problems/company/apple
    type: secondary
  - title: Introducing Apple Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
---

## 真题记录

- 公司：Apple
- 岗位：Siri / Apple Intelligence MLE
- 来源：一亩三分地 Apple 题库公开预览「Siri Grounded Response Generation」，约 60 分钟系统设计 / case。题面要点：回答中的事实必须由工具结果支持、控制幻觉、适应 voice 长度、上下文变长仍可评
- 最近记录标注到 2026-06

这题最容易答成「上个 RAG」。Siri 的约束是语音、工具、隐私、可评测四件同时成立。云端客服 检索增强生成（RAG） 的默认假设（长文本、可点引用、数据可随便上传）这里不全真。

## 有实际证据支持是契约，不是 输入提示里写一句

系统先跑工具（天气、日历、设备状态、可选的检索），得到结构化证据 $E$。生成条件是 $(q,E)$，解码侧要能指出答案跨度对应 $E$ 里哪一条。做不到就拒答或追问，而不是用预训练知识补。

实现分层：

1. 工具层负责权限和新鲜度。日历事件过期了就不能当证据。
2. 规划层决定还要不要再调工具。语音交互里多一跳就是多一次 TTS，要算延迟。
3. 生成层只在 $E$ 上解码。可用：constrained decoding（实体必须是 $E$ 里的 span）、引用标记、或独立 NLI 模型查是否 entail。
4. 口头层把经过证据核对的文字压到听得完的长度。压缩不能把限定词丢掉（「下午三点」变成「三点」会错）。

幻觉拦截和引用，国内手册里 `ali-hallucination-intercept`、`ali-rag-eval` 同构，但 Siri 多了语音预算和端侧数据不出设备。私有上下文（消息、邮件）优先 on-device foundation models，这是 Apple 公开技术叙述，面试里要能点到，不要设计成「全量上传云端再 RAG」。

## 评测：拆开，别只报一个分

题面点名 evaluable as context grows。我会拆：

- Grounding：人工或 NLI，答案关键命题能否在 $E$ 中定位。$E$ 为空时应拒答，拒答率单独记。
- Correctness：工具金标下的准确。和 grounding 分开：可以有实际证据支持但选错槽。
- Voice fitness：时长、是否可 TTS、是否去掉不可说的 URL / 表格。
- Context scaling：工具结果从 1 条涨到 50 条，有实际证据支持率和延迟的曲线。长上下文把证据淹没时，要检索 / 重排，不是把 JSON 全塞 输入提示（prompt）。

不要用 BLEU 当主指标。口头改写和金标书面句面差很大，BLEU 低也可能是好回答。

## 追问

- **工具错了怎么办？** 生成再忠实也是错的。监控工具层，不要用更大模型补救错误 API。
- **用户让你猜？** 语音里「你就说一个」不是授权幻觉。仍然拒答或给带不确定标记的短句，并留下再查工具的路径。
- **和 Apple Intelligence 的 on-device / Private Cloud Compute？** 证据和模型尽量留在设备或 PCC，设计里不要默认「日志拿去训下一版」。这是产品约束，不是加分口号。
