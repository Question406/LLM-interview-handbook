---
id: dt-synth-bench-trap
section: labs
order: 8
level: S
title: Anthropic 风格陷阱：开源合成推理集自称 GSM8K +15%，你先做什么？
quick: "先检查合成数据是否泄漏了冻结评测题：做精确匹配、n-gram、embedding 近邻检索，并抽查改写题。质量过滤和 MinHash 去重不能证明没有训练测试题。排除污染后，再检查答案与推理过程；内部合成同样不能把评测题放进生成提示。"
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

先把冻结评测的题面、选项、参考答案和已知题解登记下来。对候选训练集做精确匹配、13-gram / shingle 检查和 embedding 近邻检索。抽查高相似样本，区分只是题型相似，还是泄漏了评测题；翻译题、改数字的题也要检查。另留时间切新题（LiveCodeBench 那种）。如果只在旧评测题上提高，新题没有改善，就不能把声称的 15% 增益当成泛化能力提升。过了再谈 验证器（verifier）、过程假、教师偏差，见 `dt-contamination`、`dt-synth-reasoning`。

不这么选的理由：公开面试题把场景写成一份合成推理数据声称 MMLU / GSM8K 涨 15%，算力够做一遍 监督微调（SFT）。很多人答质量过滤或 MinHash。题要的是 benchmark bleed。前沿教师在预训练里见过公开基准，用它合成「新题」，题面常是改写。

接到苹果：AFM mid 写了验证合成，没有写「下载一份开源推理集直接混」。生成器禁带门禁。作者声称已经去污，仍用我自己的门禁版本再跑。泄漏 0.5% 先拿掉命中再训一版小模型，拿掉后 15% 还在，才谈混入。合成题过标准答案，门禁用真源。

公开锚点：LiveCodeBench 按时间切新题防背题；Lee et al. 2021 证明复制有害，解决不了改写泄漏。

## 追问

- **作者声称已经去污？** 仍用我自己的门禁版本再跑。他们的套件和报告套件往往不是同一版。
- **泄漏 0.5% 能不能用？** 拿掉命中再训一版小模型。拿掉后 15% 还在，才谈混入。
- **内部合成会不会一样脏？** 会，如果 输入提示里带了评测题。生成器禁带门禁，见 `dt-contamination`。
