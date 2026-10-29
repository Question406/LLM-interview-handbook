---
id: data-entropy-fix-order
section: data
order: 17
level: S
title: 熵塌了先动哪几个旋钮？温度为什么排最后？
quick: >-
  先确认熵下降时成功率没跟上，排除正常收敛。然后按顺序动：先让组里有可区分的奖励，再查 clip 与学习率，再管输出长度，最后才调 entropy
  regularization。温度只改轨迹 sampling、不改权重，排在最后；过早加大熵系数，会放大靠拉长输出拿奖励的行为和无关输出。
tags:
  - Entropy
  - RL Debug
  - DAPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24T00:00:00.000Z
sources:
  - title: >-
      The Entropy Mechanism of Reinforcement Learning for Reasoning Language
      Models
    url: 'https://arxiv.org/abs/2505.22617'
    type: primary
  - title: DAPO
    url: 'https://arxiv.org/abs/2503.14476'
    type: primary
  - title: SimKO — Simple Pass@K Policy Optimization
    url: 'https://arxiv.org/abs/2510.14807'
    type: secondary
---

顺序是先让组里有信号，再让好 token 有梯度，再管长度，最后才管探索的形状；温度排在最后，甚至可以不上清单。这题默认已经判断过，这是一次成功率没跟上的坏塌。熵掉了算不算坏事是另一道题，见 `data-entropy-collapse`，那边要把正确率、熵、长度、组内 $\sigma$ 叠起来看。这题面试官想听的是旋钮顺序。

举个例子，一个 GRPO run 熵掉得很快，大部分组的回答全对。这时候把温度调高、把熵系数加大，sampling 看起来是散开了，可组内奖励还是一样，优势还是 0，什么也学不到。要先解决的是题太简单。

## 按这个顺序动

第一步看有效组。零方差组比例高，GRPO 这一步本来就没有优势，见 `byte-grpo-all-same-zero-adv`。先改题目难度、$G$，或者上 DAPO 的动态 sampling，见 `pt-dapo`、`data-rlvr-select`。组内没有可区分的奖励，正则怎么调都补不出有效的任务学习信号。

第二步看 clip 和步长。clip fraction 长期贴着正向上界，说明少见的高质量 token 的更新被裁掉了，概率分布进一步往常见 token 上集中。先试 clip-higher，或者把学习率 / PPO epoch 降下来，见 `pt-rl-hparams-joint`。Entropy Mechanism（`2505.22617`）把熵变写成概率和 logit 更新的协方差：高概率且高优势的 token 在降熵。限制这些 token 的步长，比在整条损失（loss）上加一个 $\lambda H$ 更对症。

第三步看长度。熵掉的同时平均长度暴涨，先按长度 hacking 处理：overlong、GFPO 组内过滤、评测锁预算，见 `data-length-hacking`、`pt-gfpo`。这时候先加 entropy bonus，模型会写得更散、更长。

最后才动 entropy regularization：训练目标里的 $\lambda H(\pi)$、Clip-Cov / KL-Cov、SimKO 保 top-$K$ support，见 `fund-entropy-temp`、`pt-grpo-family-sapo-simko`。它们是在已经有有效梯度的基础上，调整策略对不同候选的概率分配。温度，比如 $T=1.2$ 的 sampling 轨迹（rollout），排在最后：评测一律用 greedy，训练里的塌缩就原形毕露。

## 别先动的几刀

最常见的是先加温度。温度只改这一次怎么抽，$\pi_\theta$ 没变，明天把 $T$ 调回去，权重还是尖的。先加大熵系数也不行：没有有效组时，高熵就是胡话；有长度 hack 时，高熵就是更长的套话。

先把 KL 加到很大也有问题。mode-seeking 的 ref KL 会把主峰锁死，见 `pt-kd-forward-vs-reverse`，熵已经塌了还加大 KL，只会加速收口。先换 GSPO / CISPO 同样解决不了根上的问题：它们改的是 $\rho$ 的粒度和 clip 形状，能间接减轻好 token 被掐死，可这批题全对或全错的时候，组是空的，换 clip 没用。

论文给过 $R\approx -a\exp(H)+b$ 这样的熵-分数经验关系。面试时讲清「性能是拿熵换来的，熵耗尽就到天花板」就够了，拟合系数不用背。

## 追问

**Clip-Cov / KL-Cov 什么时候上？**
有效组和 clip-higher 都处理过了，熵还在单调往下掉，再对高协方差 token 截梯度或者加 KL。别一上来就替换 PPO clip。

**pass@1 涨、pass@K 掉，是同一个问题吗？**
不完全是。那是候选的 support 塌了，要看另一套监控。SimKO 比加熵系数更对症，见 `pt-grpo-family-sapo-simko`。

**怎么验收这一刀有效？**
holdout pass@1 要动，unique 轨迹或 n-gram 回升，零方差组下降，长度没有趁机爆炸。只报「熵拉回来了」不够。
