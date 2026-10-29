---
id: meta-synth-sft
section: meta
order: 19
level: A
title: Meta：合成 SFT 数据——自指令、teacher model、泄漏和多样性
quick: >-
  Llama 3 合成 SFT 用模型扩指令、写回答，再结合过滤和执行反馈选数据。8B / 70B 能从更强教师受益，405B
  只学自己的代码却可能退步，所以旗舰更需要单测等外部真值；同时检查评测泄漏、教师风格和任务覆盖。
tags:
  - Meta
  - Llama
  - SFT
  - Synthetic Data
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: Self-Instruct — Aligning Language Models with Self-Generated Instructions
    url: 'https://arxiv.org/abs/2212.10560'
    type: primary
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: 'https://arxiv.org/abs/2307.09288'
    type: secondary
  - title: Introducing Llama 3.1
    url: 'https://ai.meta.com/blog/meta-llama-3-1/'
    type: primary
---

## 可以这样回答

合成 SFT 要把生成、过滤和外部反馈一起设计。比如教师能写出一条代码回答，并不说明它值得让学生学；先执行、根据报错修正，再留下能过单测的轨迹，信号就可靠得多。Self-Instruct 给出了自指令流程，Llama 3 Herd 则公开了迭代后训练和代码执行反馈的做法。

Self-Instruct：少量人工种子指令 → 模型写新指令 → 过滤太像的 → 再写回答 → 再过滤。Llama 3 把这套放大，并且**迭代**：每一轮后训练用最新模型产数据，再 SFT + DPO。论文写 SFT 目标仍是标准 cross entropy loss（CE），prompt 的 token 不计入损失，很多 target 其实是模型生成的。

## 技术备查

合成 SFT 要把生成、过滤和外部反馈一起设计。比如教师能写出一条代码回答，并不说明它值得让学生学；先执行、根据报错修正，再留下能过单测的轨迹，信号就可靠得多。Self-Instruct 给出了自指令流程，Llama 3 Herd 则公开了迭代后训练和代码执行反馈的做法。

## 谁生成，怎样确认回答值得学

Self-Instruct：少量人工种子指令 → 模型写新指令 → 过滤太像的 → 再写回答 → 再过滤。Llama 3 把这套放大，并且**迭代**：每一轮后训练用最新模型产数据，再 SFT + DPO。论文写 SFT 目标仍是标准 cross entropy loss（CE），prompt 的 token 不计入损失，很多 target 其实是模型生成的。

Herd 里代码这条最具体：他们训了一个 code expert（主 run 分叉 CPT），再用 Llama 3 和这个专家合成对话，SFT 用了超过 $2.7\mathrm{M}$ 条合成代码样本。三种数据生成方式：

1. 强模型直接写指令-回答；
2. 执行反馈：跑测试、报错、让模型修，把能过单测的轨迹留下；
3. 系统提示和格式过滤，丢掉语法错误、指令没跟上的。

关键实验：8B / 70B 吃更大模型写的数据会涨；**405B 吃自己写的代码、没有执行信号，不涨甚至掉**。对旗舰而言，编译器和解释器提供了模型自己缺少的外部真值。没有可验证环境的开放域合成，旗舰很容易自我强化 hallucination。

写作、推理和工具等开放域不总有单测，公开流程则结合多模型 sampling、人类偏好、rejection sampling 和 DPO，没有披露的内部条数不作推断。安全拒答应走独立 policy model，见 `meta-llama-guard`，不要指望合成 SFT 单独把政策明确固定下来。

## 怎样检查泄漏和多样性

我会分别检查评测题面、教师指纹和种子来源：

1. **评测题面。** 教师在预训练里见过 GSM8k / HumanEval，prompt 稍一像就会默写。Herd 写预训练和后训练都做了去污染；后训练是和 benchmark prompt 做 exact match。因此在合成流水线出口还要跑评测 n-gram / 精确匹配，见 `meta-llama-eval`。
2. **教师指纹。** 学生变成教师的风格复制器。同族模型当 judge 会系统性偏爱自己的句式。交叉教师、人类抽检、和教师做 n-gram 重叠，比只看 BLEU 有用。
3. **种子泄漏。** 种子若来自公开指令集，扩写会把原题改写后送回。种子也要去污染。

大量生成 MMLU 风格的「下面哪项正确」选择题，再只报 MMLU 分数，可能混入格式适配和泄漏。Herd 的退火对照也提示，小模型从 benchmark 训练集得到的收益，不能直接当作更广泛的能力提升。

多样性方面，自指令容易出现模板坍缩：开头全是「请解释…」、代码全是 `def solution`、拒绝全是同一套道歉。条数到百万，有效任务族可能只有几十。

除了总条数，我会记录以下过滤和覆盖情况：

- 指令侧：embedding 近邻 / MinHash 去重，压长度极端值；
- 任务侧：用分类器或聚类看题型覆盖，刻意 upsample 长尾（多语言、工具、多轮）；
- 回答侧：过短、循环、拒答比例异常的丢掉；代码必须过执行；
- 训练侧：高质量源可以多 epoch，低质量源降 sampling。Herd 写他们按主题、难度、质量调 mix。

多样性靠种子和约束扩覆盖。只调高温度会增加随机性，未必增加题型覆盖。

合成 SFT 调整的是指令条件下的回答分布，与预训练退火和领域 CPT 的目标不同。相关：`meta-llama3-pretrain`、`meta-continual-pt`。

## 追问

**学生当教师行不行？**
8B 可以吃 405B；405B 吃自己，要有外部真值（执行、检索、人类）。没有真值就是在拟合自身错误。
**和 DPO 数据冲突吗？**
可以同源。SFT 用 rejection sampling 的胜者；DPO 用胜负对。注意 SFT 把分布收窄后，DPO 能探索的空间也变小。Llama 4 博客后来说轻量 SFT 再做 RL，就是怕 SFT 把模型锁死。
**合成数据能替代预训练吗？**
不能。它改的是指令条件分布，装不进 $15\mathrm{T}$ 的世界知识。领域知识不够先 CPT，再合成 SFT。
**怎么验收泄漏？**
公开榜、去重叠后的榜、私有变体三列一起报。合成集和评测的 n-gram 命中率要写进实验记录，不要口头说「做过去污染」。
