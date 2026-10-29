---
id: sys-rl-fw-clip-zero
section: systems
order: 236
level: S
title: TRL / veRL / OpenRLHF 里为什么 clip fraction 会一直是 0？
quick: >-
  一批 rollout 只做一次 `optimizer.step()` 时，$\pi_\theta$ 还没离开
  $\pi_{\mathrm{old}}$，$\rho\approx 1$，clip 自然恒为 0。只有对同一批数据做第二次更新才会出现非零。
tags:
  - TRL
  - VeRL
  - OpenRLHF
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Proximal Policy Optimization Algorithms
    url: 'https://arxiv.org/abs/1707.06347'
    type: primary
  - title: 群体相对策略优化 (GRPO) — verl 文档
    url: 'https://verl.readthedocs.io/en/latest/algo/grpo.html'
    type: primary
  - title: 深入理解目前主流RL训练框架中的重要性采样机制
    url: 'https://blog.csdn.net/Cyril_KI/article/details/161460206'
    type: secondary
---

我会先查同一批 rollout 实际做了几次 `optimizer.step()`。如果只做一次，计算 loss 时当前 $\pi_\theta$ 还没有离开 sampling 时的 $\pi_{\mathrm{old}}$，$\rho=\pi_\theta/\pi_{\mathrm{old}}\approx 1$，clip fraction $=0$ 通常就是预期。Clip 统计的是 $\rho$ 越出 $[1-\varepsilon,1+\varepsilon]$ 的比例；必须先发生参数更新，后续计算才可能看到越界。Surrogate 公式见 `code-ppo-clip`、`pt-ppo-clip`。

## 先对照更新循环

标准 PPO 先用 $\pi_{\mathrm{old}}$ sampling 并冻结 old logp，再对同一批轨迹做多次 mini-batch 更新。第一次 step 时 $\rho\approx 1$；$\theta$ 更新后，同一 token 的 $\rho$ 才开始偏离 1，越界一侧会被 $\min(\rho A,\mathrm{clip}(\rho)A)$ 截断梯度。`ppo_epochs` 和 mini-batch 次数决定数据复用多少次，推导见 `pt-pg-to-ppo-to-grpo`。长 CoT 反复 backward 会增加显存和耗时，LLM 训练中因此常选择单步使用。

Ray / Trainer 循环里如果生成完只 `step` 一次，下一包立即重新 rollout，更新就接近带 KL 的 REINFORCE。这样配置可以节省长 CoT 的复用成本，但说明稳定性时要对应 KL、组 baseline 和学习率，不能再把未触发的 clip 当作保护。

## 再检查框架配置和 metric definition

- **TRL。** 看 `steps_per_generation * num_iterations` 是否大于实际的生成间隔（文档里的 `generate_every` 一类）。若每积累完梯度就马上对新 rollout 更新，没有「旧策略上的第二遍」，clip 统计接近 0。
- **veRL。** `ppo_mini_batch_size` 等于整包且 `ppo_epochs=1` 时，整包一次更新，$\rho$ 来不及偏离。要把同一批轨迹切成更小 mini-batch 或 `ppo_epochs>1`，后面的 micro-batch 才会看到非 1 的 ratio。文档里的 `ppo_*` 前缀对 GRPO **同样生效**，不要说「我跑的是 GRPO 所以没有 clip 配置」。动态 batch 打开后，「整包」不再是固定条数，更要以是否对同一 `rollout_id` 多次 `step` 为准，见 `sys-verl-dynamic-bsz`。
- **OpenRLHF。** `max_epochs` 与 `train_batch_size` 决定对同一批 rollout 做几次真正的 DeepSpeed `step`。Epoch 名义上大于 1、但实际每条数据只进一次 optimizer，统计照样是 0。

排查时先打印同一批数据被 `step` 了几次，再确认 old logp 是否冻结，最后检查 clip 实现。gradient accumulation 只把多个 micro-batch 合成一次更新，累积期间 $\theta$ 不变，$\rho$ 仍然是 1，因此不算第二次 step。

