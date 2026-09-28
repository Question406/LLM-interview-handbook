---
id: pt-lopd
section: posttrain
order: 243
level: A
title: LOPD 为什么把特权上下文改成可学习的 latent，而不是再手写一种 $y^\star$？
quick: >-
  OPSD 家族的差别几乎都在「教师多看什么」。LOPD 不再指定答案 / 技能 / 轨迹文本，而是检索经验、压成连续
  latent token 条件自教师，学生仍只看任务状态。反向 KL 蒸学生；privileged-margin 防止 composer
  把教师分布拉向学生。推理只留学生，检索和 latent 都丢掉。
tags:
  - OPSD
  - Agent
  - Distillation
  - Latent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Latent On-Policy Self-Distillation
    url: https://arxiv.org/abs/2608.13040
    type: primary
  - title: Self-Distilled Reasoner (OPSD)
    url: https://arxiv.org/abs/2601.18734
    type: secondary
---

OPSD / u-OPSD / π-Distill 都还在换手写特权：GT、多数票、动作轨迹，见 `pt-self-opd-family`。再发明一种文本特权，仍然被设计师选的格式卡住。LOPD 把特权改成从经验里学出来的连续上下文，自教师自己决定留下什么。

## 学生照旧采样，教师多看 latent

学生只凭任务与交互史 $\bm{s}$ 滚轨迹。经验库里检索 top-$J$ 条相关成功轨迹，composer 压成 $K$ 个连续 token $\bm{c}_{\phi}$，冻骨干的教师看 $[\bm{s};\bm{c}_{\phi}]$。在学生前缀上做 reverse KL（论文默认 top-$M$ + tail bucket）

$$
\mathcal{L}_{\mathrm{distill}}=\mathbb{E}\big[D_{\mathrm{KL}}(\tilde{p}^{S}\|\tilde{p}^{T})\big].
$$

$\bar{\theta}$ 冻住，但前向对 $\bm{c}_{\phi}$ 可微，所以梯度能回到 composer。这和 Zhao OPSD「教师冻初始、特权是文本 $y^\star$」同骨架，只是 $\Phi$ 从规则变成 $\phi$。

推理丢掉经验库、检索和 composer，只部署学生。若线上还要检索才能做，说明能力没迁进 $\pi^{S}$，只是训练时开卷。

## 为什么必须加 privileged-margin

无约束时，composer 最小化 KL 的捷径是让 $p^{T}\to p^{S}$：特权变成无信息噪声，loss 假降。定义 token 级特权

$$
\delta_{t,n}=\log\pi^{T}(a_{t,n}\mid\bm{s},\bm{c}_{\phi})-\operatorname{sg}[\log\pi^{S}(a_{t,n}\mid\bm{s})],
$$

再用轨迹验证 $A(\bm{\tau})=2 r(\bm{\tau})-1$ 加权，要求平均特权 $\Delta(\phi)\ge m$（论文 $m=0.05$）。对成功轨迹，教师应比学生更偏好实际采取的 token；失败轨迹则反向压。对偶 $\beta$ 在 $\Delta\lt m$ 时抬罚。再加一项把 $\bm{c}_{\phi}$ 锚在 cold-start $\phi_0$，防止 latent 漂飞。

这和 SR-OPSD 用 $\pi_{\mathrm{ref}}$ 插值是同一类「别让自教师塌成学生」，只是 LOPD 的塌缩发生在可学习上下文上，而不是 EMA 权重上。

## 和谁比、别背成新公式

- 相对 OPSD：不必 gold CoT，特权从经验检索来，适合 agent / 代码这种「成功轨迹比标准解答好找」的域。
- 相对 u-OPSD：不必可解析答案空间，也不把多数票当文本教师。
- 相对 π-Distill：不必联合训一个会用文本 PI 的教师；教师骨干冻住，学的是 composer。
- 相对 GRPO：仍要环境 $r$ 来算 margin，但密集监督在蒸馏 KL 上，rollout 预算可以更小。论文报过低于 GRPO / Skill-SD 约 $30\%$ 的 rollout。

检索本身不够：把同样轨迹当文本塞进教师，是又一种手写特权。消融要回答的是可学习压缩有没有比「检索 + 原文拼接」多出来。

## 追问

- **latent 会不会泄漏到学生？** 架构上学生上下文不含 $\bm{c}_{\phi}$。实现上要保证 embedding 注入只进教师前向。评测关掉检索。
- **没有成功经验怎么办？** composer cold-start 依赖成功轨迹银行。冷启动仍要 RS / 弱教师 / 少量 demo，见 `pt-rejection-sampling-vs-rl`。LOPD 不是从零自我对弈。
- **和记忆 / 技能库？** 训练时的 latent 是教师特权，不是推理时 memory。Skill 文本可以当检索源，但 LOPD 的点是不要把技能格式写死成教师条件。
- **KL 方向？** 这篇用 $D_{\mathrm{KL}}(p^{S}\|p^{T})$，和 Zhao 默认的 $D(p_T\|p_S)$ 又是一层命名坑。先写期望在谁身上，再报左右。
