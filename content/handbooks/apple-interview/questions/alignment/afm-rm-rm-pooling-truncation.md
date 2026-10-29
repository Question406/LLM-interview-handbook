---
id: afm-rm-rm-pooling-truncation
section: alignment
order: 103
level: A
title: RM 实现排错：取了最后一个 padding token，为什么训练准确率仍很高？
quick: 我会先检查模型到底在给哪个位置打分，以及截断后两条回答是否还保留了真正的差别。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - Reward Modeling
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
---

## 面试官可能这样问

训练准确率很高，换个 padding 或模板就崩了，你先查什么？

## 可以这样回答

我会先把一个 batch 打印出来，看看 token、mask、截断位置和实际取来打分的位置。比如右侧补了 padding，却直接取最后一个位置，那读到的可能已经不是回答结束的位置。

训练准确率高并不能排除这种错误。假如好回答普遍更长，模型可能只学了长度或模板特征。我会先用同一条回答换不同 padding 长度，看分数会不会变；再查两条回答是不是截断以后已经一样，却仍然带相反标签。实现和数据先对上，再讨论模型容量。

## 技术备查

## 场景与问题
右 padding 的 batch 使用 hidden[:, -1] 打分，A 类回答更长；训练准确率 95%，新模板只剩 53%。怎么定位？

## 参考答案
先打印每条 token、attention mask、截断后的回答和被 pooling 位置。普通连续右 padding 可用有效长度减一找末 token；左 padding 或内部空洞不能直接照搬，应找实际最后有效下标。确认 EOS 是否有效、reward head 的 dtype、chosen/rejected 是否共享 prompt 与模板，以及截断是否截掉分歧位置。

做三个对照：相同回答不同 padding 长度奖励不变；仅更换无关模板不改变排序；互换长短分布后仍能识别真实错误。训练准确率高可能是长度或来源捷径，不说明 pooling 正确。若两条回答在截断后完全一样，应 re-annotation 或去掉该对，不应保留相反标签。

## 追问
**全 padding 怎么办？** 按数据契约拒收，不能把任意 padding 的状态当语义奖励。
**一定只能 EOS pooling 吗？** 不是；这是常见实现选择，其他 pooling 需要相同的有效位置契约和独立验证。

