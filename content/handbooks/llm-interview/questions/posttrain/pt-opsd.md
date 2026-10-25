---
id: pt-opsd
section: posttrain
order: 238
level: S
title: OPSD 和 OPD 差在哪？同一套权重怎么当自己的老师？
quick: "OPD 的教师是外部模型，OPSD 的教师是同一套权重，只是训练时多看了正解 $y^\\star$。学生自己采样前缀，在这些前缀上最小化 $D(p_T\\|p_S)$，梯度只回学生；推理时只看 $x$，所以验收要看去掉 $y^\\star$ 之后的准确率。"
tags:
  - OPD
  - OPSD
  - Distillation
  - Self-Distillation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
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
OPD 和 OPSD 的差别在教师是谁：OPD 用一个外部的、通常更大的模型当老师；OPSD 的老师就是同一套权重，只是训练时上下文里多放了正解 $y^\star$。学生照样自己采样，教师在学生的前缀上给出「已经知道答案的自己」会怎么写下一个 token。$y^\star$ 只在训练时进上下文，推理时模型仍然只看 $x$。

面试里说的 Self-OPD / OPSD，指的就是「同一套权重、特权上下文当老师」这个做法，算不上第三种算法。外部教师的 OPD 见 `pt-on-policy-distillation`。OPSD 也不是「没有老师、自己对自己做 SFT」，老师还在，只是老师是看过 $y^\star$ 的自己。

打个比方，学生做一道几何题，第三步引错了辅助线。同一个模型看着标准解答再读这个前缀，很容易看出「这里应该连另一条线」，它在这一步给出的下一 token 分布就是监督。即使学生最后答错了，这一路前缀上的信号照样能用。

## 三个角色，一套参数

给定题 $x$ 和训练时可见的正解或标准思维链（CoT，即分步推理过程）$y^\star$，同一个网络被切成两个条件分布：

$$
p_S(\cdot\mid x)=\pi_{\theta}(\cdot\mid x),\qquad p_T(\cdot\mid x,y^\star)=\bar{\pi}(\cdot\mid x,y^\star).
$$

$\bar{\pi}$ 通常做 stop-gradient，论文里还常把教师冻在初始策略上，免得师生一起漂。学生按推理时的条件采样

$$
\hat{y}\sim p_S(\cdot\mid x),
$$

然后在学生前缀 $\hat{y}_{\lt n}$ 上同时算两边的下一个 token 分布。教师不生成，只对同一个前缀做一次前向，把分布写给学生。轨迹上的平均散度是

$$
D(p_T\|p_S)(\hat{y}\mid x)=\frac{1}{|\hat{y}|}\sum_n D\Big(p_T(\cdot\mid x,y^\star,\hat{y}_{\lt n})\,\Big\|\,p_S(\cdot\mid x,\hat{y}_{\lt n})\Big).
$$

$D$ 可以是 KL，也可以是 $\mathrm{JSD}_\beta$。论文默认 $\beta=0$，也就是在这个前缀上算全词表的正向 $D_{\mathrm{KL}}(p_T\|p_S)$，梯度只回学生的 logits。

三件事要分开记：谁采样（学生）决定了状态是 on-policy 的；谁的上下文里有 $y^\star$ 决定了教师比学生强；梯度只走没有特权的那一侧。

它和 STaR 也不一样。STaR 要教师显式写出 rationalization，再对答对的样本用硬标签做监督微调（SFT）；OPSD 在学生终局错了的时候，前缀上也有稠密的分布信号，对照见 `pt-star-vs-opsd`。没有 GT 走 `pt-u-opsd`，多轮只有动作示范走 `pt-pi-distill`，特权本身要能学走 `pt-lopd`。

## 和 OPD、GRPO 的差

| | 教师是谁 | 状态从哪来 | 每个 token 的信号 | 没有有效组时 |
| --- | --- | --- | --- | --- |
| 离线 KD / SFT | 外部或演示 | 教师轨迹 | 稠密，off-policy | 仍有 交叉熵损失（CE） |
| OPD | 通常更大的外部模型 | 学生 采样轨迹（rollout） | 稠密分布 | 仍有 KL |
| OPSD | 同权重 + $y^\star$ | 学生 rollout | 稠密分布 | 仍有 KL |
| GRPO | 无教师 | 学生 rollout | 序列标量 $A$ | 全对/全错梯度没了 |

