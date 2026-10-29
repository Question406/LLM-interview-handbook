---
id: fund-chinchilla
section: fundamentals
order: 191
level: A
title: Chinchilla 计算最优是什么？过训和欠训怎么判断？
quick: >-
  计算最优是在固定 FLOP 预算 $C\approx 6ND$ 下挑 $N$ 和 $D$ 的拆分，让损失最低。Kaplan
  把更多算力分给参数；Hoffmann / Chinchilla 给出 $N$ 与 $D$ 近似同速涨，$D/N\approx
  20$，所以同算力下更大的模型不总是更好。过训 / 欠训看 $D/N$ 相对这条前沿的位置，最干净的判据是同 $C$ 换更小 $N$、更多 $D$
  损失会不会更低。
tags:
  - Scaling Laws
  - Chinchilla
  - Compute
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Training Compute-Optimal Large Language Models
    url: 'https://arxiv.org/abs/2203.15556'
    type: primary
  - title: Scaling Laws for Neural Language Models
    url: 'https://arxiv.org/abs/2001.08361'
    type: secondary
---
Chinchilla 计算最优说的是：训练算力锁死时，参数量 $N$ 和 token 数 $D$ 该怎么拆才能让损失最低，答案是两者近似同速增长，大约每个参数 20 个 token。「同样 FLOPs 下模型越大越好」是 Kaplan 定义的老说法，被 Hoffmann / Chinchilla 用同算力对比推翻了。过训、欠训就是看实际的 $D/N$ 落在这条前沿的哪一边。训练 FLOPs 的 $6ND$ 口算见 `infra-rl-mfu-6nd`，这题问的是 $N$ 和 $D$ 怎么配，跟 GPU 利用率无关。

## 固定 FLOP 下什么叫计算最优

一次完整训练（前向加反向）的算力近似是

$$
C \approx 6ND,
$$

$N$ 是参数量，$D$ 是 token 数。预算锁死时 $ND$ 近似是常数，参数翻一倍，token 就要减半。计算最优就是在这条双曲线上挑一个点，让验证损失最低，把卡全堆给更大的 $N$ 未必是最好的那个点。

口试时我会先写 $C=6ND$，再声明「最优是 $(N,D)$ 的分配」。漏掉 $D$、只说「70B 比 10B 强」，比的就不是同一笔算力。Attention 的 $T^2$ 项、MoE 稀疏、重计算都会修正 $6N$，但面试里估数量级仍然用 $6ND$。显存放不放得下是另一本账，见 `sys-memory`。

## Kaplan 和 Hoffmann 差在哪

Kaplan 等拟合当时的损失曲面，得到最优配置大约是 $N_{\mathrm{opt}}\propto C^{0.73}$、$D_{\mathrm{opt}}\propto C^{0.27}$：新增的算力大部分拿去加参数，数据涨得慢。按这个处方，大模型会相对欠训，参数很多，每个参数看到的 token 很少。GPT-3 级的 175B 只吃了约 300B token，$D/N\approx 1.7$，就是这条路的典型点。

Hoffmann 等（Chinchilla）用三条独立路径（IsoFLOP 剖面、参数化损失拟合、把小模型训到收敛再外推）得到近似

$$
N_{\mathrm{opt}}\propto C^{0.5},\qquad D_{\mathrm{opt}}\propto C^{0.5},
$$

经验比例是每个参数约 20 个 token。Chinchilla 70B 吃了 1.4T token，和 Gopher 280B / 300B token 用的是同一笔算力，下游全面更好。也就是说，Gopher 的问题出在同样 $C$ 下 $N$ 太大、$D$ 太小。

白板上一句话对比就够：Kaplan 把边际算力给 $N$，Chinchilla 给 $N$ 和 $D$ 各一半。光背「20」、说不出 $C$ 固定时 $N$ 和 $D$ 此消彼长，会被追问卡住。

## 过训、欠训怎么判断

欠训是 $D/N$ 明显小于约 $20$。同样的 $C$ 换成更小的模型、更多的 token，损失还能再降。症状是验证曲线仍然很陡、数据还没过第二遍就开始换更大的 $N$。

过训是 $D/N\gg 20$，比如 Llama 3 8B 吃了 15T token，$D/N$ 上千。按 Chinchilla 看，这笔算力本可以养一个更大的模型；但从推理成本看，这常常是故意的：小模型服务便宜，多花训练 FLOPs 换低延迟。

判断时别只报一个比值。更干净的做法是 IsoFLOP：固定 $C$，扫几档 $N$，看哪一档损失最低。最低点左边是欠训（$N$ 太大），右边是过训（$N$ 太小、数据相对过多）。重复数据和低质量网页会让名义上的 $D$ 虚高，有效 token 其实更少，看起来过训，实际上有效信号仍然不够。

当代预训练相对 Chinchilla 普遍是过训的，因为模型整个生命周期里的 decode 成本远大于多训一次的成本。这半句我会主动补上，不然会被追问「那为什么没人训计算最优的 8B」。计算最优是训练预算下的最优，没把训练加推理的总账算进去。

## 追问

**「更大一定更强」什么时候成立？**
数据也按比例加，或者预算没锁死的时候。锁死 $C$ 只加 $N$，Chinchilla 表明会亏。

**20 是定理吗？**
是经验拟合，会随数据质量、重复、vocabulary、MoE 稀疏而漂移。拿它当数量级用，现场能画的判据是 IsoFLOP。

**MoE 怎么套这套公式？**
算 FLOPs 时 $N$ 用激活参数，总参数只影响显存。把 671B 全参数当成 $6ND$ 里的 $N$，算力会虚高一个数量级。

**和 MFU 什么关系？**
MFU 问的是这笔 $6ND$ 有没有打满 GPU，这题问 $N$ 和 $D$ 怎么拆。利用率很高，也可能是在高效地训一个欠训的大模型。

**过训算失败吗？**
对纯训练损失的最优来说是偏离，对要部署的小模型来说常常就是目标。先问清对方锁的是训练预算还是服务成本。
