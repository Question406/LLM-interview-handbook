---
id: dt-data-mix-quota
section: panel
order: 6
level: S
title: Panel：data mix 怎么定，怎么证明没有在背某一个源？
quick: >-
  按能力类别分配 token 预算，预算来自冻结评测上的缺口，初值用小规模 data mix 实验或 mixing law
  来定。要证明没背某个源，每个来源都留去过污的独立 test set，做 leave-one-source-out，并报 near-duplicates
  contamination rate。只看总 loss，或凭经验定 1:1:1，都说明不了问题。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Data Mixing Laws
    url: 'https://arxiv.org/abs/2403.16952'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: DataComp-LM
    url: 'https://arxiv.org/abs/2406.11794'
    type: primary
---

按能力类别分 token 预算，每个类别给多少看冻结评测上的缺口，和磁盘上各目录有多大没关系。要说明没在背某个主要来源，得每个来源单独留测试数据、做 leave-one-source-out、报 near-duplicates contamination rate，总 loss 下降代替不了这些证据。

举个例子，AFM 把 multilingual 从 8% 提到 30%，就是在改预算；视觉 mid 阶段的 60 / 10 / 28.5 / 1.5 也是预算。经验上的 1:1:1 和实际缺口对不上，hard examples 也不是越多越好，小来源会先 overfitting。Panel 很爱从「你们 mix 怎么定的」一路追问到 overfitting，就是想听这一套。

具体做法是先按能力切桶：英语通用、数学、代码、multilingual、图文、工具，每个桶一个预算。桶内的 long-tail 交给 temperature sampling $p_i\propto n_i^{\alpha}$ 去管（`dt-temp-mix-code`）。时间上用 curriculum，新配额先小后大，逐步加到目标值。AFM 发现 multilingual 走课程和全程 30% 收益相近，但课程对英语更安全。

## 初值怎么选

Data Mixing Laws 给了一个可以在面试里讲的式子。固定模型与步数，域 $i$ 的验证损失为

$$
L_i(r)=c_i+k_i\exp\Big(\sum_j t_{ij} r_j\Big),
$$

其中 $r$ 是各域的比例，$t_{ij}<0$ 表示域 $j$ 对域 $i$ 有帮助。先做小规模 sweep 拟合参数，再外推到目标规模。这条式子拟合的是验证损失，post-training 的 win-rate、human evaluation 和工具成功率还是要做真实 sweep。

## 怎么证明没背主源

我会先给每个来源都留 held-out，并且和 training set 做 near-duplicates decontamination，否则「该源 holdout 涨了」可能只是背诵。然后做 leave-one-source-out，每次拿掉一个来源，看相关任务的表现有没有明显下降。如果只有这个来源自己的题在涨，独立构造的变体没改善，就要怀疑 overfitting。最后报 near-duplicates contamination rate，以及每个桶的 $\Delta$ 能力 / $\Delta$ token。

整个过程和 DataComp-LM 的方法同构：固定模型，只动数据。一次只改一维，绑定 `dataset_version`；同时改过滤、data mix 和奖励，飞轮就没法复盘。

## 追问

**新来源只有 2 万条，配额怎么给？**
先按缺口给一个小配额，看边际 $\Delta$。条数少就容易 overfitting，用温度和重复上限控制，别为了「看起来重视」打到 20%。

**代码和网页能共用一个质量模型吗？**
不能。网页上训练的教科书风格分类器会把代码杀掉，见 `dt-quality-filter-code`。

**data mix 每周都在变，怎么 attribution？**
一周只动一维。两周的 $\Delta$ 对不上版本，就当这次实验没做。

**mixing law 拟出来的比例能直接用到 post-training 吗？**
不能直接用。它拟合的是验证损失，post-training 看的 win-rate、human evaluation 和工具成功率要单独 sweep。

相关：`dt-data-flywheel`、`dt-temp-mix-code`
