---
id: openai-if-eval
section: openai
order: 26
level: A
title: OpenAI：指令遵循评测（IFEval 一类）和「会考试不会听话」
quick: >-
  IFEval 测的是可自动校验的约束：字数、关键词、格式、大小写，不是 MMLU 会不会。会考试不会听话，是知识榜高、约束遵守低。判分用程序
  不要用模型当法官。OpenAI 的模型规范还把系统 / 开发者 / 用户指令分层，冲突时听谁要单独测。
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

## 题怎么来的

InstructGPT 的卖点是听人话，不只是会做题。IFEval（Zhou et al.）把「听话」收成可程序检查的约束，大约 500 条 prompt、二十多类指令：用词次数、禁止逗号、JSON 外壳、标题层级、语言、长度。OpenAI 对内评测纪律见 `openai-eval-harness`；本题专门对付 **指令遵循和知识评测被揉成一个平均分**。模型规范（Model Spec）后来把系统 / 开发者 / 用户的优先级写进产品，冲突指令是这题的加试。

「会考试不会听话」的画像：MMLU / GSM8K 很高，但「用恰好三个项目符号、每个以指定动词开头」做不到。基座模型常见；SFT 不足、或 RLHF 只优化冗长客气时也会出现。反过来，死磕格式、事实胡编，是另一类失败，要用能力 holdout 拦住，不要用 IFEval 冒充知识榜。

## IFEval 测什么，不测什么

每条 prompt 带若干 **可验证** 约束。判分器是确定性程序：数词、匹配正则、检查是否包含 / 禁止某短语。论文报两层：prompt 级（所有约束都过）和 instruction 级（单条约束）；再加 strict / loose（loose 允许轻微格式变体）。我会把这四个数字都报，不只报一个「IFEval 分」。

它 **不测**：开放目标是否有用、是否谄媚、是否安全拒答、多步工具是否选对。那些要 Arena、人工、或 `openai-function-calling` 的工具 eval。也不要用 LLM-as-judge 去判 IFEval——题目存在的理由就是避免法官模型的偏好。simple-evals 把协议写死，同一精神：换 prompt 算新实验。

和「考试」正交的原因很具体。选择题可以把世界知识读进选项；IFEval 的目标往往是输出形状。一个背过考点的模型仍可能无视「不要用逗号」。SFT 若全是「详尽回答」，模型会为了像助手而打破长度上限。DPO 若 chosen 更长，长度约束会掉点。所以对齐之后 **必须重跑** IFEval，不要假设偏好优化单调改进听话。

冲突指令要单独做切片：系统说「永远用中文」，用户说「Reply in English only」。Model Spec 的层级是系统 > 开发者 > 用户 > 工具输出；面试不必背原文条款，但要说 **你的 harness 有没有测层级**。没有层级切片，线上就会在越权工具调用和「用户说忽略系统」上翻车。Prompt 注入是攻击版的同一问题，见 `anthropic-prompt-injection`。

## 我会怎么放进内部 harness

- **Dev：** 小子集，允许看失败 case，用来回归格式回归。默认怀疑它已被过拟合。
- **Frozen IFEval：** 题目、判分器版本、解码温度、是否允许思维链全部打标签。涨点必须同一版本。
- **私有约束集：** 自己写的格式 / 长度 / JSON schema，不上网。IFEval 会进预训练，公开榜只能沟通。
- **和能力 holdout 分表。** 不要把 IFEval 和 MMLU 加权成「总分」用来选 checkpoint。两个方向的失败模式相反，平均会互相洗白。
- **切片。** 长度、关键词、大小写、JSON、多约束叠在同一句。掉点通常藏在多约束和冲突层级，不藏在平均里。

训练侧：SFT 数据要显式带约束和负例（「不要用项目符号」的完成里就没有项目符号）。只喂「有帮助的长回答」，IFEval 上的短约束会掉。工具调用的 schema 遵守是 IFEval 的近亲，但判分走 JSON Schema，不是字数正则。

错法：用 GPT-4 当法官给「是否听话」打 1–5 分，再宣称对标 IFEval。分数不可复现，而且法官偏爱流畅。另一错法：把 IFEval 编进 RL 奖励，过两周模型只会刷那 25 类约束，真正的用户指令仍不听。Harness 的职责是检测 hacking，见 `openai-eval-harness`。

我会在口头上把两句话拆开：**会不会做题** 和 **会不会按约束说话**。混成一个平均分，选 checkpoint 时两边的失败会互相洗白。产品要听指令时，IFEval 是契约，不是附加题。

## 追问

- **loose 高、strict 低说明什么？** 模型大致听懂，格式差一个空格或标点。产品能否接受，要看约束是「必须合法 JSON」还是「语气」。
- **基座能不能跑 IFEval？** 能跑，分数通常低。它说明指令调优有没有把「约束」训进去，不是说明预训练失败。
- **和 Arena 谁说了算？** Arena 是偏好，IFEval 是契约。用户喜欢的长文可能正好违反「少于 20 词」。两张表都要。
- **多约束冲突怎么办？** 产品要有层级；评测要有冲突切片。模型自己「综合一下」往往是谁声音大听谁的。
