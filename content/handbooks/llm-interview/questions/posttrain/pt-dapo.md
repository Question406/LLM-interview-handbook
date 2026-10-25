---
id: pt-dapo
section: posttrain
order: 19
level: S
title: DAPO 四个关键修改分别解决什么？
quick: "DAPO 还是组相对优势，改的是四处工程失败：Clip-Higher 单独放宽正向上界，给稀有的好 token 留出涨的空间；动态采样丢掉全对或全错的零方差组；token 级平均让每个 token 等权；超长部分用软惩罚，不在截断处直接把奖励打成零。"
tags:
  - DAPO
  - GRPO
  - Clip-Higher
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: DAPO — Decoupled Clip and Dynamic sAmpling Policy Optimization
    url: https://arxiv.org/abs/2503.14476
    type: primary
---

DAPO 仍然用 GRPO 的组相对优势，它改了四个地方：clip 的上界、哪些组算有效样本、损失（loss） 怎么归约、超长怎么惩罚。每一处修的是一种工程上的失败，所以别答成「又一个优势公式」或者「去掉 KL 的 GRPO」。小红书真题卡 `xiaohongshu-dapo-vs-grpo` 问的是同一件事，这里把四个旋钮拆开，每个都能在白板上写出公式。

## Clip-Higher：单独放宽正向上界

PPO / GRPO 的对称 clip 是 $\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)$。$A\gt 0$ 且 $\rho\gt 1+\varepsilon$ 时这一项梯度为 0。比如模型偶然写出一个低概率但正确的推理步骤，它的 $\rho$ 一涨就顶到上界，马上拿不到梯度了，熵更容易塌，见 `data-entropy-collapse`。DAPO 把上下界拆开：

$$
\mathrm{clip}\big(\rho_t,\;1-\varepsilon_{\mathrm{low}},\;1+\varepsilon_{\mathrm{high}}\big),\qquad \varepsilon_{\mathrm{high}}\gt\varepsilon_{\mathrm{low}}.
$$

论文默认 $\varepsilon_{\mathrm{low}}=0.2$、$\varepsilon_{\mathrm{high}}=0.28$。负侧还是紧的，坏 token 被大幅压低时步子不会失控；正侧松一点，稀有的正确推理还能继续涨。它和 CISPO 不一样：CISPO clip 的是 detach 之后的 IS 权重，越界 token 仍有 $\nabla\log\pi$，见 `pt-cispo`；DAPO 还是 PPO 风格的 surrogate clip，只是区间不对称了。

$\varepsilon_{\mathrm{high}}$ 放得太大就 $\approx$ 没 clip，格式会被高 $A$ 的样本冲掉。所以要盯 clip fraction、熵和 holdout 上的格式，光看训练 奖励分数（reward） 不够。

## Dynamic Sampling：丢掉零方差组

约束写成

$$
0 \lt \bigl|\{o_i:\ \mathrm{is\_equivalent}(a,o_i)\}\bigr| \lt G.
$$

一组全对或全错时，组内 $\hat A=0$，这一步白算，见 `byte-grpo-all-same-zero-adv`。过滤是针对当前策略做的，同一道题以后可能又变得可分，所以题目不会被永久删掉。实现上有效组不够就继续采，凑满 mini-batch 再更新。

副作用是一种隐性的 curriculum：长期只留下当前能解的题，超难的桶再也进不了梯度。所以要配覆盖配额，定期把全错桶重新探一遍。过滤后有效 batch 太小、更新频率下降时，先加大 $G$ 或者降低难度，别去加学习率。

## Token-level PG：每个 token 等权

vanilla GRPO 常先对每条回复做 $(1/|o_i|)\sum_t$，再对组求平均，每条序列的总权重相同，长回复里单个 token 就被摊薄了。一条又长又差的胡话受到的惩罚不够，长度和熵会「不健康地」上涨。DAPO 改成全局 token 平均：

$$
\mathcal{J}_{\mathrm{DAPO}}=\mathbb{E}\Bigg[\frac{1}{\sum_i|o_i|}\sum_{i,t}\min\big(\rho_{i,t}\hat A_{i,t},\;\mathrm{clip}(\rho_{i,t})\hat A_{i,t}\big)\Bigg].
$$

这样长序列对梯度的贡献随 token 数增长。它和 Dr.GRPO 讨论的 length weighting 是同一条轴，见 `pt-drgrpo`：没有脱离目标的「绝对正确」，要看你想让序列等权还是 token 等权。slime / veRL 里的 `loss_agg_mode`、`--calculate-per-token-loss` 就是这个开关。

## Overlong shaping：别让截断制造假标签

如果规则是「超过 `max_tokens` 就把 $r$ 从 1 打成 0 或 $-1$」，一条推理正确、只是写长了的轨迹也会挨罚，模型分不清「答错了」和「写超了」。DAPO 先试过对截断样本 mask 掉 loss（Overlong Filtering），后来改用软缓存：在期望长度 $L_{\mathrm{max}}$（论文是 16k）外面再留 $L_{\mathrm{cache}}$（4k），在 $[L_{\mathrm{max}},L_{\mathrm{max}}+L_{\mathrm{cache}}]$ 上线性加惩罚，超过缓存再给满罚。奖励是连续的，长度 hack 和「好推理被截断」就能分开看。这和 `data-length-hacking`、`pt-reasoning-token-cost-frontier` 是同一个纪律：长度要进评测，只看原始奖励分数不够。

## 追问

**DAPO 和「去掉 KL」是一回事吗？**
两回事。高德、小红书去 KL 是另一种取舍，见 `gaode-dapo-no-kl`。DAPO 论文可以弱化显式的 $\beta\mathrm{KL}$，靠 clip-higher 和动态采样管步长，但这四个修改本身并没有规定「无 KL」。

**Clip-Higher 和熵崩有什么关系？**
稀有好 token 的 $\rho$ 很快顶到 $1+\varepsilon$，正向梯度没了，策略就锁进已有的高概率模式。放宽上界是在延长探索窗口，保证不了熵不掉。熵塌了先动哪几个旋钮，见 `data-entropy-fix-order`。

**动态采样会不会变慢？**
会多采一些全错组，但同步 强化学习（RL） 的实际耗时常常由最长的样本决定；论文观察到收敛步数下降了，总时间不一定更差。要监控有效组比例，光报采样条数不够。

**token-level 一定更好吗？**
不一定。想让每道题等权就用序列平均；想惩罚长胡话、让长推理里的关键 token 拿到足够权重，就用 token 平均。先说目标，再选归约方式。
