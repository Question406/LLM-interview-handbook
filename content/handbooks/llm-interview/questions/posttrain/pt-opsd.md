---
id: pt-opsd
section: posttrain
order: 238
level: S
title: OPSD 和 OPD 差在哪？同一套权重怎么当自己的老师？
quick: >-
  OPD 是学生采样、外部教师给 token 级分布。OPSD（Self-Distilled Reasoner）教师和学生是同一套参数：学生只看题
  $p_S(\cdot\mid x)$，教师多看特权正解 $p_T(\cdot\mid x,y^\star)$；在学生自己的前缀上最小化
  $D(p_T\|p_S)$，梯度只走学生。不要说成「没有老师、自己 SFT 自己」。
tags:
  - OPD
  - OPSD
  - Distillation
  - Self-Distillation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-20
sources:
  - title: Self-Distilled Reasoner — On-Policy Self-Distillation
    url: https://arxiv.org/abs/2601.18734
    type: primary
  - title: OPSD 作者博客
    url: https://siyan-zhao.github.io/blog/2026/opsd/
    type: secondary
  - title: Thinking Machines — On-Policy Distillation
    url: https://thinkingmachines.ai/blog/on-policy-distillation/
    type: secondary
---

面试里 **Self-OPD / OPSD** 指的是「同一套权重、特权上下文当老师」，不是第三种算法名。先和外部教师的 OPD 切开，见 `pt-on-policy-distillation`。OPSD 不是「没有老师、自己对自己做 SFT」：老师仍在，只是老师是 **看过 $y^\star$ 的自己**。$y^\star$ 只在训练时进上下文，推理仍只看 $x$。

## 三个角色，一套参数

给定题 $x$ 和训练时可见的正解 / 标准 CoT $y^\star$，同一网络切成两个条件分布：

$$
p_S(\cdot\mid x)=\pi_{\theta}(\cdot\mid x),\qquad p_T(\cdot\mid x,y^\star)=\bar{\pi}(\cdot\mid x,y^\star).
$$

$\bar{\pi}$ 通常 stop-gradient，论文里还常把教师冻在初始策略，避免师生一起漂。学生按推理条件采样

$$
\hat{y}\sim p_S(\cdot\mid x),
$$

然后在学生前缀 $\hat{y}_{\lt n}$ 上同时算下一 token 分布。教师 **不生成**：只对同一前缀做一次前向，把「已经知道答案的自己」的分布写给学生。轨迹平均散度

$$
D(p_T\|p_S)(\hat{y}\mid x)=\frac{1}{|\hat{y}|}\sum_n D\Big(p_T(\cdot\mid x,y^\star,\hat{y}_{\lt n})\,\Big\|\,p_S(\cdot\mid x,\hat{y}_{\lt n})\Big).
$$

$D$ 可以是 KL 或 $\mathrm{JSD}_\beta$。论文默认 $\beta=0$，即在该前缀上的 **全词表正向** $D_{\mathrm{KL}}(p_T\|p_S)$。梯度只回学生 logits。这和 STaR 不同：STaR 要教师显式写出 rationalization，再对 **答对** 的硬标签做 SFT；OPSD 即使学生终局错了，前缀上仍有稠密分布信号。对照卡 `pt-star-vs-opsd`。无 GT 时走 `pt-u-opsd`；多轮只有动作示范走 `pt-pi-distill`；特权本身要可学走 `pt-lopd`。

白板口诀：**谁采样（学生）决定状态 on-policy；谁进上下文（$y^\star$）决定教师比学生强；梯度只走没特权的那一侧。**

## 和 OPD、GRPO 的差

| | 教师是谁 | 状态从哪来 | 每个 token 的信号 | 没有有效组时 |
| --- | --- | --- | --- | --- |
| 离线 KD / SFT | 外部或演示 | 教师轨迹 | 稠密，off-policy | 仍有 CE |
| OPD | 通常更大的外部模型 | 学生 rollout | 稠密分布 | 仍有 KL |
| OPSD | 同权重 + $y^\star$ | 学生 rollout | 稠密分布 | 仍有 KL |
| GRPO | 无教师 | 学生 rollout | 序列标量 $A$ | 全对/全错梯度没了 |

