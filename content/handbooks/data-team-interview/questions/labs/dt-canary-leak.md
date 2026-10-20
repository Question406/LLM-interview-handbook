---
id: dt-canary-leak
section: labs
order: 48
level: A
title: Gemini 预训练评测岗：泄漏和记忆怎么分开测？
quick: "结合 n-gram 扫描、金丝雀字符串和题目扰动检查泄漏。命中说明可能见过内容；还要比较改数字、改变量名后的表现，判断是否因此得分虚高。n 太大或忽略低频命中会漏检，教师间接泄漏还需要近邻和私有评测。"
companies:
  - apple
tags:
  - DeepMind
  - Contamination
  - Memorization
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Evaluation data contamination in LLMs: how do we measure it and (when) does it matter?"
    url: https://arxiv.org/abs/2411.03923
    type: primary
  - title: LiveBench
    url: https://arxiv.org/abs/2406.19314
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

泄漏检查分两件事：训练内容是否与评测重叠，以及这种重叠是否抬高了分数。

先用 13-gram 或子串扫描固定评测与训练集，见 `dt-ngram-contam-code`。再对同题改数字、变量名或语言，比较表现。如果变化后仍能做对，更支持能力泛化；若分数大幅下降，就要怀疑背题。还可以在训练文档中放入独一无二的金丝雀字符串，检查模型能否续写，判断它是否见过这段内容。

ConTAM 的结论是，只看最长污染子串，往往比合并所有命中更容易辨别污染。$n$ 取太大，或忽略训练中出现次数少的命中，都可能造成假阴性。不能只报「污染率 0.3%」就结束，还要分析命中是否影响成绩。

## 查到后怎么处理

依赖受污染评测的发布先停下来，换成按时间划分的新题或私有题，见 `dt-contam-hold`。把金丝雀及其数据血缘写入 dataset card，保证可复现。

教师见过公开榜，再把知识带入合成样本，n-gram 可能完全不命中。此时还要检查 embedding 近邻，并用教师未见过的私有切片验证，见 `dt-code-bench-bleed`。长期可以采用 LiveBench、LiveCodeBench 这类定期更新题目并使用客观参考答案的方式。

公开参考包括 ConTAM（arxiv 2411.03923）和 LiveBench。DeepMind London 预训练评测岗的公开 JD 涉及 leakage、覆盖和验证集；这里是相关题型整理，不是逐字面经。

## 追问

- 记忆与泄漏伤害怎么区分？续写训练内容是记忆；因内容恰好是评测题而得分虚高，才说明评测受泄漏影响。
- 金丝雀会被去重删掉吗？可能。应嵌入正常文档，避免整页乱码，并在去重后确认仍留在 shard 中。
- 如何用于规模定律？固定计算量，只更换数据，比较校正泄漏后的下游结果。受污染榜上的缩放曲线不适合作为决策依据。
