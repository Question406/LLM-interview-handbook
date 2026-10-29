---
id: byte-recall-at-5
section: fundamentals
order: 180
level: A
title: 字节实习一面：Recall@5 怎么算，评测 overfitting 怎么防？
quick: >-
  Recall@5 有两种算法：query 级看每条 query 的 top-5 里有没有至少一篇相关文档再取平均，文档级看相关文档有多少进了
  top-5，报数前先对齐用哪种，并同时看 Precision@5。判断 overfitting 就换一批同分布的新 query 盲测、把 gold
  文档从索引里拿掉查泄漏，再看和线上投诉是否同向；固定 dev、定期轮换评测集，别只刷榜上那 200 条。
tags:
  - ByteDance
  - Eval
  - RAG
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 字节实习 agent开发一面
    url: 'https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604'
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“Recall@5 怎么计算？评测集刷高了怎么判断是 overfitting？”**

$\mathrm{Recall}@5$ 有两种算法，报数前要先对齐用哪种：query 级看每条 query 的 top-5 里有没有命中至少一篇相关文档，再对 query 取平均；文档级看相关文档里有多少被召回进了 top-5。判断是不是 overfitting，最直接的办法是换一批同分布的新 query 盲测，分数骤降就是 overfitting。

用个数例说两种定义的差别。100 条 query，80 条在 top-5 里至少命中一篇，query 级 $\mathrm{Recall}@5=0.8$。某条 query 有 3 篇相关文档、只召回 1 篇，query 级算命中，文档级只有 $1/3$（可以再对 query 做 macro 平均）。写成公式，query 级是

$$
\mathrm{Recall}@k=\frac{1}{N}\sum_{i=1}^{N}\mathbf{1}\big[\mathcal{R}_i\cap\mathrm{Top}k(q_i)\neq\emptyset\big],
$$

文档级则对 $|\mathcal{R}_i\cap\mathrm{Top}k|/|\mathcal{R}_i|$ 再平均。面试时我会先写定义再代入数字，并主动问用哪一种。

这个指标有几个前提。它只在相关文档有标注的离线集上有意义；只有点击、没有金标时，会被 position bias 污染，用户只点第一位，拿点击当相关就会高估排在前面的文档。没有人标时，先抽样人标再算，弱监督至少做 IPS 或随机化曝光的点击位置纠偏。它衡量的是检索增强生成（RAG）和搜索的召回（`fund-rag`），和生成质量无关；pass@$k$ 是生成侧的多次 sampling，别和 Recall@$k$ 混名（`fund-passk`）。报 Recall 时还要同时报 $\mathrm{Precision}@5$ 和人工抽检，只优化召回可以把噪声文档堆满；nDCG 才惩罚相关文档排得太低，Recall@$k$ 不管排序位置。把 $k$ 开得接近库的大小，召回能刷到 $1$，毫无意义。多路召回要分路报 Recall，免得某一路占满结果、掩盖另一路的失败（`baichuan-three-path-recall`）。

再说 overfitting。「评测集刷高了」要能指出是哪一种。第一种是题面 overfitting：改写器、同义 vocabulary 或者人工规则只对那 $200$ 条生效，换同分布的新 query 就骤降。第二种是索引 overfitting：为榜单文档加了特殊字段，或者重复入库。第三种是标注 overfitting：模型记住了标注员爱用的关键词，负例其实也相关。对照实验有两个：冻结系统，换一批同来源的新 query；或者把 gold 文档从索引里拿掉，看分数是不是还很高，还高就是泄漏。其他信号还有 dev 升、线上投诉也升。

防护上，固定 dev、留一个盲测 holdout、定期换 query，旧集降为回归集、新集做盲测，同时看负例和 position bias。prompt 和检索超参迭代时冻结评测集。覆盖不足时，榜单很好看，线上长尾查询却表现很差（`pdd-offline-eval-coverage`）；离线召回涨、线上采纳不涨，按 `data-offline-online-metric-gap` 去查。Agent 场景还要补忠实度，Recall@$5=1$ 时生成照样可能没用到证据。

## 追问

**和 nDCG 差在哪？**
Recall@$k$ 只问相关文档进没进窗口，nDCG 看排得高不高。相关文档排在第 $5$ 位和第 $1$ 位，Recall@$5$ 是一样的。

**Agent 只看 Recall 够吗？**
不够。召回只是上游，还要看忠实度和任务成功。

**怎么证明没有 overfitting？**
新 query 盲测，并且和线上投诉的方向一致。只有 dev 涨不够。

**把 $k$ 开到 $100$ 刷 Recall，算优化吗？**
不算。要同时看 Precision、延迟和生成噪声，拐点在 Recall 对延迟的曲线上。
