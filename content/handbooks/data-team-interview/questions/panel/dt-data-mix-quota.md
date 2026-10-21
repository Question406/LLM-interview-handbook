---
id: dt-data-mix-quota
section: panel
order: 6
level: S
title: Panel：配比怎么定，怎么证明没有在背某一个源？
quick: "按能力类别分配 token 预算，预算来自冻结评测上的缺口，用小规模配比实验或 mixing law 选初值。要证明没背某个源，每个来源都留去过污的独立测试集，做 leave-one-source-out，并报告近重复污染率。只看总 loss，或凭经验定 1:1:1，都说明不了问题。"
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

我会按能力类别分配 token 预算，每个类别给多少由评测上的缺口决定，和磁盘上各目录有多大无关。要检查是否在背某个主要来源，需要各来源独立留出测试数据、做 leave-one-source-out 实验，并检查近重复污染率。总 loss 下降代替不了这些证据。

Panel 很爱从「你们 mix 怎么定的」一路追问到过拟合。经验上的 1:1:1 和实际缺口对不上；难例也不是越多越好，小来源会先过拟合。

## 配额是预算

先按能力切桶：英语通用、数学、代码、多语、图文、工具。每个桶一个 token 预算，预算来自冻结评测上的缺口。AFM 把多语从 8% 提到 30%，就是在改预算；视觉 mid 阶段的 60 / 10 / 28.5 / 1.5 也是预算。

桶内和时间维度还有两件事要管。温度采样 $p_i\propto n_i^{\alpha}$ 只管桶内的长尾，见 `dt-temp-mix-code`。Curriculum 管时间：新配额先小后大，逐步加到目标值。AFM 发现多语走课程和全程 30% 收益相近，但课程对英语更安全。

## 初值怎么选

Data Mixing Laws 给了一个可以在面试里讲的式子。固定模型与步数，域 $i$ 的验证损失为

$$
L_i(r)=c_i+k_i\exp\Big(\sum_j t_{ij} r_j\Big),
$$

其中 $r$ 是各域的比例，$t_{ij}<0$ 表示域 $j$ 对域 $i$ 有帮助。先做小规模 sweep 拟合参数，再外推到目标规模。这条式子拟合的是验证损失，后训练的 win-rate、人评和工具成功率仍要做真实 sweep。

## 怎么证明没背主源

第一步，每个来源都留 held-out，并且和训练集做近重复去污。否则「该源 holdout 涨了」可能只是背诵。

第二步，做 leave-one-source-out：每次移除一个来源，看相关任务的表现是否明显下降。如果只有该来源自己的题在涨，独立构造的变体没有改善，就要怀疑过拟合。

第三步，报告近重复污染率，以及每个桶的 $\Delta$ 能力 / $\Delta$ token。

整个过程和 DataComp-LM 的方法同构：固定模型，只动数据。一次只改一维，绑定 `dataset_version`。如果同时改过滤、配比和奖励，飞轮就没法复盘，见 `dt-data-flywheel`。

## 追问

- **新来源只有 2 万条，配额怎么给？** 先按缺口给一个小配额，看边际 $\Delta$。条数少就容易过拟合，用温度和重复上限控制，别为了「看起来重视」打到 20%。
- **代码和网页能共用一个质量模型吗？** 不能。网页上训练的教科书风格分类器会把代码杀掉，见 `dt-quality-filter-code`。
- **配比每周都在变，怎么归因？** 一周只动一维。两周的 $\Delta$ 对不上版本，就当这次实验没做。