OPD 买的是一个更强的外部教师，OPSD 靠的是「评价和合理化比生成容易」：给了答案以后，模型往往能指出学生的前缀哪里不像正解。上界还是受没有特权时的容量限制，题目远远超出模型的理解范围，教师看了 $y^\star$ 也给不出有意义的下一个 token，蒸馏出来的就是噪声。论文用的是 Qwen3 量级，并不是任意小模型都能 self-distill。

和 GRPO 比，OPSD 不用为了组方差等 $G$ 条回答，也不用等终局对错。作者的设置里，学生的蒸馏长度可以短到 1k、每题 1 条 rollout，GRPO 那边用的是更长的生成和 $G=8$。代价是必须有 $y^\star$，或者 `pt-self-opd-family` 里那些伪标签；KL 方向选错，还会和拼多多那道 OPD 题的答案打架，下面会讲。

slime 的 `--use-opd` 是把外部教师的 KL 叠到 advantage 上，和 OPSD 是两回事，更不是一种 estimator，见 `slime-advantage-estimator`。

## 实现时容易踩的坑

最大的坑是 KL 方向。Thinking Machines 的 OPD 一般把采样写在学生上，目标接近 $D_{\mathrm{KL}}(\pi_S\|\pi_T)$，是反向、mode-seeking 的。Zhao 的 OPSD 在学生前缀上算全词表 $D_{\mathrm{KL}}(p_T\|p_S)$，下一 token 的期望在教师上，是正向 covering，只是前缀还是学生的。所以状态 on-policy，不代表下一 token 的 KL 一定是反向。拼多多的原问如果指外部 OPD，先答反向；如果指 OPSD 论文的公式，先写 $D(p_T\|p_S)$，见 `pt-kd-forward-vs-reverse`、`pdd-forward-reverse-kl`。

第二个坑是风格 token 霸榜。`wait`、`think`、`therefore` 这些词上的逐点 KL 往往比数学 token 大得多，不做 per-token pointwise clip 的话，损失可能主要是连接词贡献的，几百 step 后训练就可能退化。仓库默认的 clip 不是可有可无的美化。

第三个是全词表还是只算采样到的 token。默认是全词表 $D(p_T\|p_S)$；`--use_tinker_loss` 只在采到的 token 上用 $r_n=\log p_T-\log p_S$，更省显存，更像 PG，也更依赖 clip。面试时先说清用的是哪一种，再谈 KL 方向。

还有 Thinking 开关。作者早期实验里，TM-off 的学生配 TM-on 的教师，数学 token 上的 KL 更大，下游效果也更好，所以师生的生成风格要显式配对，别默认用同一个模板。师生共漂也要防：教师跟着当前 $\theta$ 一起更新，特权分布会追着学生跑，监督就变软了。把教师冻在初始策略或者用 EMA，相当于隐式加了一个 $\pi_{\mathrm{ref}}$，SR-OPSD 把这件事做成了显式插值，见 `pt-self-opd-family`。最后是泄漏，$y^\star$ 绝对不能出现在学生的上下文或者评测的输入提示（prompt）里，模板字段名、分隔符漏出去都等于开卷考试。

验收要看去掉 $y^\star$ 之后的 pass@1 和 pass@k，蒸馏 loss 说明不了问题。loss 在降、无特权的准确率不动，说明学生在拟合「看着答案时的口吻」，能力并没有迁进 $p_S$。

## 追问

**和外部 OPD 怎么选？**
有更强的教师，或者格式、工具要对齐，用 OPD。只有标准答案、模型已经读得懂解答，用 OPSD，还能省一次大模型前向。教师比学生弱的时候，外部 OPD 只会更快把偏见灌进去。

**学生终局错了，还能学吗？**
能。监督落在前缀上的下一 token 分布，和 $\hat{y}$ 最后是不是等价于 $y^\star$ 无关。这是它相对 GRPO 零方差组的主要优势。

**$y^\star$ 一定要是 CoT 吗？**
不一定。标准答案、简短解答、工具轨迹都可以当特权。信息量不够的话，教师分布和学生差不多，KL 就没有信号。Agent 那边只有动作轨迹当 PI、没有前沿 CoT 的情况，见 `pt-pi-distill`。

**和 STaR、RS 比呢？**
STaR 和 RS 是硬过滤出成功样本再做 SFT，错的样本梯度为零；OPSD 对的错的都蒸，见 `pt-star-vs-opsd`。

**会不会比 GRPO 更快塌熵？**
全词表正向是 covering，反向是 seeking，但不管哪边，风格 token 不做 clip 都会假收敛。和 `data-entropy-collapse` 一样，要对着无特权的成功率看，单看熵看不出来。
