---
id: ml101-duplicates
section: data
order: 13
level: A
title: "重复和近重复样本应该如何处理？"
quick: "先区分重复采集和真实重复事件，再做精确或近重复分组。评估独立泛化时，同源或近重复样本不能跨训练和测试；训练去重或降权要保留来源和频次信息，避免把业务分布里的真实频率一起抹掉。"
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Lee et al.: Deduplicating Training Data Makes Language Models Better"
    url: https://arxiv.org/abs/2107.06499
    type: primary
  - title: "scikit-learn: Cross-validation"
    url: https://scikit-learn.org/stable/modules/cross_validation.html
    type: primary
---

重复样本要先查来源，再决定删除、合并还是保留频次。重复上传同一事件会改变训练权重；高度相似的记录跨训练与测试，还会让模型通过记忆得到虚高分。语言模型去重研究展示了近重复文本、记忆和评估污染的关系，但具体任务仍要按自己的采样单位制定规则。[Lee et al.: Deduplicating Training Data Makes Language Models Better](https://arxiv.org/abs/2107.06499)。

精确重复可以先规范化字段，再按内容或事件键哈希分组。近重复则需要符合任务的相似性：文本模板、图片变体、同一原始文档的切片都可能需要同源标识。归一化不能抹掉会改变答案的信息，例如金额或否定词。

比如同一段客服对话被导出两次，训练留一份、测试留一份，就无法评价对新对话的泛化。应先建立重复组，再把组整体分配到集合。scikit-learn 的分组交叉验证也强调，相关群组要保持训练与验证隔离，才能测试未见群组的表现。[scikit-learn: Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)。

如果两笔不同订单恰好拥有相同特征，它们可能是真实独立事件，不能只因行内容相同就删除。可以保留事件键、来源、原始次数及处理理由，单独报告去重前后分布，确认没有把稀有任务或高频业务不成比例地移除。

## 追问

**去重应该在切分前还是后？**
用于识别跨集合污染的分组应在切分时就考虑，保证同一组不跨边界。最终还要检查集合间近重复，避免漏掉变体。

**同样的输入有不同标签怎么办？**
先查是否缺少决定标签的上下文、是否关联错行或标注冲突。把它们直接合并成一个标签，可能隐藏真正的问题。

**近重复阈值越严格越好吗？**
不一定。如果相似度达到门槛就判成重复，门槛过高会漏掉重复样本，门槛过低又会把本来不同的例子误合并。需要用人工检查的相似与不相似样本定阈值，并抽查边界案例。
