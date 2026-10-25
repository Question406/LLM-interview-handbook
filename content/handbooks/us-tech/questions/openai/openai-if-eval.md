---
id: openai-if-eval
section: openai
order: 26
level: A
title: OpenAI：指令遵循评测（IFEval 一类）和「会考试不会听话」
quick: "我会用确定性程序检查字数、关键词、格式等约束，分别报告 prompt 级和 instruction 级的 strict、loose 结果。它衡量按约束回答的能力，知识正确性与指令层级冲突还需要另外测，不能靠一个平均分选模型。"
tags:
  - OpenAI
  - IFEval
  - Instruction following
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Instruction-Following Evaluation for Large Language Models
    url: https://arxiv.org/abs/2311.07911
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Introducing the Model Spec
    url: https://openai.com/index/introducing-the-model-spec/
    type: primary
  - title: openai/simple-evals
    url: https://github.com/openai/simple-evals
    type: primary
---

指令遵循要单独评，用程序检查明确约束，再与知识能力分表看。比如模型 MMLU、GSM8K 很高，却做不到“恰好三个项目符号、每个以指定动词开头”，说明它能答题但没有稳定满足输出要求。反过来格式全对、事实编造，也不能算合格。

IFEval（Zhou et al.）用约 500 条 prompt、二十多类指令覆盖用词次数、禁止逗号、JSON、标题层级、语言和长度。判分器数词、匹配正则或检查短语，报告 prompt 级全部通过、instruction 级单条通过，以及 strict、允许轻微格式变体的 loose，共四个数字。它刻意避免法官模型的偏好，用 GPT-4 打 1 到 5 分不能叫同一套评测。

知识榜测不出这些约束，是因为选择题可依靠知识选答案，而 IFEval 经常约束输出形状。基座模型、SFT 不足、只偏好冗长客气回答的 RLHF 都可能失守；DPO chosen 更长，也可能降低长度约束分数，所以每次对齐后重跑。开放回答是否有用、谄媚、安全拒答、工具选择，则需要 Arena、人评和工具 eval。

指令冲突还要单独切片。比如系统要求中文，用户要求“Reply in English only”，按这里讨论的层级检查系统 > 开发者 > 用户 > 工具输出，观察模型是否被“忽略系统”或注入内容诱导越权。Model Spec 的优先级不能和普通字数题混为一谈。

放进 harness 时，dev 用可看错题的小集做格式回归；frozen 固定题目、grader 版本、温度、是否允许 CoT，改 prompt 算新实验；私有集自己写格式、长度、JSON schema 约束，不上网，因为公开 IFEval 也可能进入训练。按长度、关键词、大小写、JSON、多约束和冲突层级看切片，避免平均掩盖问题，IFEval 和 MMLU 也不合成总分。

训练数据要显式包含约束和负例，例如要求不用项目符号时，示范就真的不用。工具 schema 同样需遵守，但由 JSON Schema 判分，不能套字数正则。若把 IFEval 直接当 RL 奖励，模型可能两周内学会刷那 25 类，却仍不遵守新指令；harness 应当检测这种过拟合。InstructGPT、simple-evals 的公开工作也强调听懂任务和固定协议，不能用流畅程度代替验证。

## 追问

**loose 高、strict 低说明什么？**
模型大致理解了要求，但空格、标点等精确形式还会错。合法 JSON 是硬约束，语气则可能容忍变体。

**基座能跑 IFEval 吗？**
可以，通常分低，反映约束还没被指令调优训进去，不能直接说明预训练失败。

**和 Arena 谁优先？**
两张表都看。偏好长文可能违反“少于 20 词”，偏好与契约回答不同问题。

**多约束冲突怎么办？**
产品先定义优先级，评测再覆盖冲突，不能让模型临场决定听谁的。

相关：`openai-eval-harness`、`openai-function-calling`、`anthropic-prompt-injection`
