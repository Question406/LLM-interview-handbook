---
id: pt-self-opd-family
section: posttrain
order: 239
level: S
title: Self-OPD 家族怎么分？u-OPSD、π-Distill、LOPD 各补哪块？
quick: "Self-OPD 是一个家族的叫法，共同点是教师和学生同一套权重、教师多拿一份特权信息，区别在特权从哪来：OPSD 用 GT；u-OPSD 用多数票、只蒸反对票；SR-OPSD 往 $\\pi_{\\mathrm{ref}}$ 插值；π-Distill 联合训练 PI 教师；LOPD 把特权换成可学习的 latent。答题先说清特权来源，再谈散度。"
tags:
  - OPD
  - OPSD
  - Self-Distillation
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Self-Distilled Reasoner (OPSD)
    url: https://arxiv.org/abs/2601.18734
    type: primary
  - title: u-OPSD — On-Policy Self-Distillation without Any Supervision
    url: https://arxiv.org/abs/2608.06296
    type: primary
  - title: SR-OPSD — Self-Referenced On-Policy Self-Distillation
    url: https://arxiv.org/abs/2608.09745
    type: primary
  - title: Privileged Information Distillation（π-Distill）
    url: https://arxiv.org/abs/2602.04942
    type: primary
  - title: Latent On-Policy Self-Distillation
    url: https://arxiv.org/abs/2608.13040
    type: primary
---

Self-OPD 指的是一族方法，没有哪篇论文就叫这个名字：教师和学生用同一套权重，教师多看一份特权信息，在学生自己生成的前缀上给逐 token 分布。几篇的区别主要在特权从哪来。被问到时我会先确认三件事：教师权重是不是自己、特权上下文从哪来、下一 token 的分布用哪种散度。机制本身在 `pt-opsd` 讲，这张卡只做家族对照，免得把 2026 年这几篇名字相近的工作答成一个公式。缩写对不上，就按论文设定讲，别硬猜。

比如同一道数学题，OPSD 的教师能看到标准解答；u-OPSD 没有标签，教师看到的是多数票里最长的那条同意轨迹；LOPD 的教师看到的是检索来的经验压成的 latent。下面这张表把六个名字放在一起。

| 名字 | 教师参数 | 特权 / 教师上下文 | 蒸在哪条轨迹上 | 典型失败 |
| --- | --- | --- | --- | --- |
| OPD | 外部（常更大） | 通常就是 $x$ | 学生生成的轨迹 | 继承外部偏见、查询成本 |
| OPSD | 同权重，常冻初始 | GT $y^\star$ | 学生 $\hat{y}$，对错都蒸 | 题太难则教师也不会；$y^\star$ 泄漏 |
| u-OPSD | 同权重，stop-grad | 多数票里最长的同意轨迹 $y^+$ | 只蒸 **不同意** 的 $y^-$ | 错共识被放大；全同意就没梯度 |
| SR-OPSD | EMA / 滞后自教师 | 反馈或特权 $h^{\mathrm{sf}}$ | 学生前缀 | 自教师和状态一起动，锁峰、熵塌 |
| π-Distill | 同权重，师生 **联合** 训 | 训练时 PI（常是动作轨迹） | 教师轨迹为主，见 `pt-pi-distill` | PI 太强导致师生分布鸿沟 |
| LOPD | 教师骨干冻住，学 composer | 检索经验压成 latent | 学生前缀 + reverse KL | composer 把教师拉向学生 |

## 几个容易讲混的点

u-OPSD 的流程是先采 $G$ 条、抽出答案做多数票 $\tilde{a}$，分成同意集 $\mathcal{Y}^{+}$ 和反对集 $\mathcal{Y}^{-}$。投票率 $c(x)\lt\tau$（论文 $\tau=1/2$）或者没有反对票，这道题这一步就跳过；截断的、解析不出答案的轨迹两边都不进。目标写出来是这样（$\bar{\pi}$ 无梯度）：

$$
\mathcal{L}=\mathbb{E}_{x}\mathbb{E}_{\{y^{(g)}\}}\Big[\mathbf{1}[\mathcal{Y}^{-}_{x}\neq\emptyset]\,\frac{1}{|\mathcal{Y}^{-}_{x}|}\sum_{y^{-}}\frac{1}{|y^{-}|}\sum_n D_{\beta}\big(\bar{\pi}(\cdot\mid x,y^{+},y^{-}_{\lt n})\,\big\|\,\pi_{\theta}(\cdot\mid x,y^{-}_{\lt n})\big)\Big].
$$

