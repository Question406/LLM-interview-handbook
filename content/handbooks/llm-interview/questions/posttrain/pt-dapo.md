---
id: pt-dapo
section: posttrain
order: 19
level: S
title: DAPO 四个关键修改分别解决什么？
quick: "Clip-Higher 放宽正向上界，给稀有好 token 涨的空间；动态采样丢掉全对/全错组；token 级平均让每个 token 等权；超长部分用软惩罚，不在截断处直接把奖励打零。"
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

常见误区是：答成「又一个优势公式」或「把 KL 删掉的 GRPO」。它仍用组相对优势，改的是 clip、有效样本、损失（loss） 归约、超长惩罚这四件工程失败。小红书真题卡 `xiaohongshu-dapo-vs-grpo` 问的是同一件事；本题把四个旋钮拆开，能白板写公式。

## Clip-Higher：正向上界单独放宽

PPO / GRPO 对称 clip 是 $\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)$。$A\gt 0$ 且 $\rho\gt 1+\varepsilon$ 时该项梯度为 0：刚冒出来的低概率的好 token 立即失去该项梯度，熵更容易塌，见 `data-entropy-collapse`。DAPO 把上下界拆开：

$$
\mathrm{clip}\big(\rho_t,\;1-\varepsilon_{\mathrm{low}},\;1+\varepsilon_{\mathrm{high}}\big),\qquad \varepsilon_{\mathrm{high}}\gt\varepsilon_{\mathrm{low}}.
$$

论文默认 $\varepsilon_{\mathrm{low}}=0.2$、$\varepsilon_{\mathrm{high}}=0.28$。负侧仍紧，防止坏 token 被大幅压低时步子失控；正侧松一点，让稀有正确推理还能涨。这和 CISPO 不同：CISPO clip 的是 detach 后的 IS 权重，越界 token 仍有 $\nabla\log\pi$，见 `pt-cispo`。DAPO 仍是 PPO 风格的 surrogate clip，只是区间不对称。

$\varepsilon_{\mathrm{high}}$ 过大 $\approx$ 没 clip，格式会被高 $A$ 样本冲掉。盯 clip fraction、熵和 holdout 格式，不要只看训练 奖励分数（reward）。

## Dynamic Sampling：丢掉零方差组

约束写成

$$
0 \lt \bigl|\{o_i:\ \mathrm{is\_equivalent}(a,o_i)\}\bigr| \lt G.
$$

全对或全错时组内 $\hat A=0$，这步白算，见 `byte-grpo-all-same-zero-adv`。过滤发生在当前策略上：同一道题以后可能又变得可分，所以不是永久删题。实现上不够有效组就继续采，凑满 mini-batch 再更新。

副作用是隐性 curriculum：长期只留当前能解的题，超难桶再也进不了梯度。要配覆盖配额，周期性把全错桶再探回来。过滤后有效 batch 过小，更新频率会下降，先加 $G$ 或降温难度，而不是加学习率。

## Token-level PG：每 token 等权

Vanilla GRPO 常先对每条回复做 $(1/|o_i|)\sum_t$，再对组平均：每条序列总权重相同，长回复里单个 token 被摊薄。长而差的胡话惩罚不够，长度和熵会「不健康地」涨。DAPO 改成全局 token 平均：

$$
\mathcal{J}_{\mathrm{DAPO}}=\mathbb{E}\Bigg[\frac{1}{\sum_i|o_i|}\sum_{i,t}\min\big(\rho_{i,t}\hat A_{i,t},\;\mathrm{clip}(\rho_{i,t})\hat A_{i,t}\big)\Bigg].
$$

长序列对梯度的贡献按 token 数涨。这和 Dr.GRPO 讨论的 length weighting 是同一轴，见 `pt-drgrpo`：没有脱离目标的「绝对正确」，只是你要序列等权还是 token 等权。slime / veRL 的 `loss_agg_mode`、`--calculate-per-token-loss` 就是这个开关。

## Overlong shaping：别让截断制造假标签

硬规则「超 `max_tokens` 就把 $r$ 从 1 打成 0 / $-1$」会惩罚一条推理正确、只是写长了的轨迹，模型分不清「答错」和「写超了」。DAPO 先试过对截断样本 mask 掉 loss（Overlong Filtering），再用软缓存：期望长度 $L_{\mathrm{max}}$（论文 16k）外再留 $L_{\mathrm{cache}}$（4k），在 $[L_{\mathrm{max}},L_{\mathrm{max}}+L_{\mathrm{cache}}]$ 上线性加惩罚，超过缓存再给满罚。奖励连续，长度 hack 和「好推理被截断」可以分开看。

这和 `data-length-hacking`、`pt-reasoning-token-cost-frontier` 同一纪律：长度必须进评测，不能只看 原始奖励分数。

## 追问

- **和「去掉 KL」是一回事吗？** 不是。高德 / 小红书去 KL 是另一条取舍，见 `gaode-dapo-no-kl`。DAPO 论文可以弱化显式 $\beta\mathrm{KL}$，靠 clip-higher 和动态采样管步长，但四个修改本身不定义「无 KL」。
- **Clip-Higher 和熵崩？** 稀有好 token 的 $\rho$ 很快顶到 $1+\varepsilon$，正向梯度没了，策略锁进已有高概率模式。放宽上界是延长探索窗口，不是保证熵不掉。塌了先动哪几个旋钮，见 `data-entropy-fix-order`。
- **动态采样会不会变慢？** 会多采一些全错组，但同步 强化学习（RL） 的实际耗时常被最长样本主导；论文观察到收敛步数下降，总时间不一定更差。监控有效组比例，不要只报采样条数。
- **Token-level 一定更好？** 不一定。你要每道题等权就用序列平均；要惩罚长胡话、让长推理中的关键 token 得到足够权重，用 token 平均。先说目标再选归约。
