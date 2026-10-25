---
id: data-entropy-collapse
section: data
order: 7
level: S
title: Entropy collapse 一定是坏事吗？
quick: "不一定。任务接近确定性最优解、成功率也跟上了，熵下降就是收敛；成功率还没提高熵就快速下降，才是探索过早停了。要把 entropy、通过率、不同轨迹的数量、clip fraction 和零方差组比例放在一起看。调高采样温度替代不了训练目标里的熵正则。"
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

不一定。任务本身接近确定性，比如有标准答案、格式锁死，模型也已经会做了，这时熵低是收敛，算不上事故。要判断的是熵掉下去的那个时刻，成功率有没有跟上。

策略熵衡量动作分布的不确定程度：

$$
H(\pi(\cdot\mid x))=-\mathbb{E}_{a\sim\pi(\cdot\mid x)}\big[\log\pi(a\mid x)\big],
$$

对 LLM 通常是把回答里各 token 的熵取平均。看到熵曲线往下就喊「崩了」不对，反过来把熵当唯一的健康指标也不对。

## 先看时序

我会把 token 熵、留出集正确率 / pass@1、平均长度、组内奖励分数（reward）的标准差 $\sigma$ 叠在同一张图上看。正确率已经高了，熵缓慢下降，长度稳定，一般就是正常收敛。正确率卡在平台上甚至在掉，熵却陡降，说明探索停了，接下来 unique 轨迹会变少、零方差组变多，GRPO 开始空转，见 `byte-grpo-all-same-zero-adv`。还有一种是熵在涨、长度暴涨、正确率不动，这多半是胡话和重复在刷探索，模型并没有在学，见 `data-length-hacking`。

DAPO 把不健康的熵和长度上涨，部分归因于按样本平均的损失摊薄了长序列里坏 token 的惩罚。它改成 token-level PG 再加 clip-higher，就是让「该罚的重复」和「该放的稀有好 token」都能进梯度，见 `pt-dapo`。

## 早期塌缩的常见原因

我会按目标、采样、数据三层去说，别只调一个温度。

目标这层，对称 clip 的上界太紧，稀有正 token 的梯度就是 0；KL / entropy bonus 太弱；reward scale 太大，一次更新就把大量概率堆到当前最常见的输出上。

采样这层，采样轨迹（rollout）的 `temperature` 太低，一组里几乎是同一条；$G$ 太小也更容易全对或全错。温度只改 rollout 的采样分布，不直接改 $\nabla_\theta$ 对应的训练目标，所以调高温度代替不了训练里的熵正则。Entropy bonus 是 $\mathcal{L}\leftarrow\mathcal{L}-\lambda H(\pi)$，直接改 objective；采样温度只是推理时的旋钮。面试被追问「你怎么把熵拉回来」，先说改的是哪一层，别回答「我们把温度调到 1.2」。

数据这层，题太容易，很快全对；太难，长期全错。两种都会让优势消失，策略就在噪声上过拟合格式。

## 和哪些指标一起看

最低的监控集是 success / pass@k、unique n-gram 或轨迹哈希、clip fraction、相对 $\pi_{\mathrm{old}}$ 和 $\pi_{\mathrm{ref}}$ 的 KL、平均长度、零方差组比例。缺了 clip fraction，就看不到正优势 token 的梯度有没有被 clip 截掉；缺了 unique 轨迹，熵掉了你分不清是收敛还是模式坍缩。

确认是坏塌之后，旋钮的先后见 `data-entropy-fix-order`：有效组 → clip / 学习率 → 长度 → 熵正则。有效组比例太低，先改题目难度和 $G$；clip fraction 长期贴着上界，考虑 clip-higher 或减小学习率；长度 hack 用 overlong shaping 或预算评测来管，别先加熵系数，那只会让模型写得更散。

## 追问

**Entropy bonus 和 temperature 差在哪？**
前者在 loss 里奖励高熵策略，后者只改采样、不改梯度。拿温度掩盖训练里的塌缩，一换成 greedy 评测，原来的塌缩照样会露出来。

**确定性任务的熵必须高吗？**
不必。最终答案的峰可以很尖，过程 token 仍然可以保留分支。要把「答案熵」和「推理熵」拆开，一个熵标量判断不了。

**DAPO 的 clip-higher 起什么作用？**
正向上界太紧会加速塌缩，放宽是给新模式留时间，它并不设定熵的目标值。成功率有没有跟上还得看。

**反向 KL / OPD 会不会塌得更快？**
会。mode-seeking 的目标，比如 OPD、基于人类反馈的强化学习（RLHF）里的 ref KL，本身就锁主峰，见 `pt-kd-forward-vs-reverse`。这是设计使然，验收要用 gold 成功率和多样性一起看，单靠把熵拉高不行。

**已经确认是坏塌，先动哪个旋钮？**
别先调温度。顺序见 `data-entropy-fix-order`。
