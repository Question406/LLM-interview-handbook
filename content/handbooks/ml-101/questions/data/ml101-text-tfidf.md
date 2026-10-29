---
id: ml101-text-tfidf
section: data
order: 11
level: A
title: 词袋和 TF-IDF 怎么表示文本？
quick: >-
  词袋先建 vocabulary，把文档表示成各词的计数，忽略词序；TF-IDF 再提高文档内常见、语料中较少见的词的相对权重。vocabulary 和
  IDF 只从训练语料拟合，验证与线上共用同一映射，中文还要明确分词或字符粒度。
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: Feature extraction'
    url: 'https://scikit-learn.org/stable/modules/feature_extraction.html'
    type: primary
---

词袋把每篇文本变成 vocabulary 上的计数向量，TF-IDF 则在计数基础上降低到处出现的词的相对影响。这样可以把不同长度的文本变成固定维度、通常很稀疏的数值特征，接上线性分类器或检索模型。scikit-learn 的文本特征指南介绍了计数、TF-IDF 和 normalization 的具体实现。[scikit-learn: Feature extraction](https://scikit-learn.org/stable/modules/feature_extraction.html)。

比如 vocabulary 是「退款、延迟、发货」，文本「退款 退款 延迟」就表示成 `[2,1,0]`。词袋不保留顺序，因此「可以退款」和「不可以退款」可能因为共同词很多而看起来接近；加入词组特征可以补一部分局部顺序。

TF 表示某词在当前文档中的频率，IDF 表示这个词在整个语料中有多稀少。以 scikit-learn 的一种默认平滑写法为例，未做向量 normalization 前：

$$
\operatorname{tfidf}(t,d)=\operatorname{count}(t,d)\left[\log\frac{1+N}{1+\operatorname{df}(t)}+1\right].
$$

这里 $N$ 是训练文档数，$\operatorname{df}(t)$ 是包含词 $t$ 的训练文档数。假设几乎每份工单都有「您好」，只有少数涉及「退款」，IDF 会让后者有更高的相对权重；它表达区分度，不能保证这个词一定对标签有用。后续还可对每篇向量做 L2 normalization，减少长度差异。

## 追问

**测试文档可以一起算 IDF 吗？**
标准独立评测里不可以。vocabulary、词频阈值和 IDF 都在训练集拟合，测试只做转换，避免提前利用测试分布。

**没见过的词怎么办？**
固定 vocabulary 通常会忽略它；可以改用字符 n-gram 或哈希表示等方案，但要在同一评测条件下比较，并考虑 vocabulary 更新。

**TF-IDF 能理解同义词吗？**
它主要匹配共享词或词组，同义词没有共同特征时很难对齐。需要这类能力时可以和语义表示比较或结合，保留精确匹配的优点。