CISPO 把 clip 对象换成 IS 权重并 detach，梯度仍走 $\log\pi$，见 `pt-cispo`。即便如此，$\rho\approx 1$ 时权重截断也不会触发，监控上仍可能「clip 为 0」。先确认有没有第二次 step，再讨论算法变体。

实验记录里把每条轨迹的更新次数和 $\varepsilon$、$\beta$ 一起写清。次数为 1 时，clip 为 0 按预期处理，稳定性主要检查对 $\pi_{\mathrm{ref}}$ 的 KL、组相对 baseline、学习率和温度。这样评审中的假设能和实际循环对上，也能避免长期为零的面板失去诊断作用。

反过来，clip fraction 很高说明复用过猛或 stale 过大：学习率、epoch、advantage 尺度、异步 policy age 都要一起看。美团「GRPO 为什么还要 clip」问的是 **要不要信任域**（`meituan-grpo-why-clip`）；本题问的是 **你配的循环有没有让信任域真正转起来**。两题连着答。

同一批轨迹上：step 0 的 $\rho$ 在 1 附近，clip fraction $\approx 0$；后续 mini-batch / epoch，$\theta$ 离开 old，ratio 分布变宽，越出 $\varepsilon$ 的比例上升。若你的曲线从第一步到最后一步都贴零，说明中间没有对这批数据做第二次真正的 `step`，或 old logp 每步都在用「当前 $\theta$」重算导致 $\rho$ 被重置为 1。后一种是 logging convention 错误：old 必须冻结在 sampling 时（或 sampling 后那一次训练图 forward），不能跟 new 用同一份即时 logp。

监控要和 KL（对 $\pi_{\mathrm{ref}}$）、熵一起看。Clip 为 0 且 KL 也几乎为 0：可能更新太弱。Clip 为 0 但 KL 在涨：单步 on-policy 仍在离开参考，护栏来自 KL 不是 clip。不要只盯一个标量。Ratio 直方图比单一 clip fraction 更有用：全部贴在 1 上，就是没发生第二次更新；已经散开却分数仍为 0，才去查 $\varepsilon$ 是否过大或统计 mask 是否把越界 token 排除了。

logging convention 和 algorithm convention 必须分开查。统计时还要注意 response mask：把 prompt token 算进 clip fraction，会把大量 $\rho=1$ 的前缀灌进均值，分数被稀释成假零。只在生成段上统计，才和 PPO 论文里的 action 一致，见 `sys-rl-response-mask`。排查时把「更新次数、old 是否冻结、mask 是否只盖 response」写成检查清单。单步 run 就把 clip 面板摘掉，避免假零消耗值班 attention。

如果保留面板，就并列显示本 batch 的 optimizer.step 次数，次数为 1 时将 clip=0 标成预期。

## 追问

**第一次 mini-batch 就该是 0 吗？**
对。即使 `ppo_epochs>1`，每个 epoch 的第一刀也接近 0，后续更新才可能升高。只看 step 0 的标量会误判。应按 epoch 内的 step 下标分组统计画，而不是全局平均一条线。
**重算 logp 会让 clip 变假吗？**
会，如果 old / new 混用了引擎数值。训练图对齐后，$\rho$ 才有资格进 clip 统计，见 `meituan-verl-recompute-logprob`。引擎 logp 当 old、训练 logp 当 new，会凭空造出大量假越界。
**想观察 clip 最低怎么配？**
同一批 rollout 上 `ppo_epochs>1` 或缩小 `ppo_mini_batch_size`，并确认中间没有重新 generate。不要靠把 $\varepsilon$ 改极小来「做出」非零分数。$\varepsilon$ 极小只会让有第二次 step 时分数虚高，诊断意义更差。
**GRPO 单步是不是就该关掉 clip？**
可以显式改成无 clip 的 REINFORCE / CISPO，但那是换算法。留着 clip 配置却永远为 0，只是让监控失效。若决定单步，把 clip fraction 从看板撤掉，改盯 KL 和熵，避免值班被假零误导。
