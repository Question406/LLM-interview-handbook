---
id: dt-data-mix-quota
section: panel
order: 6
level: S
title: Panel：配比怎么定，怎么证明没有在背某一个源？
quick: "按任务缺口和难度分组分配 token 预算，用小规模配比实验或 mixing law 选初值。每个来源都留独立测试数据，再做移除某个来源的实验，并报告近重复污染率。只看总 loss，或凭经验固定为 1:1:1，都说明不了模型是否过拟合某个来源。"
companies:
  - apple
tags:
  - Apple
  - Data Mix
  - Curriculum
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Data Mixing Laws
    url: https://arxiv.org/abs/2403.16952
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: DataComp-LM
    url: https://arxiv.org/abs/2406.11794
    type: primary
---

我会按能力类别分配 token 预算，不能直接按磁盘目录大小决定。要检查是否背了主要来源，需要各来源独立留出测试数据，做 leave-one-source-out 实验，并检查近重复污染率。总 loss 下降无法代替这些证据。

不这么选的理由：Panel 很爱从「你们 mix 怎么定的」挖到过拟合。经验 1:1:1 对不上缺口。难例越多越好，小源会先过拟合。

## 配额是预算，不是文件大小

先按能力切桶：英语通用、数学、代码、多语、图文、工具。每桶一个 token 预算，来自冻结评测的缺口。AFM 把多语从 8% 提到 30%，是在改预算。视觉 mid 的 60 / 10 / 28.5 / 1.5 也是预算。

温度采样 $p_i\propto n_i^{\alpha}$ 只管桶内长尾，见 `dt-temp-mix-code`。Curriculum 管时间：先别把新配额打满。AFM 发现多语课程和全程 30% 收益相近，英语更安全。

Data Mixing Laws 给一个可讲的式子。固定模型与步数，域 $i$ 验证损失

$$
L_i(r)=c_i+k_i\exp\Big(\sum_j t_{ij} r_j\Big),
$$

$r$ 是比例，$t_{ij}<0$ 表示域 $j$ 帮域 $i$。小规模 sweep 拟合后再外推。后训练的 win-rate 不能直接套这条，人评和工具成功率仍要真实 sweep。

## 怎么证明没背主源

每源留 held-out，且和训练集做近重复去污。否则「该源 holdout 涨」只是背诵。

leave-one-source-out 是每次移除一个来源，检查相关任务的表现是否明显下降。如果只有该来源的题提高，而独立变体没有改善，就要怀疑过拟合。

再报近重复污染率、各桶 $\Delta$ 能力 / $\Delta$ token。

DataComp-LM 的方法同构：固定模型，只动数据。一次只改一维，绑定 `dataset_version`。同时改过滤、配比和奖励，飞轮不可复盘，见 `dt-data-flywheel`。

## 追问

- **新源只有 2 万条，配额怎么给？** 先按缺口给小配额，看边际 $\Delta$。条数少就过拟合，用温度和重复上限，不要为了「看起来重视」打到 20%。
- **代码和网页能共用质量模型吗？** 不能。网页教科书分类器会杀代码，见 `dt-quality-filter-code`。
- **配比每周变怎么归因？** 一周动一维。两周的 $\Delta$ 对不上版本，就当没做。
