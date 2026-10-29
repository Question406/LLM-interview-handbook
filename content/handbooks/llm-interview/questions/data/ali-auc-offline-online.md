---
id: ali-auc-offline-online
section: data
order: 32
level: A
title: AI Coding 压轴：离线 AUC 高、上线暴跌，如何从数据/标签/serving 归因？
quick: >-
  先拿同一请求对齐训练和线上的特征，看是不是 train-serving skew，再查样本分布、特征泄漏、label definitions
  和延迟、标注噪声、模型版本与 schema、在线缺失填充和数值精度。用日志回放和「在线特征重打离线分」把原因分开，别一上来就说 overfitting。
tags:
  - Alibaba
  - Eval
  - AI Coding
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ 淘宝闪购 Agent 算法一面
    url: 'https://www.nowcoder.com/discuss/879393838081597440'
    type: legacy-reference
---

离线 AUC 高、上线暴跌，我会按数据、标签、serving 去归因，用日志回放、特征监控和切片评估验证，不急着说「overfitting」或者「换个模型」。常见根因有 train-serving skew、样本分布偏移、特征泄露、label definitions 或延迟、标注噪声、模型与特征 schema 不一致、在线缺失填充与精度差异。

举个例子。离线用「成交后 7 天是否退货」当标签，却把成交后才有的「退货申请次数」当成特征，AUC 自然虚高。上线时这个特征全是缺失，填充策略又和训练不一样，线上 AUC 就塌了。回放同一批请求，对比离线和在线的特征值直方图，泄漏和缺失值填充差异都能直接看出来。

## 排查顺序

这条清单要有离线样本和在线日志、特征能对齐才跑得通。公开的闪购面经给的排序是：

1. Train-Serving 特征分布偏移；
2. 线上样本分布与训练不一致；
3. 特征泄露导致离线虚高；
4. label definitions 不一致；
5. Label delay；
6. 标注噪声放大；
7. 版本与 schema 未对齐；
8. 在线推理精度/缺失填充策略差异。

证明是 skew 靠对齐和对照，光凭「感觉分布变了」不行。对同一个 `request_id` 对齐特征，算 PSI / JS 散度；再用在线特征重打离线分。离线重打也掉，说明是 serving 特征变了；离线重打仍然高、线上低，就更像样本选择或者 label definitions 的问题。只看总体 AUC 会漏掉新用户、大促这类切片。

标签这边，线上用点击、离线用成交，本来就是两个任务，得先统一 $y$ 的定义。Label delay 也是同样的问题：训练用 T+7 成交，线上用实时点击当代理，优化的目标对不上。标注噪声在类别极偏的时候会把 AUC 撑得很好看，模型学到的是「多数类」或者泄露特征。

剩下两类比较隐蔽。schema 没对齐，比如特征改了名、离散 bucket boundaries 变了，效果等同于静默的 skew。精度差异是离线 float32、在线量化或 fp16，少数关键的连续特征会漂。

## 换成 Agent 场景

纯生成式 Agent 没有 AUC，别硬套，但「离线集好看、线上掉」的思路照样适用，对照 `data-offline-online-metric-gap`。Agent 的「离线好看」常常是固定评测集 overfitting：离线固定话术集 success 很高，线上工具超时、用户口误、大促话术都没覆盖，看起来像模型不行，其实是分布和定义的问题，归因同构：分布、泄漏、定义（`ali-agent-eval-dims`、`ali-rag-eval`）。先做 request 级对齐，再谈换模型或者上 GRPO。

## 追问

**PSI 多少算异常？**
没有普适阈值。看头部特征的相对变化，再结合「在线特征重打离线」的对照，别背 0.2。

**没有 request_id 怎么办？**
先补日志对齐。不然没法证伪 skew，只能猜。

**Agent 没有 AUC 怎么答？**
换成任务成功率或忠实度的离线 / 线上差，归因顺序不变：分布、泄漏、定义、延迟。
