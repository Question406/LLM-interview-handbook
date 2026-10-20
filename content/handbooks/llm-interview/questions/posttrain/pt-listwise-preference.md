---
id: pt-listwise-preference
section: posttrain
order: 233
level: A
title: List-wise preference 相对 pairwise DPO 多提供了什么信息？
quick: "一次对 $K$ 个候选给出排序或 Plackett-Luce 似然，能利用名次与难负例，而不仅是一对 $(y_w,y_l)$。 标注更贵，对平局与位置偏差更敏感；只有稀疏 pair 或 $K=2$ 时退回 直接偏好优化（DPO） 即可。"
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

常见误区是：「list-wise 一定比 DPO 强」，或「把排序拆成所有 pair 就等价」。Pairwise 只说 $y_w\succ y_l$，丢掉同一输入提示 下其余候选的名次与间隔。List-wise 对 $y_1,\ldots,y_K$ 建模完整排序，名次靠前的难负例和「第二名也很好」都会进似然；但标注更贵，对位置偏差和裁判长度偏好仍然敏感。信息增益来自同一输入提示 的名次结构。

## Plackett-Luce 比 pair 多了什么

$$
P(\sigma\mid x)=\prod_{k=1}^{K}\frac{\exp(s_{x,y_{\sigma(k)}})}{\sum_{j=k}^{K}\exp(s_{x,y_{\sigma(j)}})}.
$$

$s$ 可以是隐式 reward 或 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$。每一步都在剩余集合里做 softmax，因此第 2、第 3 名相对第 1 的间隔和第 8 名被压低，是不同强度的监督。把全排序拆成 $\binom{K}{2}$ 个独立 pair 会引入构造依赖、放大弱胜，并把「第二名接近第一」冲淡。LiPO 把学习排序的 listwise 损失（ListNet / ListMLE / LambdaLoss 一族）接到语言模型上，用名次差加权梯度，让 top 附近的错排比尾部错排更疼。

这正好补上 pairwise 直接偏好优化（DPO） 的盲区：一对 $(y_w,y_l)$ 不编码「$y_l$ 是第二名还是第八名」。若只有稀疏 pair 或 $K=2$，退回 DPO 即可，硬上 list-wise 没有额外信息，只多噪声。和「一个正样本配多个负样本」也要分开：多负例 pairwise 仍然只约束 $y^+\succ y_i^-$，负例之间的序不可识别；list-wise 的似然才在剩余集合里比较负例。分数 $s$ 若直接用 奖励模型（RM） 标量，会把 RM 的尺度误差写进名次；更稳的是用策略对数比，让优化和对齐目标一致。

## 何时值得上、何时只是更贵的 pairwise

条件：$K$ 较大、人类或裁判能给稳定排序或近似分数、同一 $x$ 有多样 采样轨迹（rollout）。此时 list-wise（LiPO、PRO）能用上难负例。采样要先保证候选真有区分度：温度过低会得到 $K$ 条近重复，排序变成噪声；过滤 n-gram 重叠后再标。标注员对长列表很难给全序，噪声和位置偏差（先看到的偏高）会进模型，需要随机打乱位置、长度匹配。

这和 `data-offline-online-metric-gap` 同类：离线排序 AUC / NDCG 很好，可能只是刷了裁判口味，线上任务成功不动。同一题 8 个 rollout 排出 $1\succ 2\succ\cdots$：list-wise 压低第 8 名同时保留 2、3 相对 1 的细间隔。$K$ 过大时后段名次不可靠，可截断 top-$k$ 或对尾部降权。平局不要强行全序：Plackett-Luce 假设严格排序，把「差不多好」拧成名次会制造假间隔。

长度偏差在 list 里更危险，最长的往往被排第一，必须做长度匹配或把长度当独立维，而不是让 $s$ 偷偷编码 verbosity。

我一般先问 $K$、标注协议和位置 debias，再谈换目标。没有名次结构，list-wise 只是更贵的 pairwise。

## 和 pairwise DPO 怎么分工

同一输入提示 上已经有稳定全序、且 $K\ge 4$ 时，list-wise 是主损失；只有 pair、或 pair 来自不同一输入提示，不要硬拼成假列表。混合数据可以：有全序走 Plackett-Luce，只有 pair 走 DPO，梯度在隐式 $s$ 上兼容。不要把「多负样本 DPO」（每个负例只相对同一个正例）当成 list-wise，那些负例之间仍不可识别。评测也要匹配：训练 list-wise 却只报 pairwise win-rate，会看不到名次校准有没有学到。线上仍以任务成功为准，离线 NDCG 只是门禁。

## 追问

- **拆成所有 pair 等价吗？** 不等价。独立 pair 似然忽略列表归一化，弱 pair 会淹没强间隔，还有构造依赖。
- **$K$ 怎么选？** 小了没名次信息，大了标注不稳、尾部噪声。常见 4-8，并对尾部降权。
- **平局怎么处理？** Plackett-Luce 假设全序；平局应显式 tie 或丢掉，不要强行排序。
- **和线上指标？** 离线 NDCG / 排序 AUC 涨了仍要看任务成功，见 `data-offline-online-metric-gap`。
