---
id: dt-code-exec-synth
section: labs
order: 23
level: S
title: Llama 3：代码后训练合成，模型改自己的单测算过关吗？
quick: "先固定测试的哈希、数量和断言，再让模型修改代码。改测试才通过的轨迹隔离，不能作 SFT 正例。执行反馈可用于学习修复，但编译器输出不计入生成 loss；只有独立测试验证的修复，才能算成功。"
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

代码合成要先固定测试。模型动手前记录测试哈希、条数和断言集合；修改了测试的轨迹放入隔离区（quarantine），不要作为监督微调（SFT）正例。

生成测试和解答时，不要用同一 prompt、同一温度一次生成完。至少独立采样一次，或加入少量人工参考测试。再与 HumanEval、MBPP、内部检查集做题面重叠检查，见 `dt-code-bench-bleed`。

工具返回和编译器输出作为上下文提供反馈，不计入模型生成的 loss，见 `dt-packed-sft-code`。没有容器时，至少做 AST 检查和解释器执行；无法运行验证的样本，不应用作基于可验证奖励的强化学习（RLVR）奖励。

## 为什么「测试全绿」还不够

单测失败后，模型可能修代码，也可能改测试来迁就错误代码。只看全绿，会把两种轨迹都收进来。固定测试，才能分辨真正修复与修改判分条件。

Llama 3 §4.3 的公开流程是，从预训练代码片段生成题、解答和单测，在容器运行；失败时把 stdout / stderr 返回给模型继续修改。约 20% 的样本最初错误，后来通过执行反馈修正，最终只把全部测试通过的对话加入 SFT。

## 在苹果场景中的用法

AFM 公开也说明数学、代码使用执行或标准答案验证，但不能推测内部测试条数。文档和解释无法靠执行判断，backtranslation 只能提供较弱检查，还要人工抽查。来源使用许可代码片段或经过验证的合成数据，不默认回收用户仓库。

最初错误再修好的轨迹，可以作为恢复示范：保留错解、stderr 和正确修复。改测试才通过的轨迹不算恢复。与 `dt-synth-reasoning` 相比，这题额外关注代码任务的测试本身会被修改。

## 追问

- 20% 的自修复能做过程监督吗？可以作恢复示范，但要确认通过的是原测试。
- 没有容器怎么办？至少做 AST 与解释器验证，未运行验证的数据不要进入 RLVR 奖励。
- 与数学合成有什么区别？除了答案验证，代码还要防止模型改动测试。
