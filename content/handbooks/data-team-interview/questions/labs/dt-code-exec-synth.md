---
id: dt-code-exec-synth
section: labs
order: 23
level: S
title: Llama 3：代码后训练合成，模型改自己的单测算过关吗？
quick: "不算。模型改测试才通过，等于改了判分条件，这种轨迹要隔离，不当 SFT 正例。做法是在模型动手前记下测试的哈希、条数和断言，只有通过原测试的修复才算成功；执行反馈可以拿来学修复，编译器输出不计入生成 loss。"
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

不算过关。单测失败之后，模型可能去修代码，也可能改测试来迁就错的代码，只看「测试全绿」会把两种轨迹都收进来。所以代码合成要先固定测试，改过测试的轨迹放进隔离区（quarantine），不当监督微调（SFT）正例。

比如一道题要求函数返回去重后的排序列表，模型漏了去重，测试挂了。它没去改函数，直接把断言里的期望值改成了自己的输出，测试就绿了。这条轨迹进了 SFT，教给模型的就是「改测试」。

Llama 3 §4.3 公开的流程是：从预训练代码片段生成题、解答和单测，在容器里跑；失败了就把 stdout / stderr 返回给模型继续改。约 20% 的样本一开始是错的，后来靠执行反馈修好，最后只把全部测试通过的对话放进 SFT。AFM 报告也写到数学和代码用执行或标准答案验证。

漏洞恰好就在「全部测试通过」这一步：测试本身能被模型改，通过就说明不了代码是对的。这也是它和 `dt-synth-reasoning` 里数学合成不一样的地方，数学只需验证答案，代码还得防模型改动判分的测试。

所以第一步是在模型动手前记下测试哈希、条数和断言集合，事后比对，有改动就隔离。题面还要和 HumanEval、MBPP、内部检查集查重叠，见 `dt-code-bench-bleed`。

一开始错、后来修好的轨迹还有额外价值，可以当恢复示范，把错解、stderr 和正确修复都留下。前提是确认通过的是原测试，改测试才过的不算恢复。

## 追问

**测试和解答能一次生成吗？**
最好分开。同一 prompt、同一温度一次生成完，测试容易和解答犯同样的错。至少独立采样一次，或者混入少量人工参考测试。

**执行反馈要不要算进 loss？**
不算。工具返回和编译器输出作为上下文给模型反馈，不计入模型生成的 loss，见 `dt-packed-sft-code`。

**没有容器能跑代码怎么办？**
至少做 AST 检查和解释器执行。没法运行验证的样本，不拿来当基于可验证奖励的强化学习（RLVR）的奖励。

**文档和解释类的代码内容怎么验？**
靠执行判断不了，backtranslation 只能给比较弱的检查，还要人工抽查。
