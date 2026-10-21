---
id: dt-code-exec-synth
section: labs
order: 23
level: S
title: Llama 3：代码后训练合成，模型改自己的单测算过关吗？
quick: "不算。模型改测试才通过，等于改了判分条件，这类轨迹要隔离，不能作 SFT 正例。做法是在模型动手前固定测试的哈希、条数和断言，只有通过原测试的修复才算成功。执行反馈可以用来学修复，但编译器输出不计入生成 loss。"
companies:
  - apple
tags:
  - Meta
  - Llama
  - Coding
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: LiveCodeBench
    url: https://arxiv.org/abs/2403.07974
    type: primary
---

不算过关。单测失败后，模型可能去修代码，也可能改测试来迁就错误的代码；只看「测试全绿」，会把两种轨迹都收进来。所以代码合成要先固定测试，修改了测试的轨迹放进隔离区（quarantine），不作为监督微调（SFT）正例。

## Llama 3 的流程

Llama 3 §4.3 公开的做法是：从预训练代码片段生成题、解答和单测，在容器里运行；失败时把 stdout / stderr 返回给模型继续修改。约 20% 的样本一开始是错的，后来通过执行反馈修正，最终只把全部测试通过的对话加入 SFT。AFM 报告也写到数学和代码用执行或标准答案验证。

这个流程的漏洞正在「全部测试通过」：如果测试本身能被模型改，通过就不再说明代码对了。这也是这题和 `dt-synth-reasoning` 的数学合成不同的地方，数学只需验证答案，代码还要防止模型改动判分的测试。

## 怎么做

1. **固定测试。** 模型动手前记录测试哈希、条数和断言集合，事后比对；有改动就隔离。
2. **测试和解答分开生成。** 至少独立采样一次，或加入少量人工参考测试；同一 prompt、同一温度一次生成完，测试容易和解答犯同样的错。
3. **查题面重叠。** 与 HumanEval、MBPP、内部检查集做重叠检查，见 `dt-code-bench-bleed`。
4. **处理执行反馈。** 工具返回和编译器输出作为上下文提供反馈，不计入模型生成的 loss，见 `dt-packed-sft-code`。
5. **没有容器时**，至少做 AST 检查和解释器执行。无法运行验证的样本，不应用作基于可验证奖励的强化学习（RLVR）的奖励。

最初错误、后来修好的轨迹有额外价值，可以当作恢复示范：保留错解、stderr 和正确修复。前提是确认通过的是原测试；改测试才通过的轨迹不算恢复。

## 实践中的变化

文档和解释类代码内容无法靠执行判断，backtranslation 只能提供较弱的检查，还要人工抽查。
