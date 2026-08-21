---
id: byte-recall-at-5
section: fundamentals
order: 180
level: A
title: 字节实习一面：Recall@5 怎么算，评测过拟合怎么防？
quick: >-
  Recall@5 = 命中相关文档的 query 比例（或相关文档被召回的比例，先对齐定义）。过拟合：固定 dev、盲测
  holdout、定期换 query、看负例与位置偏差，不要只刷榜上那 200 条。
tags:
  - ByteDance
  - Eval
  - RAG
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 字节实习 agent开发一面
    url: https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“Recall@5 怎么计算？评测集刷高了怎么判断是过拟合？”**

陷阱是不先对齐定义就报一个数，或把整个库塞进 top-5 把召回刷到 $1$。$\mathrm{Recall}@5$ 只在 **相关文档有标注** 的离线集上有意义；没有金标、只有点击时会被位置偏差污染。适用场景是 RAG / 搜索召回（`fund-rag`），不是生成质量。Agent 还要补「召回对了但生成没用」的忠实度。pass@$k$ 是生成侧多次采样，不要和 Recall@$k$ 混名（`fund-passk`）。

## 两种定义，先问再用

**Query 级：** 一条 query 的 top-5 是否命中至少一条相关文档，再对 query 取平均。**文档级：** 相关文档里有多少被召回到 top-5（可再对 query macro）。例：100 条 query，80 条在 top-5 里至少命中一篇，则 query 级 $\mathrm{Recall}@5=0.8$。若某 query 有 3 篇相关、只召回 1 篇，query 级仍算命中，文档级只有 $1/3$。面试主动问用哪一种。多路召回场景见 `baichuan-three-path-recall`。

必须同时看 $\mathrm{Precision}@5$：只优化召回可以把噪声文档堆满。nDCG 才惩罚相关文档排太低；Recall@$k$ 不关心排序位置。

## 刷高了如何判断过拟合

信号：dev 升、线上投诉升；换同分布新 query 骤降；只对标注员爱用的关键词有效；索引或改写过拟合到那两百条榜题。防护：固定 dev、盲测 holdout、定期换 query、看负例与位置偏差；覆盖不足见 `pdd-offline-eval-coverage`。离线召回涨、线上采纳不涨，走 `data-offline-online-metric-gap`。提示词 / 检索超参迭代时冻结评测集。

失败模式：用点击当相关；$k$ 大到接近库大小；只报 Recall 不报 Precision 与人工抽检。

## 过拟合的操作定义和对照实验

「评测集刷高了」要能指出是哪一种过拟合。第一种是 **题面过拟合**：改写器、同义词表、或人工规则只对那 $200$ 条生效，换同分布新 query 骤降。第二种是 **索引过拟合**：为榜单文档加了特殊字段或重复入库。第三种是 **标注过拟合**：标注员爱用的关键词被模型记住，负例其实仍相关。对照实验：冻结系统，换一批同来源新 query；或把 gold 文档从索引里拿掉看分数是否仍高（泄漏）。定期轮换评测集，旧集降为回归、新集盲测。

位置偏差：用户只点第一位时，用点击当相关会高估排在前面的文档。没有人标时至少做 IPS / 随机化曝光，不要直接当 Recall。Agent 场景补忠实度：Recall@$5=1$ 仍可能生成没用到证据。多路召回要分路报 Recall，避免一路撑满、一路挂了看不见（`baichuan-three-path-recall`）。覆盖不足时榜很好、线上长尾崩（`pdd-offline-eval-coverage`）。

公式层面 query 级可写

$$
\mathrm{Recall}@k=\frac{1}{N}\sum_{i=1}^{N}\mathbf{1}\big[\mathcal{R}_i\cap\mathrm{Top}k(q_i)\neq\emptyset\big],
$$

文档级则对 $|\mathcal{R}_i\cap\mathrm{Top}k|/|\mathcal{R}_i|$ 再平均。先写定义再代入数字。

## 追问

- **和 nDCG 差在哪？** Recall@$k$ 只问进没进窗口；nDCG 看排得高不高。相关文档在第 $5$ 位和第 $1$ 位，Recall@$5$ 一样。
- **没有金标怎么办？** 先抽样人标再算；弱监督要点击位置纠偏，不能直接当 Recall。
- **Agent 只看 Recall 够吗？** 不够。还要忠实度与任务成功，召回只是上游。
- **如何证明没过拟合？** 盲测新 query + 与线上投诉同向；只有 dev 涨不够。
- **把 $k$ 开到 $100$ 刷 Recall 算优化吗？** 不算。必须看 Precision、延迟和生成噪声。拐点在 Recall–延迟曲线上。
