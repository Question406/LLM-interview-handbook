---
id: meta-synth-sft
section: meta
order: 19
level: A
title: Meta：合成 SFT 数据——自指令、教师模型、泄漏和多样性
quick: >-
  Llama 3 后训练大量用模型写 SFT：自指令扩题、强教师写答、执行反馈筛代码。405B 吃自己的代码轨迹没有执行信号会掉点。泄漏看评测题面、教师指纹、模板坍缩，不要只报条数。
tags:
  - Meta
  - Llama
  - SFT
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Self-Instruct — Aligning Language Models with Self-Generated Instructions
    url: https://arxiv.org/abs/2212.10560
    type: primary
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: secondary
  - title: Introducing Llama 3.1
    url: https://ai.meta.com/blog/meta-llama-3-1/
    type: primary
---

Llama 后训练岗很少问「SFT 的全称」。会问：合成数据从哪来、教师是谁、怎么防把 MMLU 写进训练集。Self-Instruct 给了社区骨架；Herd 论文给了 Meta 公开做法。别把合成 SFT 说成预训练退火（`meta-llama3-pretrain`），也别说成 CPT（`meta-continual-pt`）。

## 管道长什么样

Self-Instruct：少量人工种子指令 → 模型写新指令 → 过滤太像的 → 再写回答 → 再过滤。Llama 3 把这套放大，并且**迭代**：每一轮后训练用最新模型产数据，再 SFT + DPO。论文写 SFT 目标仍是标准 CE，prompt token 不进 loss，很多 target 其实是模型生成的。

Herd 里代码这条最具体：他们训了一个 code expert（主 run 分叉 CPT），再用 Llama 3 和这个专家合成对话，SFT 用了超过 $2.7\mathrm{M}$ 条合成代码样本。三条产数路：

1. 强模型直接写指令-回答；
2. 执行反馈：跑测试、报错、让模型修，把能过单测的轨迹留下；
3. 系统提示和格式过滤，丢掉语法烂、指令没跟上的。

关键实验：8B / 70B 吃更大模型写的数据会涨；**405B 吃自己写的代码、没有执行信号，不涨甚至掉**。所以「教师」对旗舰不是另一台更大的 Llama，而是编译器 / 解释器。没有可验证环境的开放域合成，旗舰很容易自我强化幻觉。

开放域（写作、推理、工具）没有单测。公开叙事是多模型采样、人类偏好、拒绝采样、DPO。面试说「合成 + 过滤 + 偏好」，不要编内部条数。安全拒答应走独立策略模型，见 `meta-llama-guard`，不要指望合成 SFT 单独把政策钉死。

## 泄漏

合成数据不是天生干净。三条泄漏：

1. **评测题面。** 教师在预训练里见过 GSM8k / HumanEval，prompt 稍一像就会默写。Herd 写预训练和后训练都做了去污染；后训练是和 benchmark prompt 做 exact match。面试要说：合成流水线出口必须再跑一遍评测 n-gram / 精确匹配，见 `meta-llama-eval`。
2. **教师指纹。** 学生变成教师的风格复制器。同族模型当 judge 会系统性偏爱自己的句式。交叉教师、人类抽检、和教师做 n-gram 重叠，比只看 BLEU 有用。
3. **种子泄漏。** 种子若来自公开指令集，扩写会把原题改写后送回。种子也要去污染。

错法：用 MMLU 风格的「下面哪项正确」模板海造选择题，再在 MMLU 上报分。那是在训格式，不是在训知识。Herd 退火实验已经警告：小模型会吃训练集，大模型吃了也不该当能力。

## 多样性

自指令最常见的死法是**模板坍缩**：开头全是「请解释…」、代码全是 `def solution`、拒绝全是同一套道歉。条数到百万，有效任务族可能只有几十。

我会报这些过滤，而不是报「我们生成了 N 条」：

- 指令侧：embedding 近邻 / MinHash 去重，压长度极端值；
- 任务侧：用分类器或聚类看题型覆盖，刻意 upsample 长尾（多语言、工具、多轮）；
- 回答侧：过短、循环、拒答比例异常的丢掉；代码必须过执行；
- 训练侧：高质量源可以多 epoch，低质量源降采样。Herd 写他们按主题、难度、质量调 mix。

多样性不是「温度调高」。温度高只是更吵，题型还是那些。要从种子和约束上扩覆盖。

## 追问

- **学生当教师行不行？** 8B 可以吃 405B；405B 吃自己，要有外部真值（执行、检索、人类）。没有真值就是在拟合自身错误。
- **和 DPO 数据冲突吗？** 可以同源。SFT 用拒绝采样的胜者；DPO 用胜负对。注意 SFT 把分布收窄后，DPO 能探索的空间也变小。Llama 4 博客后来说轻量 SFT 再 RL，就是怕 SFT 把模型锁死。
- **合成数据能替代预训练吗？** 不能。它改的是指令条件分布，装不进 $15\mathrm{T}$ 的世界知识。领域知识不够先 CPT，再合成 SFT。
- **怎么验收泄漏？** 公开榜、去重叠后的榜、私有变体三列一起报。合成集和评测的 n-gram 命中率要写进实验记录，不要口头说「做过去污染」。
