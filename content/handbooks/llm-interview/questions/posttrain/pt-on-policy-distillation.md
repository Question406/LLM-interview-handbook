---
id: pt-on-policy-distillation
section: posttrain
order: 32
level: S
title: On-policy Distillation 为什么能同时获得 RL 的 state-distribution relevance 和蒸馏的稠密反馈？
quick: 学生先自己 rollout，teacher 再在学生实际访问的状态上给 token-level 分布信号。它避开纯离线 SFT 的 exposure bias，又比只给终局 reward 的 RL 更稠密；代价是 teacher 查询、版本一致性和 teacher 偏差。
tags:
  - Distillation
  - On-policy
  - KL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-20
sources:
  - title: Thinking Machines — On-Policy Distillation
    url: https://thinkingmachines.ai/blog/on-policy-distillation/
    type: primary
  - title: Generalized Knowledge Distillation for Auto-regressive Sequence Models
    url: https://arxiv.org/abs/2306.13649
    type: primary
---

别把 OPD 讲成「普通 KD 换了个名字」，也别讲成「RL 换了个稠密奖励」。关键只有一句：学生自己采样状态，teacher 在这些状态上给 token 级分布，于是 **状态分布跟 RL 一样 on-policy，信号密度跟蒸馏一样密**。教师若换成「同一套权重、多看特权 $y^\star$」，就是 OPSD / Self-OPD，见 `pt-opsd`、`pt-self-opd-family`；slime `--use-opd` 仍指外部教师这条，不是 OPSD。离线蒸馏的 CE 再小，也只说明学生在教师轨迹上像老师；一放到自己的 rollout 里，中间步一偏就没有监督。纯 RL 则相反：状态对了，但要等终局才知道好坏。OPD 卡在两者中间，所以代价也两边都有——要在线采样，还要持续查 teacher。

## 离线 SFT / KD 缺的是学生会走到的状态

标准 SFT 和离线蒸馏的期望在 teacher 或演示的前缀上取。学生部署时一旦在某一步走偏，后续 token 都落在从未训练过的条件分布上，错误会沿序列放大，这就是 exposure bias。把 teacher 的整段答案当标签，学的是「教师轨迹上的模仿」，不是「学生出错后如何回到正解」。长 CoT 和多轮工具尤其明显：教师从不在「调错工具之后」的前缀上说话，学生却会在那里循环道歉或重复调用。OPD 专门在这些前缀上要 teacher 的下一 token，等于补上离线数据里缺失的恢复动作。

GKD 一类工作已经指出：自回归蒸馏的正确期望应对着 **学生自己的 rollout 分布**。OPD 把这句话落到后训练配方里：先让 $\pi_{\mathrm{student}}$ 生成前缀，再查 teacher 的下一 token 分布（或 continuation），用

$$
\mathbb{E}_{x\sim\pi_{\mathrm{student}}}\big[D_{\mathrm{KL}}\big(\pi_{\mathrm{teacher}}(\cdot\mid x)\,\|\,\pi_{\mathrm{student}}(\cdot\mid x)\big)\big]
$$

或对称的 token-level 目标。注意这里 KL 的采样在学生上，属于 reverse / on-policy 方向，见 `fund-kl-directions`。slime 里 `--use-opd --opd-kl-coef` 和 advantage estimator 正交，不要说「OPD 是一种 GRPO」，见 `slime-advantage-estimator`。

## 和 RL 比，密在哪里

Outcome-only RL 的奖励往往在序列末才出现，credit assignment 要靠 advantage 把标量 smeared 到每个 token。OPD 的每个位置都有 teacher 分布，梯度直接走 $\log\pi_{\mathrm{student}}$，不需要等终局对错。这就是「稠密」：不是奖励更大，而是 **几乎每个 token 都有监督**。

和 RL 相同的部分是 state distribution：学生不会的格式、会走偏的中间步，只要自己采样到了，就能被纠正。这正是 `pt-cold-start-to-multistage-rl` 里 cold start 想提供的「可学习区域」，OPD 用在线教师代替静态示范。

它 **不是** 免费的更强 RL。Teacher 错了，学生会更高效地继承；teacher 拒答或高熵时，硬拟合会把噪声当标签。序列级 KL 和 token 级 KL 的权重、是否在坏轨迹上截断，都要显式定义。Teacher 版本要钉死：训练中途换 checkpoint，等于监督分布跳变，loss 会假跌或假涨。和学生一样，teacher 也要记 `rollout_id` 式的版本，方便事后把「哪一版老师教出来的」拆开看。

## 实现与验收

