---
id: data-teacher-bias
section: data
order: 11
level: A
title: Synthetic Data 的 Teacher Bias 怎么检测？
quick: "先并排比较不同 teacher、temperature 和 prompt 生成数据的长度、n-gram、小标题、拒答率、错误类型和推理模式，看风格是不是锁死了。评价要换独立来源：其他教师、人类或可执行验证器。最后用这些数据分别训 student，看它是否学到了教师的捷径和偏差。"
tags:
  - Synthetic Data
  - Distillation
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: The False Promise of Imitating Proprietary LLMs
    url: https://arxiv.org/abs/2305.15717
    type: primary
---

我会分三步查：先看分布，比较不同教师、温度和模板生成的数据在风格上是不是锁死了；再换独立的评价源判对错；最后拿这些数据分别训学生做 ablation，看偏差有没有被蒸进去。只用同一个教师模型当 judge 是最常见的错误，那测的是「像不像它自己」，跟对不对无关。

举个例子，某个教师的回答看着都很好，可几乎每条都很长、带固定小标题，碰到安全相关的词就拒答，推理也总是同一种模板。把这种单一教师的输出当金标，学生模型（student）学到的更像一个风格分类器，任务边界却没学清楚。这件事和可学性（`data-strong-weak`）是两个维度：数据可学但有偏，照样会把坏的归纳蒸进去。

## 先看分布，再看正确率

并排比较不同 teacher、temperature、输入提示（prompt）模板在 length、n-gram、heading、拒答率、错误类型、reasoning pattern 上的直方图。换一个采样温度，长度和模板结构几乎不变，就说明风格锁死了。风格探针可以很便宜，heading 词表、平均句长、拒答触发词、代码格式化工具的指纹都行，不用一上来就训分类器。想量化的话，再训一个浅分类器识别 teacher source，很容易分开就说明数据带着很强的 signature。错误类型也要分开看：某个教师系统性地编引用，某个教师逢安全词就拒，这些都会变成学生的默认策略。

评价要独立。用 cross-teacher、人类抽检或可执行的验证器（verifier），别让生成数据的教师给自己打分。事实和代码类优先硬校验；开放生成才用另一家的 judge，并报告 judge 和人类的一致率。评测 prompt 也别复用教师的系统提示，否则奖励的是「像某家产品」。

## 学生 ablation 做最后判断

在相同的 token 预算下，分别用 teacher-A、teacher-B、混合、人类子集训学生，看目标分布、分布外数据（OOD，即与训练数据明显不同的数据）和风格塌缩。如果 A 只在「像 A」的评测上赢，换个模板或换个域就掉，就是偏差被蒸进去了。对照要做长度匹配，免得长教师靠 verbosity 赢。合成数据的占比和代数也要记账，没验证的多代回流会从偏差一路滑到自污染（`data-synthetic-self-contamination`）。

发现偏差以后，先把这个源的占比隔离出来，再做压缩或改写，马上换一家更强的闭源模型多半会重复同样的错误。混合教师时也别平均成另一种中庸腔，按任务来切：代码用带测试的教师，安全用更严的教师，开放聊天混人类数据。在监督微调（SFT）管线（`data-sft-pipeline`）里，教师只是候选生成器，能不能进训练看边际增益，跟来源品牌无关。只说「教师很强所以数据好」，等于没做检测。

## 追问

**分类器很容易认出教师，说明什么？**
说明风格 signature 太强，学生可能在学腔调。可以混教师、压缩模板，或者给这个源降权。

**最强的闭源教师一定最好吗？**
不一定。复现不了的超长推理和隐藏的工具依赖，会让小模型只学会表面格式，见 `data-strong-weak`。

**和评测泄漏怎么区分？**
偏差是训练分布被教师的口味染了色，泄漏是评测题被看见了。两者可以同时发生，门禁不一样。

**发现偏差后，先换教师还是先改评测？**
先把评测从这个教师那里独立出去，再做混合和压缩的 ablation。顺序反了，你可能「修好」的是一个本来就被污染的分数。
