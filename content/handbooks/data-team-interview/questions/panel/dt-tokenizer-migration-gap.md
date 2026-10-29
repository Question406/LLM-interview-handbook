---
id: dt-tokenizer-migration-gap
section: panel
order: 49
level: A
title: Panel 情景：换 tokenizer 后 loss 更低，为什么 multilingual 能力和 long context 都退化？
quick: >-
  假设换 tokenizer 后平均 token loss 更低，但同一段文本被切成了不同数量的 tokens。两个 loss
  的单位已经变化，不能直接比较谁更好。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - AFM 加练第二批
  - 情景练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: PyTorch Dataset and DataLoader
    url: 'https://docs.pytorch.org/docs/2.14/data.html'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

原创训练 debugging 题，建议 35 分钟。你更换 tokenizer 后，平均 token loss 下降，multilingual 问答却掉点。训练仍限制每条 4096 tokens，旧缓存中有预先分词的样本和角色 mask。tool calls 的结构化字段也更容易出错。

请列出优先级最高的排查步骤，并说明在什么证据出现前不应该立刻追加 multilingual 数据。数字为练习约定。

## 回答思路

> **问题与场景：** 假设换 tokenizer 后平均 token loss 更低，但同一段文本被切成了不同数量的 tokens。
>
> **做法与原因：** 我会固定原始文本，检查各语言的切分长度、未知或异常切分，以及相同 token window 实际能容纳多少内容。
>
> **检查与取舍：** 最终用相同任务、按真实输入长度分层评估质量与成本。

## 可以这样回答

假设换 tokenizer 后平均 token loss 更低，但同一段文本被切成了不同数量的 tokens。两个 loss 的单位已经变化，不能直接比较谁更好。

我会固定原始文本，检查各语言的切分长度、未知或异常切分，以及相同 token window 实际能容纳多少内容。也要核对 special tokens、packing 和模型权重迁移。

最终用相同任务、按真实输入长度分层评估质量与成本。Tokenizer 变化会影响有效上下文和训练预算，不能只看一个 loss。

## 技术备查

## 解题思路与参考答案

每 token loss 的计量单位已经改变，不能直接判断变好。先固定原始文本和评价范围，用一致的字节数或其他明确定义的长度 normalization 比较 negative log likelihood，且说明特殊 token、encoding 和 sequence segmentation 的处理；这仍不是所有能力的替代指标。

### 先查 pipeline 一致性

检查输入 ID、vocabulary embedding、输出 head、特殊 token 映射和缓存版本。旧 token ID 不能按新 vocabulary 解释；旧角色 mask 也不能按位置直接复用。缓存应关联 tokenizer 的明确版本与配置，迁移时重新分词和对齐。抽几条工具对话打印 token、角色、label 和 shift，检查 JSON 分隔、EOS 与工具标记。

### 再查分布与长度

按语言统计相同原文的 token 数、截断比例、有效回答保留率和每条训练的原始字节覆盖。相同 4096 tokens 在不同语言与 tokenizer 下能容纳的内容不同，可能截断关键证据或回答。固定 token 预算的实验也可能改变实际覆盖的文档量，应分别报告计算预算和原文覆盖。

### 如何定位真实能力变化

先用干净重分词缓存和正确 mask 做最小对照，再比较长度匹配、证据完整的 multilingual 测试与原 long context 测试。若工具格式错误在修映射后恢复，根因主要是接口；若只有某些语言的覆盖变少，再针对长度或 sampling 改数据。不能把映射错误靠追加样本“训练回来”。

## 面试追问

**统一为每字节 loss 就完全公平吗？** 仍需同一原文、sequence segmentation 和 probability definition，并且它不直接衡量工具成功或推理质量。使用它只是避免每 token 单位不同的误导。

**能复用旧 embedding 吗？** 相同 token ID 的语义不一定相同，需按 vocabulary 内容与初始化策略处理，不能凭下标直接复用全部参数。

**最小可靠检查？** 对一条短样本，人工核对 decode、role separation、有效 label 和第一个预测目标，先证实 pipeline 含义正确。
