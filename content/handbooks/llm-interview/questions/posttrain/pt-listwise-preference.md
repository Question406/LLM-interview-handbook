---
id: pt-listwise-preference
section: posttrain
order: 233
level: A
title: List-wise preference 相对 pairwise DPO 多提供了什么信息？
quick: "List-wise 多给的是同一个提示下的名次结构：一次对 $K$ 个候选排序或算 Plackett-Luce 似然，第二名离第一名多近、难负例排第几都进了监督，一对 $(y_w,y_l)$ 编码不了这些。代价是标注更贵，对平局和位置偏差更敏感；只有稀疏 pair 或 $K=2$ 时，退回直接偏好优化（DPO）就行。"
tags:
  - Preference Learning
  - DPO
  - Ranking
  - LiPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: LiPO — Listwise Preference Optimization through Learning-to-Rank
    url: https://arxiv.org/abs/2402.01878
    type: primary
---
List-wise 多出来的是同一个输入提示下的名次结构。pairwise 只说 $y_w\succ y_l$，至于 $y_l$ 是第二名还是第八名、第二名是不是和第一名差不多好，它都不知道；list-wise 对 $y_1,\ldots,y_K$ 建模完整排序，这些都进了似然。但它不是一定比 DPO 强，标注更贵，对位置偏差和裁判的长度偏好也照样敏感。

比如同一道题采了 8 个 rollout，排出 $1\succ 2\succ\cdots$。list-wise 可以一边把第 8 名狠狠压下去，一边保留 2、3 名相对第 1 名那点细小的间隔。拆成 pair 的话，这些强弱不同的信息就被拉平了。

## Plackett-Luce 比 pair 多了什么

$$
P(\sigma\mid x)=\prod_{k=1}^{K}\frac{\exp(s_{x,y_{\sigma(k)}})}{\sum_{j=k}^{K}\exp(s_{x,y_{\sigma(j)}})}.
$$

$s$ 可以是隐式 reward，也可以是 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$。每一步都在剩下的集合里做一次 softmax，所以「第 2、第 3 名相对第 1 名的间隔」和「第 8 名被压低」是强度不同的监督。把全排序拆成 $\binom{K}{2}$ 个独立的 pair，会引入构造上的依赖，放大弱胜，还会把「第二名接近第一名」这个信息冲淡。LiPO 那篇把学习排序里的 listwise 损失（ListNet / ListMLE / LambdaLoss 一族）接到了语言模型上，按名次差给梯度加权，top 附近排错比尾部排错罚得更重。

这正好补上 pairwise 直接偏好优化（DPO）的盲区。只有稀疏 pair 或者 $K=2$ 的时候，硬上 list-wise 没有额外信息，只会多一份噪声，退回 DPO 就行。它也要和「一个正样本配多个负样本」分开：多负例 pairwise 还是只约束 $y^+\succ y_i^-$，负例之间的顺序识别不出来，只有 list-wise 的似然才在剩余集合里比较负例。分数 $s$ 直接用奖励模型（RM）的标量，会把 RM 的尺度误差写进名次，用策略对数比更稳，优化和对齐目标是一致的。

## 什么时候值得上

值得上的条件是 $K$ 比较大、人或裁判能给出稳定的排序或近似分数、同一个 $x$ 有多样的采样轨迹（rollout）。这时候 list-wise（LiPO、PRO）能把难负例用起来。

采样先要保证候选之间真有区分度，温度太低会得到 $K$ 条近乎重复的回答，排序就成了噪声，所以先过滤掉 n-gram 重叠高的再标。标注员对长列表很难给出全序，噪声和位置偏差（先看到的打分偏高）都会进模型，要随机打乱位置、做长度匹配。长度偏差在列表里更危险，最长的那条往往被排第一，要么做长度匹配，要么把长度当成单独一维，别让 $s$ 偷偷编码 verbosity。$K$ 太大时后段名次不可靠，可以截断到 top-$k$ 或者给尾部降权。平局别硬排，Plackett-Luce 假设严格全序，把「差不多好」拧成名次，就造出了假的间隔。

离线排序 AUC、NDCG 很好看，也可能只是刷了裁判的口味，线上任务成功率没动，这和 `data-offline-online-metric-gap` 是同一类问题。我一般先问 $K$ 多大、标注协议怎么定、位置偏差怎么去，再谈换目标。没有名次结构的话，list-wise 只是更贵的 pairwise。

## 和 pairwise DPO 怎么分工

同一个输入提示上已经有稳定全序、而且 $K\ge 4$，list-wise 当主损失；只有 pair，或者 pair 来自不同的输入提示，就别硬拼成假列表。混合数据也可以一起用，有全序的走 Plackett-Luce，只有 pair 的走 DPO，梯度都落在隐式 $s$ 上，是兼容的。多负样本 DPO（每个负例只和同一个正例比）也别当成 list-wise，那些负例之间还是识别不出顺序。评测要跟着匹配，训的是 list-wise，却只报 pairwise win-rate，就看不到名次校准学没学到。最终还是看线上任务成功，离线 NDCG 只当门禁。

## 追问

**把排序拆成所有 pair，等价吗？**
不等价。独立 pair 的似然忽略了列表上的归一化，弱 pair 会淹没强间隔，而且 pair 之间有构造依赖。

**$K$ 怎么选？**
小了没有名次信息，大了标注不稳、尾部噪声大。常见是 4-8，再给尾部降权。

**平局怎么处理？**
Plackett-Luce 假设全序，平局要显式标成 tie 或者直接丢掉，别强行排序。

**离线指标涨了，线上一定涨吗？**
不一定。离线 NDCG 或排序 AUC 涨了，还是要看任务成功率，见 `data-offline-online-metric-gap`。
