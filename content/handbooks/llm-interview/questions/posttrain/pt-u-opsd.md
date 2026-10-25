---
id: pt-u-opsd
section: posttrain
order: 240
level: S
title: 没有标准答案时 u-OPSD 怎么自己当老师？和 GRPO 多数票差在哪？
quick: "采 $G$ 条，用多数票选出伪解答 $y^+$，只在投反对票的那些前缀上把 $p(\\cdot\\mid x,y^+)$ 蒸进 $p(\\cdot\\mid x)$。共识用来构造特权上下文，没变成标量 $A$；票不够稳或没有反对票，这一步就没有梯度。风险是错共识会被写成稠密教师。"
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

u-OPSD 用模型自己的多数票当特权信息：同一道题采 $G$ 条，选出多数答案，把最长的同意轨迹 $y^+$ 塞进教师上下文，再在每条投反对票的轨迹前缀上做 token 级蒸馏。它和 GRPO 多数票的区别在于共识怎么用：GRPO 把共识变成标量优势 $A$，u-OPSD 用共识构造教师上下文，监督仍是 token 级的 $D(p_T\|p_S)$。所以它既算不上「无监督 GRPO」，也不是「self-consistency 当 reward」。OPSD 本身还要 GT $y^\star$（见 `pt-opsd`），u-OPSD 把这层外部监督也拆掉了。

举个例子。一道题采一组，大多数轨迹答 A，少数答 B。u-OPSD 取答 A 的轨迹里最长的一条当 $y^+$，教师看着它去读那几条答 B 的轨迹，在它们走偏的位置给出纠正分布。同样这一组，GRPO 会给答 A 的正优势、答 B 的负优势，整条轨迹共享一个数。

## 三步：采、投票、蒸反对票

对无标签题 $x$ 采 $G$ 条 $y^{(g)}\sim\bar{\pi}(\cdot\mid x)$，解析出终局答案 $a^{(g)}$，截断或解析失败的记空，两边都不进。多数票得到 $\tilde{a}$，分成同意集 $\mathcal{Y}^{+}$ 和反对集 $\mathcal{Y}^{-}$。置信度是

$$
c(x)=\frac{1}{G}\sum_g\mathbf{1}[a^{(g)}=\tilde{a}].
$$

$c(x)\lt\tau$（论文 $\tau=1/2$）或 $\mathcal{Y}^{-}=\emptyset$，这一步跳过。过线以后取最长的同意轨迹当 $y^+$，在每条 $y^{-}$ 的前缀上匹配

$$
D_{\beta}\big(\bar{\pi}(\cdot\mid x,y^{+},y^{-}_{\lt n})\,\big\|\,\pi_{\theta}(\cdot\mid x,y^{-}_{\lt n})\big).
$$

其中 $\bar{\pi}$ 做 stop-gradient。课程是自发形成的：太难的题形不成票，太简单的全同意，两头都没梯度，剩下的是「能形成共识、但还会走偏」的边界题。这和 DAPO 丢掉零方差组是一类做法，见 `pt-dapo`。

要分清的是，这里采 $G$ 条是为了投票，跟组相对优势无关。没有反对票时，u-OPSD 没有可蒸的对象；GRPO 没有反对票时 $A=0$。两者看着都是「全同意就空转」，机制却不一样。

## 共识当上下文，不当标量

把 self-consistency / majority vote 当强化学习（RL）奖励，整段共享一个 $0/1$，credit 仍然稀疏，错的中间步和对的结尾绑在一起。u-OPSD 把最长同意轨迹放进教师上下文，反对前缀上的每个 token 都拿到一个分布。论文的观察是，同一套共识，当稠密教师信号往往比当标量 reward 更有效。self-rewarding 那条路见 `pt-self-rewarding-idpo`。

它和对 $y^+$ 做监督微调（SFT）也不一样。SFT 在同意轨迹的教师前缀上算交叉熵损失（CE）；u-OPSD 在不同意的学生前缀上做纠正。它学的是「已经会的解法，怎么把走偏的自己拉回来」，用不着再克隆一条本来就会写的长解。

## 会在哪里出问题

最大的风险是错共识。多数票一旦错了，$y^+$ 会把错解写进每条反对轨迹的教师分布，固化错误的效率比稀疏负奖励还高。数学题有 checker 就用 checker 过滤伪标签，别为了「无监督」把验证器（verifier）关掉；开放生成没有可解析的答案空间，这条配方不该当默认。

还有几处细节。投票率 $c(x)$ 的分母是全部 $G$，截断会拉低置信度，这样能避免「有效的几条里全同意」被当成高置信。解析器要稳定，`\boxed{}` 的规范化一变，票就碎了，训练和评测必须用同一套 `Ans(\cdot)`。另外用最长同意轨迹当 $y^+$，可能偏向啰嗦但碰巧答案相同的样本，要和 `data-length-hacking` 一起看 held-out。

验收时看无特权、单次采样的 pass@1，以及多数票相对 gold 的一致率。票很稳、gold 却不对，就是在蒸一个错老师。

## 追问

**和 OPSD 怎么选？**
有可靠的 $y^\star$ 就用 OPSD；没标签、答案能解析、还能稳定过半，用 u-OPSD。两者都可以叠风格 token clip，见 `pt-opsd`。

**能不能既用 verifier 又投票？**
能。只有 checker 过了的同意轨迹才当 $y^+$，反对票照样蒸。这时已经算不上「没有任何监督」，只是少用了 gold 思维链（CoT，即分步推理过程）。

**所有轨迹都同意，还要蒸吗？**
按定义跳过。硬蒸等于把已经对齐的分布再推一遍，白白浪费 decode 成本。

**和 SR-OPSD 是什么关系？**
u-OPSD 解决特权从哪来，SR-OPSD 解决自教师跟着训会漂。可以一起用：伪标签当 $h^{\mathrm{sf}}$，再和 $\pi_{\mathrm{ref}}$ 插值，见 `pt-self-opd-family`。
