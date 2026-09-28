---
id: openai-scaling-laws
section: openai
order: 18
level: S
title: OpenAI：Kaplan 和 Chinchilla 差在哪，compute-optimal 坐标别背错
quick: >-
  Compute-optimal 看的是等 FLOPs 曲线上 loss 最低的 $(N,D)$，不是「同样训 300B token、谁大谁好」。Kaplan 把更多
  compute 分给参数（$N\propto C^{0.73}$）；Chinchilla 参数和 token 近似均分（$N,D\propto C^{0.5}$），大约
  20 token/参数。20 是训练 FLOP 最优，不是推理最优。
tags:
  - OpenAI
  - Scaling
  - Chinchilla
  - Compute
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Scaling Laws for Neural Language Models
    url: https://arxiv.org/abs/2001.08361
    type: primary
  - title: Training Compute-Optimal Large Language Models
    url: https://arxiv.org/abs/2203.15556
    type: primary
  - title: Language Models are Few-Shot Learners
    url: https://arxiv.org/abs/2005.14165
    type: primary
  - title: GPT-4 Technical Report
    url: https://arxiv.org/abs/2303.08774
    type: primary
---

## 题怎么来的

Kaplan et al. 是 OpenAI 自己的 scaling 论文；Hoffmann et al. 的 Chinchilla 是 DeepMind 后来打脸「大模型少数据」那条 frontier。LLM 研究岗几乎必问。错法不是记不住公式，是把两张图的坐标轴混在一张嘴边：一张是固定 token 数看模型大小，一张是固定 FLOPs 看怎么分 $N$ 和 $D$。GPT-4 报告继续讲 scale，但不公开拟合系数，我会用 Kaplan / Chinchilla 的公开拟合答，不编内部曲线。

Transformer 的训练 FLOPs 近似

$$
C \approx 6ND,
$$

$N$ 是参数量，$D$ 是训练 token 数。2 来自前向的 matmul，反向大约再乘 2。这是数量级账，不是精确 profiler。白板我先写这行，再谈最优分配。

## 两套定律，两个最优

Kaplan 把 loss 分别拟成规模的幂律，例如非 embedding 参数

$$
L(N) = \bigl(N_c / N\bigr)^{\alpha_N},\qquad \alpha_N \approx 0.076.
$$

在 compute 预算下他们得到经验分配 $N_{\mathrm{opt}}\propto C^{0.73}$、$D_{\mathrm{opt}}\propto C^{0.27}$。含义：多出来的 FLOPs 大部分去堆参数，数据涨得慢，大模型在远没吃饱数据时就停。GPT-3 175B 吃约 300B token，正是这条思路。

Chinchilla 用三条独立路径（固定 FLOPs 扫 $N$、IsoFLOP 剖面、参数化拟合）收敛到同一句话：参数和 token 应一起加。拟合形如

$$
L(N,D)=E+\frac{A}{N^{\alpha}}+\frac{B}{D^{\beta}},
$$

再在 $C=6ND$ 上求最小。经验结果 $N_{\mathrm{opt}}\propto C^{0.5}$、$D_{\mathrm{opt}}\propto C^{0.5}$。70B 的 Chinchilla 吃 1.4T token；同算力的 Gopher 280B 只吃了 300B，是典型的「太大、太饿」。一个好记的比是约 20 token / 参数，来自 $1.4\mathrm{T}/70\mathrm{B}$，不是 Kaplan 主图的横轴。

按 Chinchilla，175B 的 compute-optimal 大约要 3.5T token，不是 GPT-3 的 300B。不要把 GPT-3 说成 Chinchilla-optimal。

轴不要背错：

1. 横轴是 $N$、所有点训相同 $D$。只说明「同样数据下更大模型更好」，每个点的 $C$ 不同，不是 compute-optimal。
2. IsoFLOP。 每条曲线固定 $C$，横轴 $N$（或 $D=C/(6N)$），谷底才是该预算下的最优宽度。Chinchilla 主结论来自这类图。
3. Loss vs compute 的 Kaplan 总图可以画很多模型，读点时必须看它训了多少 token。把 Chinchilla 70B 随便钉上去而不对 $D$，是常见口误。
4. 20 token/参数是训练 FLOP 最优附近的比，且随拟合细节漂。它不是「永远 20」。推理时小模型反复用，overtrain（8B 吃十几 T 那种）更划算：训练多花 token，服务省参数。
5. Kaplan 对 embedding 是否计入 $N$、学习率是否 cosine 到数据预算结束，Hoffmann 点名会影响「数据值不值」。面试提一句调度差异，比争论 $0.73$ 对 $0.50$ 的第三位小数有用。

数据重复之后，$D$ 不能按「看到的 token」和「独立 token」混用，见 `openai-data-mix`。评测涨点还要过污染，见 `openai-eval-harness`。

## 追问

- **为什么是 $6ND$ 不是 $2ND$？** $2ND$ 只算前向。训练还有反向，激活那条路上 matmul 大约再倍一倍。推理算力不是 $6ND$。
- **现在都 overtrain，Chinchilla 废了吗？** 没废。它回答「这块训练预算怎么分」。产品目标换成推理成本，最优会移到更小 $N$、更大 $D$。
- **Kaplan 说数据不重要？** 没有。他们有 $L(D)$，只是 compute-optimal 把指数分给 $N$ 更多。
- **GPT-4 的曲线能背吗？** 报告只有定性。白板用 Kaplan / Chinchilla 的公开拟合，声明假设。
