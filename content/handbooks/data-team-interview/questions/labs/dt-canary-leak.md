---
id: dt-canary-leak
section: labs
order: 48
level: A
title: Gemini pre-training 评测岗：leakage 和记忆怎么分开测？
quick: >-
  分两步测：先查训练内容和评测有没有重叠，再查这种重叠有没有把分数抬高。重叠用 n-gram
  扫描和金丝雀字符串查，是否虚高就把题目改数字、改变量名再测一遍。teacher model 间接 leakage n-gram 扫不到，要靠
  embedding nearest neighbors 和私有评测。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: >-
      Evaluation data contamination in LLMs: how do we measure it and (when)
      does it matter?
    url: 'https://arxiv.org/abs/2411.03923'
    type: primary
  - title: LiveBench
    url: 'https://arxiv.org/abs/2406.19314'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

要分开测两件事：训练内容和评测有没有重叠，以及这种重叠有没有把分数抬高。模型能续写训练里见过的内容，这是记忆；因为这段内容恰好是评测题而分数虚高，才说明评测受了 leakage 影响。只报一个「contamination rate 0.3%」就结束，等于只答了前一半。

举个例子，一道数学评测题在 training set 里有 13-gram 命中。把题里的数字换掉再问，模型还能做对，更像是真会；一换就大幅掉分，就要怀疑它是背下来的。

先查有没有重叠。用 13-gram 或子串扫描，把固定的 evaluation set 和 training set 对比，见 `dt-ngram-contam-code`。另一个办法是在训练文档里埋独一无二的金丝雀字符串，事后看模型能不能续写，来判断它见没见过这段内容。

再查重叠有没有影响分数，就是上面例子的做法：对同一道题改数字、变量名或语言，比较前后的表现。有一类 leakage n-gram 完全扫不到：teacher model 见过公开榜，又把知识带进了合成样本。这时要查 embedding nearest neighbors，并用 teacher 没见过的私有 evaluation slices 验证，见 `dt-code-bench-bleed`。

确认受了影响，依赖这份评测的发布先停下来，换成按时间划分的新题或私有题，见 `dt-contam-hold`。金丝雀和它的数据血缘写进 dataset card，保证能复现。长期可以学 LiveBench、LiveCodeBench，定期更新题目，用客观参考答案。

## 追问

**n-gram 扫描的参数怎么定？**
$n$ 别取太大，低频命中也别丢，两者都会造成假阴性。ConTAM（arxiv 2411.03923）还发现，只看最长 contamination 子串，往往比把所有命中合起来更容易辨别 contamination。

**金丝雀会不会被 deduplication 删掉？**
可能。要把它嵌进正常文档，别做成整页乱码，并在 deduplication 之后确认它还留在 shard 里。

**这套方法怎么用到规模定律上？**
固定计算量，只换数据，比较校正 leakage 之后的下游结果。受 contamination 榜单上画出来的缩放曲线不适合拿来做决策。

**这题在 DeepMind 是怎么出的？**
来源为公开 JD。DeepMind London pre-training 评测岗的公开 JD 涉及 leakage、覆盖和 validation set，这里按相关题型整理。