实现清单：teacher / student 的 tokenizer 与模板对齐；每次学生更新后 teacher 查询用哪一版权重；teacher 不确定时是 skip、降权还是回退到硬标签；是否混合少量离线演示防止漂移。Teacher 查询成本和版本记录是主开销，不是又一个超参故事。模板不对齐会把「看起来在蒸馏」变成噪声监督：同一句话两边切出来的 token 对不上，KL 仍可下降。工具调用场景还要锁工具列表和参数 schema，否则学生 rollout 出教师从未见过的工具名，teacher 分布没有意义。这些前置条件不满足时，先别上 OPD。

验收不要只看 imitation loss：短 imitation 下降但长 rollout 成功率不动，说明仍有 exposure bias。现场把「学生自己的错前缀」举一个具体工具调用例子，比只背 KL 公式更像做过蒸馏。

- 短 imitation 下降但长 rollout 成功率不动 → 仍有 exposure bias 或截断策略不对。
- 对分布外前缀的恢复能力（故意打乱中间步再看能否接回）比 CE 更能说明 on-policy 的价值。
- 同时报 teacher 调用成本和学生独立解题率。若离了 teacher 就不会做，说明在学查询接口而不是策略。
- 通用能力与安全：教师若爱拒答或爱套话，学生会在自己的错误前缀上把这些行为学得更死。

若要把 OPD 当探索手段，记住 reverse KL 仍偏 mode-seeking：学生会锁 teacher 的主峰。Teacher 本身覆盖不到的正确长尾，OPD 也采不出，见 `pt-kl-direction-and-exploration`。

## 和 SFT、RL 的对照

| | 状态从哪来 | 每个 token 的信号 | 主要失败 |
| --- | --- | --- | --- |
| 离线 SFT / KD | teacher / 演示 | 稠密，但在别人的前缀上 | exposure bias |
| Outcome RL | 学生自己 | 稀疏，靠 advantage 分摊 | credit assignment、hacking |
| OPD | 学生自己 | 稠密的外部 teacher 分布 | 继承 teacher 偏差、查询成本 |
| OPSD | 学生自己 | 同权重 + 特权 $y^\star$ 的分布 | 题太难则自教师没信号；$y^\star$ 泄漏 |

现场口诀：**谁采样，监督就覆盖谁的错。** 学生不会的中间步，只要自己走到了，就能被 teacher 拉回；从没走到的状态，OPD 和 RL 一样帮不上，仍要靠探索或更好的 seed。和 `pt-cold-start-to-multistage-rl` 搭配时，常用 OPD / 短 SFT 进可读区域，再用 RLVR 做可验证探索，而不是用 OPD 替代全部 RL。Teacher 查询可以隔 step 做，不必逐步都查：前缀已经很像教师时，边际信息少、成本高。隔多少步要看学生偏离速度，用和学生 rollout 的 KL 当触发，而不是固定常数。

Teacher 不确定时不要硬拟合：高熵位置降权或跳过，避免把「教师也不会」写成尖峰标签。坏轨迹是否截断，取决于你想教「如何从错误前缀恢复」还是「根本不要进入这种前缀」——前者保留，后者截断并给负的 outcome。恢复型更符合 on-policy 的初衷，但会消耗 teacher 查询；截断型更像带拒绝的 SFT，暴露偏置会回来。选题时按错误是否可恢复来分，不要全局一刀。

## 追问

- **和 RLHF 的 reverse KL 是一回事吗？** 采样都在当前策略上，但是 OPD 的目标分布是 teacher，RLHF 的参考是 $\pi_{\mathrm{ref}}$ 且外面还有奖励。一个是模仿，一个是约束漂移。把 OPD 的 KL 系数当成 PPO 的 $\beta$ 来调，会调错对象。前者越大越像老师，后者越大越不敢离开参考。
- **Teacher 比学生弱能做吗？** 可以在局部格式或工具调用上当老师，但能力上界仍被 teacher 卡住。弱教师加 on-policy 只会更快过拟合其偏见。格式 teacher 和能力 teacher 可以不是同一个模型。
- **要不要再加 outcome reward？** 可以混合：teacher 管过程密度，verifier 管终局对错。两者冲突时以可执行 oracle 为准，不要让教师文风压过正确答案。混合时要分别记录两项的贡献，避免「蒸馏 loss 下降、准确率不动」时无从下手。
- **和离线 RS 怎么选？** 学生已经常对、只需回收成功轨迹时用 RS；学生会走偏、需要对「自己的错前缀」给信号时用 OPD。Coverage 已经很高就不必每步查 teacher。RS 便宜、可审计；OPD 贵、但能教恢复。
- **和 OPSD / Self-OPD？** 外部教师用 OPD；只有标准答案、模型已能读懂解答，用同权重特权教师（`pt-opsd`）。没标签但能多数票时用 u-OPSD（`pt-u-opsd`）。Agent 只有动作示范用 π-Distill（`pt-pi-distill`）。不要把 `--use-opd` 说成 OPSD。
