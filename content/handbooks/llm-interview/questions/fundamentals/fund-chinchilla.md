---
id: fund-chinchilla
section: fundamentals
order: 191
level: A
title: Chinchilla 计算最优是什么？过训和欠训怎么判断？
quick: >-
  固定 FLOP 预算 $C\approx 6ND$ 时，选 $N$ 和 $D$ 让损失最低。Kaplan 把更多算力分给参数；Hoffmann /
  Chinchilla 给出 $N$ 与 $D$ 近似同速涨，$D/N\approx 20$。同算力更大模型不总是更好。过训 / 欠训看
  $D/N$ 相对这条前沿，以及同 $C$ 换更小 $N$、更多 $D$ 会不会更低损。
tags:
  - Scaling Laws
  - Chinchilla
  - Compute
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Training Compute-Optimal Large Language Models
    url: https://arxiv.org/abs/2203.15556
    type: primary
  - title: Scaling Laws for Neural Language Models
    url: https://arxiv.org/abs/2001.08361
    type: secondary
---

常见误区是：「同样 FLOPs 下模型越大越好」。那是 Kaplan 口径的口头禅，被 Hoffmann / Chinchilla 用同算力对比推翻。本题先定义固定预算下的最优拆分，再谈过训、欠训。训练 FLOPs 的 $6ND$ 口算见 `infra-rl-mfu-6nd`；这里问的是 $N$ 和 $D$ 怎么配，不是 GPU 利用率。

## 固定 FLOP 下什么叫计算最优

一次完整训练（前向加反向）近似

$$
C \approx 6ND,
$$

$N$ 是参数量，$D$ 是 token 数。预算锁死时 $ND$ 近似常数：参数加一倍，token 就要减半。计算最优是在这条双曲线上挑一点，使验证损失最低，不是把卡全堆进更大的 $N$。

口试我先写 $C=6ND$，再声明「最优是 $(N,D)$ 的分配」。漏掉 $D$，只报「70B 比 10B 强」，比较的就不是同一笔算力。Attention 的 $T^2$ 项、MoE 稀疏、重计算都会修正 $6N$，面试数量级仍用 $6ND$。显存能不能放下是另一本账，见 `sys-memory`。

## Kaplan 和 Hoffmann 差在哪

Kaplan 等拟合当时的损失曲面，得到最优配置大约 $N_{\mathrm{opt}}\propto C^{0.73}$、$D_{\mathrm{opt}}\propto C^{0.27}$：新增算力大部分去加参数，数据涨得慢。按这个处方，大模型会相对欠训，参数很多，每个参数看到的 token 很少。GPT-3 级 175B 只吃约 300B token，$D/N\approx 1.7$，是这条路的典型点。

Hoffmann 等（Chinchilla）用三条独立路径（IsoFLOP 剖面、参数化损失拟合、以及把小模型训到收敛再外推）得到近似

$$
N_{\mathrm{opt}}\propto C^{0.5},\qquad D_{\mathrm{opt}}\propto C^{0.5},
$$

经验比例每个参数约 20 个 token。Chinchilla 70B 吃 1.4T token，与 Gopher 280B / 300B token 同算力，下游全面更好。结论：Gopher 不是不够大，是同样 $C$ 下 $N$ 太大、$D$ 太小。

白板对比就这一句：Kaplan 把边际算力给 $N$；Chinchilla 给 $N$ 和 $D$ 各一半。不要背「20」却说不出 $C$ 固定、$ND$ 互换。

## 过训、欠训怎么判断

相对 Chinchilla 前沿：

- 欠训：$D/N$ 明显小于约 $20$。同 $C$ 换成更小模型、更多 token，损失还应再降。症状是验证曲线仍陡、数据还没过第二遍就开始换更大 $N$。
- 过训：$D/N\gg 20$，例如 Llama 3 8B 吃 15T，$D/N$ 上千。按 Chinchilla 这是「算力本可以养一个更大的模型」；按推理成本这常常是故意的：小模型服务便宜，多花训练 FLOPs 换低延迟。

判断不要只报一个比值。更干净的是 IsoFLOP：固定 $C$，扫几档 $N$，看哪一档损失最低。最低点左边是欠训（$N$ 太大），右边是过训（$N$ 太小、数据相对过多）。重复数据、低质量 web 会让「名义 $D$」虚高，真正有效 token 更少，看起来过训、其实仍欠有效信号。

当代预训练普遍过训相对 Chinchilla，因为模型整个生命周期中的 decode 成本远大于再训一次。我会主动补这半句，否则会被追「那为什么没人训计算最优的 8B」。计算最优是训练预算的最优，不是训练加推理总账的最优。

## 追问

- **「更大一定更强」何时对？** 数据也按比例加、或预算不锁死时。锁死 $C$ 只加 $N$，Chinchilla 表明会亏。
- **20 是定理吗？** 经验拟合，随数据质量、重复、词表、MoE 稀疏会漂。用它当数量级，IsoFLOP 才是现场可画的判据。
- **MoE 怎么套？** $N$ 用激活参数估 FLOPs，总参数走显存。把 671B 全参数当 $6ND$ 的 $N$，算力会虚高一个数量级。
- **和 MFU 什么关系？** MFU 问这笔 $6ND$ 有没有打满 GPU；本题问 $N$ 与 $D$ 怎么拆。利用率高也可能在训一个欠训的大模型。
- **过训是失败吗？** 对纯训练损失的最优来说是偏离；对要部署的小模型常常是目标。先问对方锁的是训练预算还是服务成本。
