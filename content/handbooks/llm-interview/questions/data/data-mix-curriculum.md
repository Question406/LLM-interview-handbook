---
id: data-mix-curriculum
section: data
order: 212
level: S
title: SFT / RL 的多源数据配比与 Curriculum 怎么定，如何证明没有 overfitting 某一源？
quick: >-
  配比和课程都靠实验定：先按任务价值和难度分组给配额，用温度 sampling 或 mixing law
  试几种配比，课程从通过率高的短轨迹逐步转到长程难例。要证明没 overfitting 某一源，就看每个源各自的留出集、拿掉单一来源的对照和近重复污染率，总
  loss 下降说明不了这件事。
tags:
  - Data Mix
  - Curriculum
  - SFT
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Data Mixing Laws
    url: 'https://arxiv.org/abs/2403.16952'
    type: primary
---

配比我会当成一组可以回放的实验来定：先按领域、任务和难度分组，给每组一个初始配额，再扫几种配比看各组的留出集怎么变；课程就是让难度跟着当前策略的通过率往上走。要证明没 overfitting 某个源，靠的是按源留出、拿掉单个源的对照和污染率这三样，「经验 $1:1:1$」或者「难例越多越好」都说服不了面试官。

举个例子，SFT 里如果模板化的短指令有几十万条，可验证的数学难例只有几千条，按条数一比一混，短模板会把难例淹掉，因为条数不等于有效梯度。这时候总 loss 照样往下走，可能只是模型更熟悉那个大源了。

## 配比怎么定，课程怎么排

做法是质量过滤以后，按领域、任务、难度配额抽样，再用温度 sampling 调长尾：$p_i \propto n_i^{\alpha}$，$\alpha$ 越小，长尾抬得越高。想省掉盲扫，可以用 Data Mixing Laws。那篇发现固定模型规模和步数时，域 $i$ 的验证损失可以写成

$$
L_i(r)=c_i+k_i\exp\Big(\sum_j t_{ij} r_j\Big),
$$

其中 $r_j$ 是训练域比例，$t_{ij}\lt 0$ 表示域 $j$ 在帮域 $i$。先在小规模上扫几组配比、拟合出这条曲线，再去预测大规模的 mix。这条定律拟合的是预训练的域损失，拿来预言 SFT win-rate 或 RL 成功率就不准了，后训练目标更稀疏、标签更噪，所以还得按任务 held-out 做小规模的真实 sweep，定律只给初值，以及哪些域会互相伤害的先验。SFT 另外还要盯遗忘：主源在涨，regression performance（通用指令、安全、格式）在下降，说明新数据在挤占已有能力，没有补上模型原本容易失败的任务。

课程学习说一句「先简单后难」不够，要讲清它防的是什么。SFT 先放格式和高置信的短样本，再把难例的 sampling 温度提上去。RL 从高通过率、短轨迹开始，慢慢过渡到低通过率的长程 agent 任务。一开始全是做不出来的题，组内全错，advantage 全是零，就没有学习信号；只加难例、又没有验证器（verifier）和课程，学到的就是噪声。所以每个桶都要看非零 advantage 的比例，全对或全错都该调 sampling，加条数解决不了。

RL 的配比还会自己变。用当前 actor 估各个桶的 pass@$1$ 和非零 advantage 率，难度标签每周更新一次；配比 $r$ 定死不动的话，策略变强以后很多桶会变成全对。难例要落在当前策略能探索到的区间里，否则课程只是多加了一堆没信号的训练。说到底，比例是实验跑出来的结果，开始时只是个假设。

## 怎么证明没有 overfitting 某一源

我会按这个顺序拿证据。第一，每个源单独留 held-out，并且和训练集做近重复去污（`data-contamination`），否则「这个源的 holdout 涨了」可能只是在背。第二，做 leave-one-source-out 或者配比 sweep，看拿掉主源以后相邻能力会不会塌；如果只有主源的分在涨，邻域和私有变体都不动，那就是 overfitting 了。第三，报告近重复污染率和每组的 $\Delta$ 能力 / $\Delta$ token，总 loss 不算证据。对照组至少要有等比例、按缺口加权、按质量加权和 curriculum 这几种。overfitting 的防法和 `meituan-sft-overfit` 是同一套，模板重复多了，配比实验就会变成在比谁背得多。

每次改配比都要绑定 `dataset_version`，能回放，才能把涨跌归到配比上。

## 追问

**为什么不用固定的 $1:1:1$？**
因为条数不等于有效梯度。短模板会淹没难例，比例应该看 holdout 的缺口、token 效率和 mixing law 的预测来定，拍一个整数比说明不了什么。

**只加难例会怎样？**
没有课程、没有 verifier 的话，RL 组内全错，SFT 学到噪声。先保证每个桶有非零 advantage 或者可验证的标签，再抬难度温度。

**怎么向面试官证明没背主源？**
按源 held-out、leave-one-source-out、近重复污染率，三样都拿出来。缺任何一样，都只能说明总榜好看。

**这题和快手、阶跃那两题有什么区别？**
那两题带场景约束：快手题（`kuaishou-sft-source-mix`）是 SFT 来源配比，阶跃题（`stepfun-agent-data-mix`）是 Agent RL 的工具桶。这题讲通用流程：分组统计、拟合或扫配比、按切片证明。场景题里的数字就是这套方法的实例。

**配比一周一变，怎么归因？**
一次只动一维，同时绑定 `dataset_version` 和环境 hash。奖励、过滤和 mix 一起动，就分不清是谁让分涨的。
