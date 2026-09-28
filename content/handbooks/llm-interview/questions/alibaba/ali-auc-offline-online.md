---
id: ali-auc-offline-online
section: alibaba
order: 32
level: A
title: AI Coding 压轴：离线 AUC 高、上线暴跌，如何从数据/标签/serving 归因？
quick: >-
  我会先查 train-serving skew、样本分布偏移、特征泄露、标签口径/延迟、标注噪声、模型与 feature schema
  不一致、在线缺失填充与精度差异。
tags:
  - Alibaba
  - Eval
  - AI Coding
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘宝闪购 Agent 算法一面
    url: 'https://www.nowcoder.com/discuss/879393838081597440'
    type: legacy-reference
---

错法：「过拟合」或「换个模型」。闪购 AI Coding 压轴要按数据/标签/serving 归因：离线 AUC 高、上线暴跌，常见根因是 train-serving skew、样本分布偏移、特征泄露、标签口径或延迟、标注噪声、模型与 feature schema 不一致、在线缺失填充与精度差异。用日志回放、特征监控、切片评估验证，而不是只猜。纯生成式 Agent 没有 AUC，不要硬套；但「离线集好看、线上掉」的思路仍然适用（对照 `data-offline-online-metric-gap`）。

## 先对齐特征和口径，再谈模型

有离线样本和在线日志、特征可对齐时，这条清单才跑得通。公开闪购面经给的排序：

1. Train-Serving 特征分布偏移；
2. 线上样本分布与训练不一致；
3. 特征泄露导致离线虚高；
4. 标签定义口径不一致；
5. Label delay；
6. 标注噪声放大；
7. 版本与 schema 未对齐；
8. 在线推理精度/缺失填充策略差异。

例子：离线用「成交后 7 天是否退货」当标签，却把成交后才有的「退货申请次数」当成特征，AUC 虚高。上线时该特征全是缺失，填充策略与训练不同，线上 AUC 塌。回放同一批请求、对比离线/在线特征值直方图，能直接钉死泄露和填充差异。

## 怎么证明是 skew，而不是「感觉分布变了」

对同一 `request_id` 对齐特征，算 PSI / JS 散度；再做对照实验：用在线特征重打离线分。若离线重打也掉，是 serving 特征变了；若离线重打仍高、线上低，才更像样本选择或标签口径。只看总体 AUC 会漏新用户/大促切片。线上用点击、离线用成交，口径根本不是同一个任务。先统一 $y$ 的定义。Agent 场景的「离线好看」常是固定评测集过拟合，线上工具超时和用户话术没覆盖，归因同构：分布、泄漏、口径（`ali-agent-eval-dims`、`ali-rag-eval`）。

## 标签延迟与噪声会放大一切

Label delay：训练用 T+7 成交，线上用实时点击代理，优化的不是同一目标。标注噪声在类别极偏时会把 AUC 撑得很好看（模型学到了「多数类」或泄露特征）。schema 未对齐（特征改名、离散桶边界变了）等价于静默 skew。精度差异：离线 float32、在线量化或 fp16，少数关键连续特征会漂。闪购压轴按上面顺序排，避免一上来「过拟合」。Agent 侧同构：离线固定话术集 success 高，线上工具超时、用户口误、大促话术没覆盖，看起来像「模型不行」，其实是分布和口径。先做 request 级对齐，再谈换模型或上 GRPO。

## 追问

- **PSI 多少算异常？** 没有普适阈值。看头部特征的相对变化，并结合「在线特征重打离线」对照，不要背 0.2。
- **没有 request_id 怎么办？** 先补日志对齐，否则无法证伪 skew，只能猜。
- **Agent 没有 AUC 怎么答？** 换成任务成功率 / 忠实度的离线/线上差，归因顺序不变：分布、泄漏、口径、延迟。
