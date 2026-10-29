---
id: dt-synth-bench-trap
section: labs
order: 8
level: S
title: Anthropic 风格陷阱：开源合成推理集自称 GSM8K +15%，你先做什么？
quick: 假设开源合成集宣称让公开 benchmark 提升很多。我会先查训练 seed、生成 prompt 和筛选规则，有没有直接使用测试题、参考答案或它们的改写。
companies:
  - apple
tags:
  - Anthropic
  - Contamination
  - Synthetic Data
  - Apple
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: 'https://arxiv.org/abs/2107.06499'
    type: primary
  - title: 'LiveCodeBench: Holistic and Contamination Free Evaluation'
    url: 'https://arxiv.org/abs/2403.07974'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 回答思路

> **问题与场景：** 假设开源合成集宣称让公开 benchmark 提升很多。
>
> **做法与原因：** 再对训练与评测做多种重叠检查，并抽查命中样本。
>
> **检查与取舍：** 确认来源后，用独立任务和匹配预算做对照。

## 可以这样回答

假设开源合成集宣称让公开 benchmark 提升很多。我会先查训练 seed、生成 prompt 和筛选规则，有没有直接使用测试题、参考答案或它们的改写。

再对训练与评测做多种重叠检查，并抽查命中样本。只换名字、数字或语言，并不保证是独立任务；同一题的变体需要一起处理。

确认来源后，用独立任务和匹配预算做对照。不能把整个数据集先加进去，再用同一个公开榜单证明它有效。

## 技术备查

第一件事是查它有没有把评测题合成进去。+15% 很可能来自 benchmark bleed，也就是评测题改写之后漏进了 training set，质量过滤和 MinHash deduplication 都查不出这种 leakage。contamination 排除了，才轮到看答案和推理过程。

公开面试题的场景是：一份合成推理数据声称 MMLU / GSM8K 涨了 15%，算力够做一遍 SFT。为什么先怀疑 leakage？前沿 teacher model 在 pre-training 时见过公开基准，用它合成「新题」，题面常常只是评测题改了几个数字。

查的时候，我先把冻结评测的题面、选项、参考答案和已知题解登记下来，对候选 training set 做精确匹配、13-gram / shingle 检查和 embedding nearest neighbors 检索。高相似的样本人工看，分清只是题型相似，还是 leakage 了评测题，翻译题、改数字的题也要查。然后另留一批按时间切出的新题，LiveCodeBench 就是这样按时间切新题来防背题的；只在旧评测题上涨、新题没改善，这 15% 就不能当成 generalization 提升。最后把命中样本删掉，再训一版 small model，哪怕只 leakage 0.5% 也先删。删掉之后 15% 还在，才谈混入。

## 追问

**MinHash deduplication 已经做过了，还不够吗？**
不够。MinHash 这类 deduplication 只能抓近似复制；Lee et al. 2021 证明了复制有害，但解决不了改写 leakage。

**作者说已经 decontamination 了呢？**
仍用我自己的 evaluation gate 版本再跑一遍。他们用的评测套件和我们报告用的，往往不是同一版。

**contamination 都排除了，下一步看什么？**
看 verifier（verifier）、过程造假和 teacher 偏差，见 `dt-contamination`、`dt-synth-reasoning`。

**内部合成会不会一样脏？**
会，只要生成提示里带了评测题，产出的就是改写 leakage，见 `dt-contamination`。所以生成器的提示里不放 held-out evaluation examples，合成题要对过标准答案，evaluation gate 本身用真实来源。AFM 2025 报告的 mid-training 用的也是经过验证的 synthetic data。
