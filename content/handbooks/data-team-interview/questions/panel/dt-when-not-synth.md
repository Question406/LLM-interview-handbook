---
id: dt-when-not-synth
section: panel
order: 9
level: A
title: Panel：什么时候不要上合成数据？
quick: "先问生成结果靠什么独立验证；答不出来就不该合成。具体的停止信号是：没有独立验证手段、需要真实世界的长尾、评测与生成器同族，或已经多代回流。合成适合补能验证的任务覆盖，其他缺口用人写种子、许可采集或改进评测来解决。"
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

我会先问：「生成结果要靠什么独立验证？」有可靠的执行检查、标准答案或人工核验，才开始设计合成流程。答不出来，就改走人写、许可数据集或改进评测。

这题考的是你会不会停下来。任何缺口都回一句「合成」，这题就答砸了；变出一些看起来像的文本，补不上真实的覆盖。能说清为什么不合成，再给出替代方案，才说明你知道合成的边界。

## 什么时候可以合成

前提是有独立于生成器的可靠检查：执行测试、符号验证、环境状态，或者人工对照许可的真实来源抽查。有了这样的检查，就是绿灯。AFM 公开的合成都带验证门：mid 阶段写了「verified for correctness wherever possible」，图表用代码渲染、自带数据表，工具数据在执行环境里生成。

## 什么时候直接停

- **主观文风、幽默、某个 locale 的自然程度。** 教师会写成翻译腔，AFM 多语评测不用翻译题就是这个原因。这类缺口用人写种子，合成最多用来扩写题面。
- **真实世界的长尾。** 罕见的海报版式、被污损的手写、某个国家的地址格式。纯合成的数据会偏干净。真数据不够就去许可采集，合成只当补充。
- **生成器和 judge 同族。** 合成题加合成评测，再加同系的奖励模型（RM），分数会三重虚高，见 `dt-judge-bias`、`dt-contamination`。
- **已经回流多代。** 错误模式越来越集中，和人类数据对照，熵在下降，见 `dt-self-improve`。
- **来源本身不合法。** 拿用户原文当种子再「改写」，等于绕过隐私，见 `dt-legal-capability`。

还有一种黄灯情况：开放知识问答。能用检索核对的可以少量合成；核对不了，就不要放大。

## 追问

- **是不是合成越少越好？** 公开配方里大量使用合成数据，AFM 就用了大量合成 caption 和经过验证的题解。要避免的是没有验证门的合成。
- **合成 50 亿条 caption 为什么算绿灯？** 因为 AFM 还用检测器、CLIP、OCR 再过滤一遍，详细 caption 放在后面的阶段。判断绿灯看的是过滤器，条数多少不影响判断。
- **时间紧、人写来不及怎么办？** 人写种子，再做验证过的扩写。人只需要写协议和种子，用不着写每一条数据。

相关：可以合成时的具体管线见 `dt-synth-reasoning`、`dt-synth-tool-mm`。
