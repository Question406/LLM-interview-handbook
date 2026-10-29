---
id: pt-on-policy-distillation
section: posttrain
order: 32
level: S
title: >-
  On-policy Distillation 为什么能同时获得 RL 的 state-distribution relevance 和
  distillation 的稠密反馈？
quick: >-
  学生先自己 sampling，教师再在学生实际写出的前缀上给下一 token 的分布。状态是学生自己会走到的，所以能覆盖离线 SFT 没见过的错误状态；每个
  token 都有教师信号，比只在终局给 reward 的 RL 密得多。代价是教师查询成本、版本同步，以及会继承教师自己的偏差。
tags:
  - Distillation
  - On-policy
  - KL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Thinking Machines — On-Policy Distillation
    url: 'https://thinkingmachines.ai/blog/on-policy-distillation/'
    type: primary
  - title: Generalized Knowledge Distillation for Auto-regressive Sequence Models
    url: 'https://arxiv.org/abs/2306.13649'
    type: primary
---
OPD 两头都占到，是因为它让学生自己 sampling 状态，再让 teacher model（teacher）在这些状态上给 token 级的分布：状态分布和 RL 一样是 on-policy 的，信号密度和 distillation 一样稠密。它卡在离线 distillation 和纯 RL 中间，所以两边的代价也都有，要在线 sampling，还要一直查 teacher。

拿多轮工具调用举例最清楚。学生调错了一个工具，接下来开始反复道歉、重复调用。离线 distillation 的教师轨迹里从来没有「调错工具之后」这个前缀，学生在这里完全没有监督；纯 RL 要等整条轨迹结束才知道失败了。OPD 直接在这个错前缀上问 teacher 下一个 token 该是什么，等于补上了离线数据里缺的恢复动作。

所以别把 OPD 讲成「普通 KD 换了个名字」，也别讲成「RL 换了个稠密奖励」。教师换成「同一套权重、多看特权 $y^\star$」的话，就是 OPSD / Self-OPD，见 `pt-opsd`、`pt-self-opd-family`；slime 里的 `--use-opd` 指的还是外部教师这条，和 OPSD 不是一回事。

## 离线 SFT / KD 缺的是学生自己会走到的状态

标准 SFT 和离线 distillation 的期望，是在 teacher 或演示的前缀上取的。学生部署时只要某一步走偏，后面的 token 全落在没训练过的条件分布上，错误沿着序列放大，这就是 exposure bias。离线 distillation 的 cross entropy loss（CE）再小，也只说明学生在教师的轨迹上像老师，学的是模仿教师轨迹，没学会出错以后怎么回到正解。长 chain of thought（CoT，即分步推理过程）和多轮工具调用上这个问题特别明显，一放进学生自己的 sampling 轨迹（rollout），中间步一偏就没人管了。

GKD 一类工作已经指出，autoregressive distillation 的期望应该对着学生自己的 rollout 分布取。OPD 把这句话落成了后训练配方：先让 $\pi_{\mathrm{student}}$ 生成前缀，再查 teacher 的下一 token 分布（或者 continuation），用

$$
\mathbb{E}_{x\sim\pi_{\mathrm{student}}}\big[D_{\mathrm{KL}}\big(\pi_{\mathrm{teacher}}(\cdot\mid x)\,\|\,\pi_{\mathrm{student}}(\cdot\mid x)\big)\big]
$$

或者对称的 token-level 目标。这里 KL 是在学生 upsampling 的，属于 reverse / on-policy 方向，见 `fund-kl-directions`。slime 里的 `--use-opd --opd-kl-coef` 和 advantage estimator 是正交的，所以别说「OPD 是一种 GRPO」，见 `slime-advantage-estimator`。

## 和 RL 比，密在哪里

只看最终结果的 RL，奖励往往在序列末尾才出现，要靠 advantage 把一个标量摊到每个 token 上做 credit assignment。OPD 每个位置都有 teacher 分布，梯度直接走 $\log\pi_{\mathrm{student}}$，不用等终局对错。稠密说的是几乎每个 token 都有监督，跟奖励大小没关系。

和 RL 相同的是 state distribution。学生不会的格式、会走偏的中间步，只要自己 sampling 到了，就能被纠正。这正是 `pt-cold-start-to-multistage-rl` 里 cold start 想提供的「可学习区域」，OPD 用在线教师代替了静态示范。

反过来，teacher 错了，学生会更高效地把错学过去；teacher 拒答或者高熵的地方，硬拟合会把噪声当标签。序列级和 token 级 KL 怎么加权、坏轨迹要不要截断，都要明确定下来。teacher 版本要固定，训练中途换 checkpoint，等于监督分布突然跳变，损失（loss）会假跌或假涨。teacher 也要像学生一样记 `rollout_id` 式的版本，方便事后拆开看是哪一版老师教出来的。

## 实现与验收

