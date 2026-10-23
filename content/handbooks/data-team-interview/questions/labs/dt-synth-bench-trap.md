---
id: dt-synth-bench-trap
section: labs
order: 8
level: S
title: Anthropic 风格陷阱：开源合成推理集自称 GSM8K +15%，你先做什么？
quick: "先查污染，再谈质量。对照冻结评测做精确匹配、n-gram 和 embedding 近邻检索，抽查改写题、翻译题，再用按时间切出的新题验证增益；质量过滤和 MinHash 去重证明不了没训到测试题。排除污染后，才检查答案和推理过程；自己合成数据时，生成提示里也不能放评测题。"
companies:
  - apple
tags:
  - Anthropic
  - Contamination
  - Synthetic Data
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: "LiveCodeBench: Holistic and Contamination Free Evaluation"
    url: https://arxiv.org/abs/2403.07974
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

第一件事是查它有没有把评测题合成进去。+15% 很可能来自 benchmark bleed，也就是评测题改写之后漏进了训练集，质量过滤和 MinHash 去重都查不出这种泄漏。污染排除了，才轮到看答案和推理过程。

公开面试题的场景是：一份合成推理数据声称 MMLU / GSM8K 涨了 15%，算力够做一遍监督微调（SFT）。为什么先怀疑泄漏？前沿教师模型在预训练时见过公开基准，用它合成「新题」，题面常常只是评测题改了几个数字。

查的时候，我先把冻结评测的题面、选项、参考答案和已知题解登记下来，对候选训练集做精确匹配、13-gram / shingle 检查和 embedding 近邻检索。高相似的样本人工看，分清只是题型相似，还是泄漏了评测题，翻译题、改数字的题也要查。然后另留一批按时间切出的新题，LiveCodeBench 就是这样按时间切新题来防背题的；只在旧评测题上涨、新题没改善，这 15% 就不能当成泛化能力提升。最后把命中样本删掉，再训一版小模型，哪怕只泄漏 0.5% 也先删。删掉之后 15% 还在，才谈混入。

## 追问

**MinHash 去重已经做过了，还不够吗？**
不够。MinHash 这类去重只能抓近似复制；Lee et al. 2021 证明了复制有害，但解决不了改写泄漏。

**作者说已经去污了呢？**
仍用我自己的门禁版本再跑一遍。他们用的评测套件和我们报告用的，往往不是同一版。

**污染都排除了，下一步看什么？**
看验证器（verifier）、过程造假和教师偏差，见 `dt-contamination`、`dt-synth-reasoning`。

**内部合成会不会一样脏？**
会，只要生成提示里带了评测题，产出的就是改写泄漏，见 `dt-contamination`。所以生成器的提示里不放门禁题，合成题要对过标准答案，门禁本身用真实来源。AFM 2025 报告的 mid-training 用的也是经过验证的合成数据。
