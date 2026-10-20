---
id: data-entropy-fix-order
section: data
order: 17
level: S
title: 熵塌了先动哪几个旋钮？温度为什么排最后？
quick: "先确认熵下降时成功率没有提高，排除正常收敛。再依次检查有效组、clip 与学习率、输出长度，最后调整熵正则。温度主要改变轨迹采样，不能作为首选修复。过早加大熵系数，可能放大靠增加长度获取奖励的行为，以及无关输出。"
tags:
  - Entropy
  - RL Debug
  - DAPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models
    url: https://arxiv.org/abs/2505.22617
    type: primary
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary
  - title: SimKO — Simple Pass@K Policy Optimization
    url: https://arxiv.org/abs/2510.14807
    type: secondary
---

「熵掉了怎么办」和「熵掉了一定是坏事吗」不是同一题。后者见 `data-entropy-collapse`：先叠正确率、熵、长度、组内 $\sigma$。本题假定已经判定是成功没跟上的塌，面试官要的是旋钮顺序，不是再背一遍监控图。

## 现场顺序

1. **有效组。** 零方差组比例高，GRPO 这一步本来就没有优势，见 `byte-grpo-all-same-zero-adv`。先改题难度、$G$、DAPO 动态采样，见 `pt-dapo`、`data-rlvr-select`。组内没有可区分的奖励时，调整正则也无法补出有效的任务学习信号。
2. **clip 和步长。** clip fraction 长期贴正向上界：较少出现的高质量 token 更新被裁剪，概率分布进一步集中到常见 token 上。先试 clip-higher 或把学习率 / PPO epoch 降下来，见 `pt-rl-hparams-joint`。Entropy Mechanism（`2505.22617`）把熵变写成概率与 logit 更新的协方差：高概率且高优势的 token 在降熵。限制这些 token 的步长，比把整条 损失（loss） 加一个 $\lambda H$ 更对症。
3. **长度。** 熵掉的同时平均长度暴涨，先按长度 hacking 处理：overlong、GFPO 组内过滤、评测锁预算，见 `data-length-hacking`、`pt-gfpo`。不要先加熵奖励，模型会写得更散、更长。
4. **最后才动熵正则。** 训练目标里的 $\lambda H(\pi)$、Clip-Cov / KL-Cov、SimKO 保 top-$K$ support，见 `fund-entropy-temp`、`pt-grpo-family-sapo-simko`。它们在已有有效梯度的基础上，调整策略对不同候选的概率分配。温度、$T=1.2$ 的 采样轨迹（rollout），排在这张清单的最后，甚至可以不上清单：评测一切 greedy，训练塌缩原形毕露。

现场口令：先让组里有信号，再让正 token 有梯度，再管长度，最后才管探索形状。

## 不要做的第一刀

- **先加温度。** 只改这一次怎么抽，不改 $\pi_\theta$。明天把 $T$ 调回去，权重还是尖的。
- **先加大熵系数。** 没有有效组时，高熵就是胡话；有长度 hack 时，高熵就是更长的套话。
- **先把 KL 加到很大。** mode-seeking 的 ref KL 会把主峰锁死，见 `pt-kd-forward-vs-reverse`。熵已经塌了再加大 KL，是在加速收口，不是在修复。
- **先换 GSPO / CISPO。** 它们改 $\rho$ 的粒度和 clip 形状，能间接减轻「好 token 被掐死」，但替代不了「这批题全对全错」。组空了换 clip 没有用。

论文给过 $R\approx -a\exp(H)+b$ 这种熵-分数经验关系。面试讲「性能是拿熵换来的、熵耗尽就到天花板」，不要背拟合系数。

## 追问

- **Clip-Cov / KL-Cov 什么时候上？** 有效组和 clip-higher 之后仍单调掉熵，再对高协方差 token 截梯度或加 KL。不要一上来替换 PPO clip。
- **pass@1 涨、pass@K 掉呢？** 那是候选 support 塌了，不是同一张监控。SimKO 比加熵系数更对症，见 `pt-grpo-family-sapo-simko`。
- **怎么验收这刀有效？** holdout pass@1 要动；unique 轨迹或 n-gram 回升；零方差组下降；长度没有借机爆炸。只报「熵拉回来了」不够。