它和 GRPO 都用了共识，但 GRPO 把共识变成标量奖励，u-OPSD 只用共识构造特权上下文，监督仍然是 token 级分布。论文的观察是，用伪标签构造教师的逐 token 分布，比把同一个共识转成强化学习的标量奖励更有效。

SR-OPSD 针对的是另一件事：自教师 $\pi_{\bar{\theta}}$、学生、on-policy 前缀三个一起动，固定 KL 会不稳定，或者过度集中。它把目标设成

$$
\pi_{\alpha}^{\star}(a)\propto \operatorname{sg}[\pi_{\bar{\theta}}(a\mid h^{\mathrm{sf}})]^{\alpha}\,\pi_{\mathrm{ref}}(a\mid h^{\mathrm{ref}})^{1-\alpha},
$$

$\alpha=1$ 是纯自教师，$\alpha=0$ 是纯参考（常取训练前的 $\pi_{\theta_0}$）。再用 Rényi 阶 $\rho$ 控制怎么投影到 $\pi_{\alpha}^{\star}$，$\rho\to 1$ 时回到 KL。面试讲到这里就够了：$\alpha$ 决定靶子在哪，$\rho$ 决定投影的几何，这是两个旋钮，别说成同一个 $\beta$。

π-Distill 面向多轮 agent。前沿模型往往只给动作、不给分步推理（CoT），于是同一套参数里，PI 条件教师 $\pi^T(\mathbf{o}\mid s,\mathbf{I})$ 和无 PI 学生 $\pi^S(\mathbf{o}\mid s)$ 一起训练，把训练时的特权迁到测试时没有特权的策略上。这篇里也有个「OPSD」，指的是 RL 加上学生与 PI 教师之间的反向 KL，和 Zhao 那篇分布匹配的 OPSD 是两个算法。所以别人一提 OPSD，我会先确认说的是 Self-Distilled Reasoner 还是 π-Distill。

## 怎么选

有标准解答、模型也读得懂解答，用 OPSD，信号稠密，不怕全错组，见 `pt-opsd`。没标签、答案能解析、还能形成稳定多数，用 u-OPSD，细节在 `pt-u-opsd`。自教师跟着训、熵掉得太快或者多样性没了，考虑 SR-OPSD，或者把教师冻住 / 用 EMA，先别去加大学习率。多轮工具场景、只有动作轨迹能当特权，用 π-Distill，见 `pt-pi-distill`。手上有成功经验、又不想把特权格式写死，用 LOPD，见 `pt-lopd`。如果有更强的外部教师、要对齐格式或安全，就走外部 OPD，见 `pt-on-policy-distillation`；Self-OPD 省的是大模型查询，并不会自动更强。被问「这不就是 STaR 吗」，区别是硬过滤和软分布，见 `pt-star-vs-opsd`。

u-OPSD 有个系统性风险，就是自信的错共识。多数票一旦错了，$y^+$ 会把错解写进每一条反对轨迹的教师分布。数学题有 checker 时，就用 checker 过滤伪标签，别为了「无监督」把验证器关掉；没有 checker 的开放生成，这条配方不该当默认。

## 和 GRPO、SFT 的边界

监督微调（SFT）在 $y^\star$ 的教师前缀上算交叉熵损失（CE），学生从来没在自己的错前缀上受过训。OPSD 家族都在学生前缀上给分布，这是 on-policy 那一半。GRPO 也在学生轨迹上，但信号稀疏，全对或全错的组梯度为零。Self-OPD 用特权分布把中间步填上，所以蒸馏长度短一点也可能够用：作者的假设是早期 token 是分支点，后面教师几乎能从长前缀预测出来。多轮规划、工具环里这个假设还成不成立，论文自己标成了开放问题。

Self-OPD 也替代不了全部 RL。verifier 可靠、探索还不够的时候，可验证奖励强化学习（RLVR）仍然负责发现新模式；蒸馏负责把已有的特权（GT、共识、PI）变成稠密的纠正。两者冲突时以可执行 oracle 为准，别让教师的文风压过正确答案。

## 追问

**Self-OPD 是一篇论文吗？**
不是，它是 OPSD 家族的统称。写简历时用具体名字：OPSD / u-OPSD / SR-OPSD / π-Distill / LOPD。

**π-Distill 里的 OPSD 和 Zhao 的 OPSD 有什么区别？**
前者是 on-policy RL 加反向 KL；后者是学生采样，再在全词表上算 $D(p_T\|p_S)$。先问清是哪篇 arXiv，展开见 `pt-pi-distill`。

**特权信息能不能学出来，不用手写？**
能。LOPD 用 latent composer 加 privileged-margin 来学，见 `pt-lopd`。
