---
id: data-entropy-collapse
section: data
order: 7
level: S
title: Entropy collapse 一定是坏事吗？
quick: >-
  不一定。任务接近确定性最优时熵下降是收敛；危险的是成功率还没起来熵就掉，探索提前停。要并排看 entropy、pass 率、unique trajectory、clip fraction 和零方差组比例。采样温度当不了训练目标里的熵正则。
tags:
  - RL Debug
  - Exploration
  - Entropy
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary
  - title: The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models
    url: https://arxiv.org/abs/2505.22617
    type: secondary
---

这块容易看到熵曲线往下就喊「崩了」，或反过来把熵当唯一健康指标。策略熵是动作分布的不确定度

$$
H(\pi(\cdot\mid x))=-\mathbb{E}_{a\sim\pi(\cdot\mid x)}\big[\log\pi(a\mid x)\big],
$$

对 LLM 通常在 response token 上平均。任务本身接近确定性（标准答案、格式锁死）且已经会做时，低熵是收敛，不是事故。要判的是 **熵掉下去的时刻，成功有没有跟上**。

## 先看时序，再谈失败

把同一张图叠四条：token 熵、holdout 正确率 / pass@1、平均长度、组内 reward $\sigma$。

- 正确率已经高、熵缓降、长度稳定：正常收口。
- 正确率平台或在掉，熵却陡降：探索停了。后面 unique 轨迹变少、零方差组变多，GRPO 会空转，见 `byte-grpo-all-same-zero-adv`。
- 熵涨、长度暴涨、正确率不动：可能是胡话和重复在刷探索，不是「还在学」，见 `data-length-hacking`。

DAPO 把不健康的熵/长度上涨部分归因于 **sample-level loss 摊薄长序列里的坏 token**；改 token-level PG 和 clip-higher，就是让「该罚的重复」和「该放的稀有好 token」都能进梯度，见 `pt-dapo`。

## 早期塌缩常见原因

按「目标 / 采样 / 数据」三层说，不要只调一个温度。

- **目标。** 对称 clip 上界太紧，稀有正 token 梯度为 0；KL / entropy bonus 太弱；reward scale 过大，一步就把质量堆到当前众数上。
- **采样。** rollout `temperature` 过低，组内几乎是同一条；$G$ 太小更容易全对或全错。温度只改 **rollout 分布**，不进 $\nabla_\theta$，所以把温度调高 **代替不了** 训练里的熵正则。
- **数据。** 题过易，很快全对；过难，长期全错。两种都会让优势消失，策略在噪声上过拟合格式。

Entropy bonus 是 $\mathcal{L}\leftarrow\mathcal{L}-\lambda H(\pi)$，直接改 objective；采样温度是推理旋钮。面试被追「你怎么把熵拉回来」时，先说改了哪一层，不要说「我们温度调到 1.2」。

## 和谁一起看

最低监控集：success / pass@k、unique n-gram 或轨迹哈希、clip fraction、相对 $\pi_{\mathrm{old}}$ 和 $\pi_{\mathrm{ref}}$ 的 KL、平均长度、零方差组比例。缺 clip fraction 就看不见「正 token 是不是被 clip 吃掉」。缺 unique 轨迹，熵掉了你不知道是收敛还是模式坍缩。

旋钮先后见 `data-entropy-fix-order`：有效组 → clip / 学习率 → 长度 → 熵正则。有效组比例太低先改题难度和 $G$；clip fraction 长期贴上界就考虑 clip-higher 或减小学习率；长度 hack 用 overlong shaping 或预算评测，不要先加熵系数把模型写得更散。

## 追问

- **Entropy bonus 和 temperature 差在哪？** 前者在 loss 里奖励高熵策略；后者只改采样、不改梯度。用温度掩盖训练塌缩，一换成 greedy 评测就原形毕露。
- **确定性任务熵必须高吗？** 不必。最终答案峰可以尖；过程 token 仍可保留分支。要拆「答案熵」和「推理熵」，不要一个标量宣判。
- **和 DAPO clip-higher？** 正向上界太紧会加速塌缩；放宽是给新模式时间，不是熵的目标值。仍要看成功有没有跟上。
- **反向 KL / OPD 会不会更快塌？** 会。mode-seeking 目标（OPD、RLHF 的 ref KL）本身就锁主峰，见 `pt-kd-forward-vs-reverse`。那是设计，要用 gold 成功率和多样性一起验收，而不是单靠把熵拉高。
- **已经确认是坏塌，先动哪个旋钮？** 温度不是第一刀。顺序见 `data-entropy-fix-order`。
