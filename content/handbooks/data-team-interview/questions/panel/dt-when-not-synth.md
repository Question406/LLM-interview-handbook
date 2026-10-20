---
id: dt-when-not-synth
section: panel
order: 9
level: A
title: Panel：什么时候不要上合成数据？
quick: "没有独立验证手段、需要真实世界长尾、评测与生成器过于相似，或已经多代回流时，应先停下合成。合成适合补充能验证的任务覆盖；其他缺口可以用人工种子、许可采集或改进评测来解决。"
companies:
  - apple
tags:
  - Apple
  - Synthetic Data
  - Data Quality
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Curse of Recursion / Model Collapse
    url: https://arxiv.org/abs/2305.17493
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Self-Instruct
    url: https://arxiv.org/abs/2212.10560
    type: primary
---

先问：「生成结果要靠什么独立验证？」有可靠的执行检查、标准答案或人工核验，才开始设计合成流程，见 `dt-synth-reasoning`、`dt-synth-tool-mm`。答不出来就走人写、许可集或改评测。

不这么选的理由：评委在听你会不会停。任何缺口都回一句「合成」，这题就砸了。再变出一些看起来像的文本，不算覆盖。Director 更吃「我拒绝合成」的理由，只要后面有替代。

## 先问门在哪

合成值得做的前提，是有独立于生成器的可靠检查：执行测试、符号验证、环境状态，或人工对照许可真实来源抽查。AFM 在 mid 写了「verified for correctness wherever possible」，图表用代码渲染自带表，工具用执行环境。这些是绿灯。

红灯我直接停：

- 主观文风、幽默、某 locale 的自然程度。教师会写成翻译腔。AFM 多语评测不用翻译题，就是这个原因。用人写种子，合成最多扩题面。
- 真实长尾几何。罕见海报版式、手写污损、某国地址格式。纯合成会偏干净。真数据不够就去许可采集，合成当补，不当主源。
- 生成器和 judge 同族。合成题 + 合成评测 + 同系 奖励模型（RM），三重虚高，见 `dt-judge-bias`、`dt-contamination`。
- 已经回流多代。错误指纹变密，对照人类熵在掉，见 `dt-self-improve`。
- 来源本身不合法。用用户原文当种子再「改写」，不是合成，是绕过隐私，见 `dt-legal-capability`。

黄灯：开放知识问答。能检索核对的可以弱合成；核不过就别放大。

## 追问

- **完全不用合成，AFM 做得到吗？** 公开配方大量用合成 caption 和验证题解。不是反合成，是反无门合成。
- **合成 50 亿 caption 为什么算绿灯？** 他们还用检测器、CLIP、OCR 再滤，详细 caption 放后段。门在过滤器，不在条数。
- **产品要上线，人写来不及？** 人写种子 + 验证扩写。人写的是协议和种子，不是每一条。
