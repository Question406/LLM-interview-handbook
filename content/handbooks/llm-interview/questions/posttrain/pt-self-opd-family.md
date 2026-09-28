---
id: pt-self-opd-family
section: posttrain
order: 239
level: S
title: Self-OPD 家族怎么分？u-OPSD、π-Distill、LOPD 各补哪块？
quick: >-
  Self-OPD 不是单独论文名，指同权重 + 特权教师。OPSD 用 GT；u-OPSD 用多数票只蒸反对票；SR-OPSD
  插值 $\pi_{\mathrm{ref}}$；π-Distill 联合训 PI 教师；LOPD 把特权改成可学习 latent。先钉特权从哪来，再谈散度。
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

机制卡见 `pt-opsd`。本题只做家族对照，避免把 2026 年几篇同名工作答成一个公式。先钉三件事：教师权重是不是自己、特权上下文从哪来、下一 token 用哪种散度。缩写对不上就按论文设定讲，不要硬猜。

## 一张表分清监督从哪来

| 名字 | 教师参数 | 特权 / 教师上下文 | 蒸在哪条轨迹上 | 典型失败 |
| --- | --- | --- | --- | --- |
| OPD | 外部（常更大） | 通常就是 $x$ | 学生 rollout | 继承外部偏见、查询成本 |
| OPSD | 同权重，常冻初始 | GT $y^\star$ | 学生 $\hat{y}$，对错都蒸 | 题太难则教师也不会；$y^\star$ 泄漏 |
| u-OPSD | 同权重，stop-grad | 多数票里最长的同意轨迹 $y^+$ | 只蒸 **不同意** 的 $y^-$ | 错共识被放大；全同意就没梯度 |
| SR-OPSD | EMA / 滞后自教师 | 反馈或特权 $h^{\mathrm{sf}}$ | 学生前缀 | 自教师和状态一起动，锁峰、熵塌 |
| π-Distill | 同权重，师生 **联合** 训 | 训练时 PI（常是动作轨迹） | 教师轨迹为主，见 `pt-pi-distill` | PI 太强导致师生分布鸿沟 |
| LOPD | 教师骨干冻住，学 composer | 检索经验压成 latent | 学生前缀 + reverse KL | composer 把教师拉向学生 |

u-OPSD 的目标可以写成（$\bar{\pi}$ 无梯度）：

$$
\mathcal{L}=\mathbb{E}_{x}\mathbb{E}_{\{y^{(g)}\}}\Big[\mathbf{1}[\mathcal{Y}^{-}_{x}\neq\emptyset]\,\frac{1}{|\mathcal{Y}^{-}_{x}|}\sum_{y^{-}}\frac{1}{|y^{-}|}\sum_n D_{\beta}\big(\bar{\pi}(\cdot\mid x,y^{+},y^{-}_{\lt n})\,\big\|\,\pi_{\theta}(\cdot\mid x,y^{-}_{\lt n})\big)\Big].
$$

先采 $G$ 条、抽答案做多数票 $\tilde{a}$，同意集 $\mathcal{Y}^{+}$、反对集 $\mathcal{Y}^{-}$。投票率 $c(x)\lt\tau$（论文 $\tau=1/2$）或没有反对票，这题本步跳过。截断、解析不出答案的轨迹两边都不进。这和 GRPO 用共识当 **标量奖励** 不同：共识只构造特权上下文，监督仍是 token 级分布。论文观察是：当伪标签当 dense teacher，比把同一共识当成 RL 标量更有效。

SR-OPSD 针对的是另一件事：自教师 $\pi_{\bar{\theta}}$、学生、on-policy 前缀 **三个一起动**，固定 KL 会不稳定或过度集中。令目标

$$
\pi_{\alpha}^{\star}(a)\propto \operatorname{sg}[\pi_{\bar{\theta}}(a\mid h^{\mathrm{sf}})]^{\alpha}\,\pi_{\mathrm{ref}}(a\mid h^{\mathrm{ref}})^{1-\alpha},
$$

$\alpha=1$ 纯自教师，$\alpha=0$ 纯参考（常取训练前 $\pi_{\theta_0}$）。再用 Rényi 阶 $\rho$ 控制怎么投影到 $\pi_{\alpha}^{\star}$，$\rho\to 1$ 回到 KL。面试只需要： **$\alpha$ 决定靶子在哪，$\rho$ 决定投影几何**；不要把两个旋钮说成同一个 $\beta$。

π-Distill 面向多轮 agent：前沿模型往往只给动作、不给 CoT。同一套参数里，PI 条件教师 $\pi^T(\mathbf{o}\mid s,\mathbf{I})$ 和无 PI 学生 $\pi^S(\mathbf{o}\mid s)$ **一起训练**，把训练时特权迁到测试时无特权策略。同一篇里的「OPSD」是 **RL + 学生与 PI 教师之间的反向 KL**，和 Zhao 的分布匹配 OPSD **不是同一算法**。被问到 OPSD 先确认对方指的是 Self-Distilled Reasoner 还是 π-Distill。

## 怎么选，别背全称

- 有标准解答、模型已经能读懂解答：OPSD。稠密、不怕全错组，见 `pt-opsd`。
- 没标签、答案可解析、还能形成稳定多数：u-OPSD，细节 `pt-u-opsd`。
- 自教师跟着训、熵掉得太快或多样性没了：SR-OPSD 或把教师冻住 / EMA，不要先加大学习率。
- 多轮工具、只有动作轨迹当特权：π-Distill，细节 `pt-pi-distill`。
- 成功经验在、但不想把特权格式写死：LOPD，细节 `pt-lopd`。
- 有更强外部教师、要对齐格式或安全：外部 OPD，见 `pt-on-policy-distillation`。Self-OPD 省的是大模型查询，不自动更强。
- 被问「不就是 STaR 吗」：硬过滤 vs 软分布，见 `pt-star-vs-opsd`。

u-OPSD 的系统性风险是 **自信的错共识**。多数票错了，$y^+$ 会把错解写进每一条反对轨迹的教师分布。数学有 checker 时，应用 checker 滤伪标签，不要为了「无监督」而关掉 verifier。没有 checker 的开放生成，这条配方不该当默认。

## 和 GRPO / SFT 的边界

SFT 在 $y^\star$ 的教师前缀上做 CE：学生从未在自己的错前缀上受训。OPSD 家族都在 **学生前缀** 上给分布，这是 on-policy 这一半。GRPO 在学生轨迹上但信号稀疏，全对/全错组为零。Self-OPD 用特权分布填中间步，所以短蒸馏长度也可能够，作者假设早期 token 是分支点，后面教师几乎能从长前缀预测。多轮规划、工具环是否仍成立，论文自己标成开放问题。

不要把 Self-OPD 答成「替代全部 RL」。Verifier 可靠且探索还不够时，RLVR 仍负责发现新模式；蒸馏负责把已有特权（GT、共识、PI）变成稠密纠正。冲突时以可执行 oracle 为准，不要让教师文风压过正确答案。

## 追问

- **Self-OPD 是一篇论文吗？** 不是。口令等于 OPSD 家族。写简历用具体名字：OPSD / u-OPSD / SR-OPSD / π-Distill / LOPD。
- **π-Distill 的 OPSD 和 Zhao 的 OPSD？** 前者是 on-policy RL + 反向 KL；后者是学生采样 + 全词表 $D(p_T\|p_S)$。先问 arXiv，展开见 `pt-pi-distill`。
- **特权能不能学而不是写？** 能，LOPD 用 latent composer + privileged-margin，见 `pt-lopd`。
