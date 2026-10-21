---
id: dt-canary-leak
section: labs
order: 48
level: A
title: Gemini 预训练评测岗：泄漏和记忆怎么分开测？
quick: "分两步：先查训练内容和评测有没有重叠，再查这种重叠有没有抬高分数。重叠用 n-gram 扫描和金丝雀字符串查；是否虚高，要比较改数字、改变量名后的表现。n 取太大或忽略低频命中会漏检，教师间接泄漏还要靠 embedding 近邻和私有评测。"
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

要分开测两件事：训练内容是否与评测重叠，以及这种重叠是否抬高了分数。模型能续写训练里的内容，是记忆；因为这段内容恰好是评测题而得分虚高，才说明评测受了泄漏影响。只报一个「污染率 0.3%」就结束，等于只回答了前一半。

## 先查有没有重叠

用 13-gram 或子串扫描，把固定的评测集和训练集对比，见 `dt-ngram-contam-code`。另一个办法是在训练文档里放入独一无二的金丝雀字符串，事后检查模型能否续写，判断它是否见过这段内容。

扫描的参数会影响结论。ConTAM（arxiv 2411.03923）发现，只看最长污染子串，往往比把所有命中合并起来更容易辨别污染。$n$ 取太大，或忽略训练中出现次数少的命中，都可能造成假阴性。

## 再查重叠有没有影响分数

对同一道题改数字、变量名或语言，比较表现。变化后仍能做对，更支持能力泛化；分数大幅下降，就要怀疑是背题。

有一类泄漏 n-gram 可能完全不命中：教师模型见过公开榜，再把知识带进合成样本。这时要检查 embedding 近邻，并用教师没见过的私有切片验证，见 `dt-code-bench-bleed`。

## 查到之后

依赖受污染评测的发布先停下来，换成按时间划分的新题或私有题，见 `dt-contam-hold`。把金丝雀及其数据血缘写进 dataset card，保证可复现。长期可以学 LiveBench、LiveCodeBench，定期更新题目并使用客观参考答案。

题目背景：DeepMind London 预训练评测岗的公开 JD 涉及 leakage、覆盖和验证集；这里按相关题型整理，题面并非逐字面经。

## 追问

- **金丝雀会被去重删掉吗？** 可能。应该把它嵌进正常文档，不要做成整页乱码，并在去重后确认它仍留在 shard 里。
- **怎么用到规模定律上？** 固定计算量，只更换数据，比较校正泄漏后的下游结果。受污染榜单上的缩放曲线不适合作为决策依据。