OPD 买的是「更强外部教师」；OPSD 买的是「评价 / 合理化比生成容易」——给答案后，模型往往能指出学生前缀哪里不像正解。上界仍受 **无特权时的容量** 限制：题远超理解阈值，教师看了 $y^\star$ 也给不出有意义的下一 token，蒸馏就是噪声。论文用 Qwen3 量级，不是任意小模型都能 self-distill。

和 GRPO 比，OPSD 不必为组方差等 $G$ 条、也不必等终局对错。作者设置里学生蒸馏长度可短到 1k、每题 1 条 rollout，而 GRPO 用更长生成和 $G=8$。代价是必须有 $y^\star$（或后面 `pt-self-opd-family` 里的伪标签），且 reverse/forward 选错会和拼多多 OPD 题打架，见下一节。

slime 的 `--use-opd` 是 **外部教师 KL 叠加在 advantage 上**，不是 OPSD，更不是一种 estimator，见 `slime-advantage-estimator`。

## 实现陷阱

- **KL 方向。** Thinking Machines OPD 常把采样写在学生上，目标近 $D_{\mathrm{KL}}(\pi_S\|\pi_T)$（反向 / mode-seeking）。Zhao 的 OPSD 在学生前缀上算 **全词表** $D_{\mathrm{KL}}(p_T\|p_S)$，期望在教师下一 token 上，是正向 covering，但 **前缀仍是学生的**。口诀拆两层：状态 on-policy $\neq$ 下一 token KL 一定是反向。拼多多原问若说的是外部 OPD，先答反向；若说的是 OPSD 论文公式，先写 $D(p_T\|p_S)$。见 `pt-kd-forward-vs-reverse`、`pdd-forward-reverse-kl`。
- **风格 token 霸榜。** `wait` / `think` / `therefore` 上的逐点 KL 往往远大于数学 token。不做 per-token pointwise clip，loss 会被连接词劫持，几百 step 就塌。仓库默认 clip 不是可选美化。
- **全词表还是采样 token。** 默认全词表 $D(p_T\|p_S)$；`--use_tinker_loss` 只在采到的 token 上用 $r_n=\log p_T-\log p_S$，更省显存、更像 PG，也更依赖 clip。面试先报用的是哪一种，再谈 KL 方向。
- **Thinking 开关。** 作者早期实验里 TM-off 学生 + TM-on 教师，数学 token 上的 KL 更大、下游更好。师生生成风格要显式配对，不要默认同一模板。
- **师生共漂。** 教师若跟当前 $\theta$ 一起更新，特权分布会追着学生走，监督变软。冻初始策略或 EMA，等于隐式 $\pi_{\mathrm{ref}}$。SR-OPSD 把这件事做成显式插值，见 `pt-self-opd-family`。
- **泄漏。** $y^\star$ 绝不能出现在学生上下文或评测 prompt。模板字段名、分隔符泄漏等于开卷考试。

验收仍看 **去掉 $y^\star$ 之后** 的 pass@1 / pass@k，不要只看蒸馏 loss。loss 降、无特权准确率不动，说明在拟合「看答案时的口吻」，没有把能力迁到 $p_S$。

## 追问

- **和外部 OPD 怎么选？** 有更强教师、格式/工具要对齐，用 OPD。只有标准答案、模型已经能读懂解答，用 OPSD，省一次大模型前向。教师弱过学生时，外部 OPD 会更快灌偏见。
- **终局错了还能学？** 能。监督在前缀的下一 token 分布上，不依赖 $\hat{y}$ 最后是否等价于 $y^\star$。这是相对 GRPO 零方差组的主要优势。
- **一定要 CoT 当 $y^\star$ 吗？** 标准答案、简短解答、工具轨迹都可以当特权；信息量不够则教师分布接近学生，KL 没信号。Agent 侧把动作轨迹当 PI、没有前沿 CoT 时，见 `pt-pi-distill`。
- **和 STaR / RS？** 硬过滤成功样本再 SFT，错的梯度为零。OPSD 对错都蒸，见 `pt-star-vs-opsd`。
- **会不会比 GRPO 更快塌熵？** 全词表正向会 covering，反向则 seeking。无论哪边，风格 token 不 clip 都会假收敛。和 `data-entropy-collapse` 一样，要对着无特权成功率看，不要单看熵。
