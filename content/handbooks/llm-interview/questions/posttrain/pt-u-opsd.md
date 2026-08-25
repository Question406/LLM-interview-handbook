---
id: pt-u-opsd
section: posttrain
order: 240
level: S
title: 没有标准答案时 u-OPSD 怎么自己当老师？和 GRPO 多数票差在哪？
quick: >-
  采 $G$ 条、多数票当伪解答 $y^+$，只在投反对票的前缀上把 $p(\cdot\mid x,y^+)$ 蒸进 $p(\cdot\mid x)$。共识构造的是特权上下文，不是标量
  $A$。票不够稳或没有反对票，这步没有梯度。错共识会把错解写成稠密教师。
tags:
  - OPSD
  - Self-Distillation
  - Self-Consistency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: On-Policy Self-Distillation without Any Supervision
    url: https://arxiv.org/abs/2608.06296
    type: primary
  - title: Self-Distilled Reasoner (OPSD)
    url: https://arxiv.org/abs/2601.18734
    type: primary
---

OPSD 仍要 GT $y^\star$，见 `pt-opsd`。u-OPSD 把「外部监督」再拆掉：特权上下文来自 **模型自己的多数票**。不要答成「无监督 GRPO」或「self-consistency 当 reward」。同一套 $G$ 条 rollout，GRPO 用对错方差估 $A$；u-OPSD 用同意轨迹当教师、反对轨迹当学生前缀，监督仍是 token 级 $D(p_T\|p_S)$。

## 三步：采、票、蒸反对票

对无标签题 $x$ 采 $G$ 条 $y^{(g)}\sim\bar{\pi}(\cdot\mid x)$，解析终局答案 $a^{(g)}$（截断解析失败记空，两边都不进）。多数票 $\tilde{a}$，同意集 $\mathcal{Y}^{+}$、反对集 $\mathcal{Y}^{-}$。置信

$$
c(x)=\frac{1}{G}\sum_g\mathbf{1}[a^{(g)}=\tilde{a}].
$$

$c(x)\lt\tau$（论文 $\tau=1/2$）或 $\mathcal{Y}^{-}=\emptyset$，本步跳过。过线后取最长同意轨迹当 $y^+$，在每条 $y^{-}$ 的前缀上匹配

$$
D_{\beta}\big(\bar{\pi}(\cdot\mid x,y^{+},y^{-}_{\lt n})\,\big\|\,\pi_{\theta}(\cdot\mid x,y^{-}_{\lt n})\big).
$$

$\bar{\pi}$ stop-gradient。课程是自发的：太难形不成票、太简单全同意，两端没梯度，剩下的是「会形成共识、但仍会走偏」的边界题。这和 DAPO 丢掉零方差组同类，见 `pt-dapo`。

$G$ 条是为了 **投票**，不是为了组相对优势。没有反对票就没有蒸的对象；GRPO 没有反对票则 $A=0$。看起来都像「全同意就空转」，机制不要讲成一个。

## 共识当上下文，不当标量

Self-consistency / majority vote 当 RL 奖励：整段共享一个 $0/1$，credit 仍稀疏，错的中间步和对的结尾绑在一起。u-OPSD 把最长同意轨迹塞进教师上下文，反对前缀上的每一 token 都有分布。论文观察是：同一套共识，当 dense teacher 往往比当标量 reward 更有效。self-rewarding 那条见 `pt-self-rewarding-idpo`。

它也 **不是** 对 $y^+$ 做 SFT。SFT 在同意轨迹的教师前缀上 CE；u-OPSD 在 **不同意** 的学生前缀上纠正。学的是「我已经会的解，如何把走偏的自己拉回来」，不是再克隆一条已经会写的长解。

## 失败面

- **错共识。** 多数票错了，$y^+$ 会把错解写进每条反对轨迹的教师分布，比稀疏负奖励更高效地固化错误。数学有 checker 就用 checker 滤伪标签，不要为了「无监督」关 verifier。开放生成没有可解析答案空间，这条不该当默认。
- **投票率口径。** $c(x)$ 分母是全部 $G$，截断会拉低置信，避免「有效条里全同意」被当成高置信。
- **解析器。** `\boxed{}` 规范化一变，票就碎。训练和评测必须同一套 `Ans(\cdot)`。
- **长度偏置。** 用最长同意轨迹当 $y^+$，可能偏向啰嗦但碰巧同答案的样本。要和 `data-length-hacking` 一起看 held-out。

验收仍看 **无特权、单次采样** 的 pass@1，以及多数票相对 gold 的一致率。票很稳但 gold 不对，就是在蒸错老师。

## 追问

- **和 OPSD 怎么切？** 有可靠 $y^\star$ 用 OPSD。没标签、答案可解析、还能稳定过半，用 u-OPSD。两者都可以叠风格 token clip，见 `pt-opsd`。
- **能不能既 verifier 又投票？** 能。checker 过的同意轨迹才当 $y^+$，反对票仍蒸。那已经不是「没有任何监督」，只是少用 gold CoT。
- **全模型都同意还要蒸吗？** 按定义跳过。硬蒸等于把已经对齐的分布再推一遍，浪费 decode。
- **和 SR-OPSD？** u-OPSD 解决「特权从哪来」；SR-OPSD 解决「自教师跟着训会漂」。可以同时用：伪标签当 $h^{\mathrm{sf}}$，再和 $\pi_{\mathrm{ref}}$ 插值，见 `pt-self-opd-family`。