动手前先把几件事对齐。teacher 和 student model（student）的 tokenizer 与模板要对齐，同一句话两边切出来的 token 对不上，KL 照样能降，distillation 的却是噪声。学生每次更新后，teacher 查询用哪一版权重要说清楚。teacher 不确定时是跳过、降权还是回退到 hard labels，要事先定。要不要混一点离线演示防漂移，也要定。工具调用场景还要锁住工具列表和参数 schema，不然学生 rollout 出一个教师没见过的工具名，teacher 的分布就没有意义。主要开销在 teacher 查询成本和版本记录上，这几条前置条件不满足，先别上 OPD。

验收别只看 imitation loss。短的 imitation 在降、长 rollout 的成功率不动，说明还有 exposure bias，或者截断策略不对。故意打乱中间步，看学生能不能接回来，这种对 out-of-distribution 前缀的恢复能力比 CE 更能说明 on-policy 的价值。teacher 调用成本和学生独立解题率要一起报，离了 teacher 就不会做，说明学生学的是查询接口，策略没学到。通用能力和安全也要看，教师爱拒答或者爱说套话，学生会在自己的错误前缀上把这些行为学得更死。

想拿 OPD 当探索手段的话要记住，reverse KL 还是偏 mode-seeking，学生会锁住 teacher 的主峰，teacher 自己覆盖不到的正确长尾，OPD 也采不出来，见 `pt-kl-direction-and-exploration`。

## 和 SFT、RL 的对照

| | 状态从哪来 | 每个 token 的信号 | 主要失败 |
| --- | --- | --- | --- |
| 离线 SFT / KD | teacher / 演示 | 稠密，但在别人的前缀上 | exposure bias |
| 最终结果 RL | 学生自己 | 稀疏，靠 advantage 分摊 | credit assignment、hacking |
| OPD | 学生自己 | 稠密的外部 teacher 分布 | 继承 teacher 偏差、查询成本 |
| OPSD | 学生自己 | 同权重 + 特权 $y^\star$ 的分布 | 题太难则自教师没信号；$y^\star$ 泄漏 |

这张表的意思是谁 sampling，监督就覆盖谁的错。学生不会的中间步，只要自己走到了，teacher 就能把它拉回来；从来没走到的状态，OPD 和 RL 一样帮不上，还是要靠探索或者更好的 seed。和 `pt-cold-start-to-multistage-rl` 搭配时，常见的做法是先用 OPD 或短 SFT 把模型带进可读区域，再用 RLVR 做可验证的探索，OPD 并不替代全部 RL。

teacher 查询可以隔几个 step 做一次，前缀已经很像教师时，边际信息少、成本高。隔多少步看学生偏离得多快，用和学生 rollout 的 KL 当触发条件，别定死一个常数。teacher 不确定的位置别硬拟合，高熵处降权或跳过，免得把「教师也不会」写成尖峰标签。坏轨迹截不截断，看你想教的是「从错误前缀恢复」还是「根本别进这种前缀」：前者保留，后者截断并给负的 outcome。恢复型更符合 on-policy 的初衷，但更耗 teacher 查询；截断型更像带拒绝的 SFT，暴露偏置会回来。按错误能不能恢复来分题，别全局一刀切。

## 追问

**和 RLHF 里的 reverse KL 是一回事吗？**
sampling 都在当前策略上，但 OPD 的目标分布是 teacher，RLHF 的参考是 $\pi_{\mathrm{ref}}$，外面还有奖励。一个是模仿，一个是约束漂移。把 OPD 的 KL 系数当成 PPO 的 $\beta$ 来调，就调错了对象：前者越大越像老师，后者越大越不敢离开参考。

**teacher 比学生弱，还能做吗？**
在局部的格式或工具调用上可以当老师，但能力上界还是被 teacher 卡住，弱教师加 on-policy 只会更快 overfitting 它的偏见。格式 teacher 和能力 teacher 可以是两个不同的模型。

**要不要再加 outcome 奖励分数（reward）？**
可以混着用，teacher 管过程的密度，验证器（verifier）管终局对错。两者冲突时以可执行的 oracle 为准，别让教师的文风压过正确答案。两项的贡献要分开记，不然「distillation loss 在降、准确率不动」时无从下手。

**和离线 RS 怎么选？**
学生已经经常做对、只需要回收成功轨迹时用 RS；学生会走偏、需要在自己的错前缀上给信号时用 OPD。coverage 已经很高，就没必要每步都查 teacher。RS 便宜、可审计，OPD 贵，但能教恢复。

**和 OPSD / Self-OPD 怎么分？**
有外部教师用 OPD；只有标准答案、模型已经能读懂解答，用同权重的特权教师（`pt-opsd`）；没有标签但能做多数票，用 u-OPSD（`pt-u-opsd`）；Agent 只有动作示范，用 π-Distill（`pt-pi-distill`）。`--use-opd` 别说成 OPSD。
