---
id: dt-synth-bench-trap
section: labs
order: 8
level: S
title: Anthropic 风格陷阱：开源合成推理集自称 GSM8K +15%，你先做什么？
quick: "先查污染，再谈质量。对照冻结评测做精确匹配、n-gram 和 embedding 近邻检索，并抽查改写题、翻译题；再用时间切出的新题验证增益。质量过滤和 MinHash 去重证明不了没训到测试题。排除污染后，才检查答案和推理过程；自己合成数据时，生成提示里也不能放评测题。"
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

第一件事是查它有没有把评测题合成进去。+15% 很可能来自 benchmark bleed，也就是评测题改写后漏进了训练集；质量过滤和 MinHash 去重都查不出这种泄漏。污染排除之后，才轮到看答案和推理过程。

## 为什么先怀疑泄漏

公开面试题把场景写成：一份合成推理数据声称 MMLU / GSM8K 涨了 15%，算力够做一遍监督微调（SFT）。前沿教师模型在预训练时见过公开基准，用它合成「新题」，题面常常只是评测题的改写。MinHash 这类去重只能抓近似复制；Lee et al. 2021 证明了复制有害，但解决不了改写泄漏。LiveCodeBench 按时间切新题来防背题，就是针对这个问题。

## 怎么查

1. 登记门禁：把冻结评测的题面、选项、参考答案和已知题解存下来。
2. 多粒度比对：对候选训练集做精确匹配、13-gram / shingle 检查和 embedding 近邻检索。
3. 人工抽查：看高相似样本，区分只是题型相似，还是泄漏了评测题。翻译题、改数字的题也要查。
4. 用新题验证：另留按时间切出的新题（LiveCodeBench 那种）。如果只在旧评测题上提高、新题没有改善，就不能把 15% 当成泛化能力提升。
5. 拿掉命中再训：哪怕只泄漏 0.5%，也先删掉命中样本，再训一版小模型。删掉后 15% 还在，才谈混入。

这些都过了，再看验证器（verifier）、过程造假和教师偏差，见 `dt-contamination`、`dt-synth-reasoning`。

自己合成数据也守同样的规矩：生成器的提示里不放门禁题，合成题要对过标准答案，门禁本身用真实来源。AFM 2025 报告的 mid-training 用的也是经过验证的合成数据。

## 追问

- **作者说已经去污了呢？** 仍用我自己的门禁版本再跑一遍。他们用的评测套件和我们报告用的往往不是同一版。
- **内部合成会不会一样脏？** 会，只要生成提示里带了评测题，产出的就是改写泄漏，见 `dt-contamination`。
