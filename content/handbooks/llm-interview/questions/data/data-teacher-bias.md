---
id: data-teacher-bias
section: data
order: 11
level: A
title: Synthetic Data 的 Teacher Bias 怎么检测？
quick: >-
  比较不同 teacher/temperature/prompt 生成的数据在 style、length、错误类型、n-gram、reasoning
  pattern 上的分布，并用 cross-teacher / human / verifier 做独立评价；最终用 student ablation
  看是否把 teacher shortcut 蒸馏进去。
tags:
  - Synthetic Data
  - Distillation
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: The False Promise of Imitating Proprietary LLMs
    url: https://arxiv.org/abs/2305.15717
    type: primary
---

Teacher 数据「看起来很好」往往带着固定腔调：过长、固定小标题、过度拒答、同一种推理模板。把单一教师的输出当金标，student 学到的是风格分类器，不是任务边界。陷阱是只用同一 teacher 当 judge——那是在测「像不像自己」，不是对不对。检测必须换独立评价源，并用 student ablation 看 shortcut 有没有被蒸进去。这和可学性（`data-strong-weak`）正交：可学但有偏，照样会把坏归纳蒸馏进去。

## 分布对照，而不是只看正确率

并排比较不同 teacher / temperature / prompt 模板在 length、n-gram、heading、拒答率、错误类型、reasoning pattern 上的直方图。若换一个采样温度，长度和模板结构几乎不变，说明风格锁死。实用探针：训练一个浅分类器识别 teacher source，若很容易分开，数据带强 signature。错误类型也要分：某教师系统性编造引用、某教师逢安全词就拒，这些会变成 student 的默认策略。

独立评价用 cross-teacher、人类抽检、或执行 verifier，不要让生成教师给自己打分。事实/代码类优先硬校验；开放生成才用另一家 judge，并报告 judge–human 一致率。

## Student ablation 才是终审

同样 token budget 下，teacher-A、teacher-B、混合、人类子集分别训 student，看目标分布、OOD、风格塌缩。若 A 只在「像 A」的评测上赢、换模板或换域就掉，就是 bias 被蒸进去了。对照要长度匹配，避免长教师赢在 verbosity。合成占比和代数要记账，无验证多代回流会从 bias 滑向自污染（`data-synthetic-self-contamination`）。

面试收口：先分布探针，再独立 verifier，最后 student 切片 ablation。只报「教师很强所以数据好」，等于没做检测。SFT 管线（`data-sft-pipeline`）里教师只是候选生成器，过门看边际增益，不看来源品牌。

风格探针可以很便宜：heading 词表、平均句长、拒答触发词、代码格式化工具指纹，不必一上来训分类器。分类器只是把「好认」量化。混合教师时不要平均成另一种中庸腔，而是按任务切：代码用带测试的教师，安全用更严的教师，开放聊天混人类。评测 prompt 禁止复用教师系统提示，否则你会奖励「像某家产品」。发现 bias 后先隔离该源占比，再做压缩/改写，而不是立刻换一家更强的闭源模型重复同一错误。

## 追问

- **分类器很容易认出教师说明什么？** 风格 signature 太强，student 可能在学腔调。应混教师、压缩模板、或降权该源。
- **最强闭源教师一定最好吗？** 不一定。不可复现的长链和隐藏工具依赖，会让小模型只学会表面格式。见 `data-strong-weak`。
- **和评测泄漏怎么分？** Bias 是训练分布被教师口味染色；泄漏是评测题被看见。可以同时发生，门禁不同。
- **发现 bias 后先换教师还是先改评测？** 先把评测从该教师独立出去，再做混合/压缩 ablation，否则你会「修好」一个被污染的分数。
