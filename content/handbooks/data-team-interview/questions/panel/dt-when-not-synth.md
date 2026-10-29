---
id: dt-when-not-synth
section: panel
order: 9
level: A
title: Panel：什么时候不要上 synthetic data？
quick: 假设每一轮都让当前模型生成下一轮训练数据，又没有独立检查。模型经常生成的模式会被反复保留，少见但重要的情况可能越来越少，错误也可能被继续学习。
companies:
  - apple
tags:
  - Apple
  - Synthetic Data
  - Data Quality
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: The Curse of Recursion / Model Collapse
    url: 'https://arxiv.org/abs/2305.17493'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Self-Instruct
    url: 'https://arxiv.org/abs/2212.10560'
    type: primary
---

## 回答思路

> **问题与场景：** 假设每一轮都让当前模型生成下一轮训练数据，又没有独立检查。
>
> **做法与原因：** 我会先问生成数据怎样证明正确，再检查覆盖与重复。
>
> **检查与取舍：** 生成数量不是成功标准。

## 可以这样回答

假设每一轮都让当前模型生成下一轮训练数据，又没有独立检查。模型经常生成的模式会被反复保留，少见但重要的情况可能越来越少，错误也可能被继续学习。

我会先问生成数据怎样证明正确，再检查覆盖与重复。对于有可靠测试的代码或数学任务，可以保留验证通过的候选；开放任务则需要额外审核和新鲜的真实数据。

生成数量不是成功标准。需要在未参与生成与筛选的任务上比较效果，并检查连续迭代后哪些能力、语言或 rare cases 在退化。

## 技术备查

我会先问一句「生成结果靠什么独立验证」。有可靠的执行检查、标准答案或人工核验，才开始设计合成流程；答不出来，就改走人写、许可数据集或改进评测。

这题考的是你会不会停下来。比如某个 locale 的回答不够自然，让 teacher 合成一批，写出来的多半是翻译腔，看起来像，补不上真实的覆盖。任何缺口都回一句「合成」，这题就答砸了；能说清为什么不合成，再给出替代方案，才说明你知道 synthetic data 的 limitations。

能合成的前提，是有独立于生成器的可靠检查：执行测试、符号验证、环境状态，或者人工对照许可的真实来源抽查。AFM 公开的合成都带验证门，mid 阶段写了「verified for correctness wherever possible」，图表用代码渲染、自带数据表，工具数据在执行环境里生成。

停下来的情况大多能从「验证不了」推出来。主观文风、幽默、locale 的自然程度，teacher 会写成翻译腔，AFM multilingual 评测不用翻译题就是这个原因，这类缺口用人写 seed，合成最多用来扩写题面。真实世界的 long-tail，比如罕见的海报版式、被污损的手写、某个国家的地址格式，纯合成的数据会偏干净，真数据不够就去许可采集，合成只当补充。开放知识问答算黄灯，能用检索核对的可以少量合成，核对不了就不要放大。

## 追问

**生成器和 judge 同族会怎样？**
分数会三重虚高。合成题加合成评测，再加同系的 reward model（RM），见 `dt-judge-bias`、`dt-contamination`。

**已经反复使用 synthetic data 训练多轮了，怎么判断该停？**
看错误模式是不是越来越集中，和人类数据对照，熵在下降就该停，见 `dt-self-improve`。

**拿用户原文当 seed 再改写，可以吗？**
不可以，来源本身不合法，这等于绕过隐私，见 `dt-legal-capability`。

**是不是合成越少越好？**
不是。公开配方里大量用 synthetic data，AFM 就用了大量合成 caption 和经过验证的题解，要避免的是没有验证门的合成。合成 50 亿条 caption 也算绿灯，因为 AFM 还用检测器、CLIP、OCR 再过滤一遍，详细 caption 放在后面的阶段；判断绿灯看的是过滤器，条数多少不影响。

**时间紧、人写来不及怎么办？**
人写 seed，再做验证过的扩写。人只需要写协议和 seed，用不着写每一条数据。

相关：`dt-synth-reasoning`、`dt-synth-tool-mm`（可以合成时的具体 pipeline）
