---
id: pt-lopd
section: posttrain
order: 243
level: A
title: LOPD 为什么把特权上下文改成可学习的 latent，而不是再手写一种 $y^\star$？
quick: >-
  手写的特权总被格式卡住，所以 LOPD 改成从经验里学：检索成功轨迹，压成只给自教师看的连续 latent token，在学生前缀上用 reverse KL
  蒸给学生。为了防止教师塌成学生，再加一个 privileged-margin 约束。
tags:
  - OPSD
  - Agent
  - Distillation
  - Latent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Latent On-Policy Self-Distillation
    url: 'https://arxiv.org/abs/2608.13040'
    type: primary
  - title: Self-Distilled Reasoner (OPSD)
    url: 'https://arxiv.org/abs/2601.18734'
    type: secondary
---
LOPD 想解决的是特权格式由人来定这件事。OPSD、u-OPSD、π-Distill 都还在换不同的手写特权，GT、多数票、动作轨迹，见 `pt-self-opd-family`；再发明一种文本特权，照样被设计者选的格式卡住。LOPD 干脆把特权改成从经验里学出来的连续上下文，留下什么由自教师自己决定。

举个例子，一个代码 agent 修一类依赖冲突的 bug。经验库里已经有几条以前修成功的轨迹，但很难提前定下「标准解答」长什么样。LOPD 把这些成功轨迹检索出来，压成几个 latent token 只喂给教师，教师就像「看过前人怎么修的」，再在学生自己走出来的前缀上告诉它下一步该怎么偏。

## 学生照旧 sampling，教师多看一段 latent

学生只凭任务和交互历史 $\bm{s}$ 滚轨迹。从经验库里检索 top-$J$ 条相关的成功轨迹，composer 把它们压成 $K$ 个连续 token $\bm{c}_{\phi}$，骨干冻住的教师看的是 $[\bm{s};\bm{c}_{\phi}]$。然后在学生前缀上做 reverse KL，论文默认用 top-$M$ 加一个 tail bucket：

$$
\mathcal{L}_{\mathrm{distill}}=\mathbb{E}\big[D_{\mathrm{KL}}(\tilde{p}^{S}\|\tilde{p}^{T})\big].
$$

$\bar{\theta}$ 是冻住的，但前向对 $\bm{c}_{\phi}$ 可微，梯度能一路回到 composer。骨架和 Zhao 的 OPSD 一样，那边教师冻在初始权重、特权是文本 $y^\star$，这边只是把 $\Phi$ 从一条规则换成了可学的 $\phi$。

推理时经验库、检索和 composer 全部扔掉，只部署学生。如果线上还得靠检索才做得出来，说明能力没迁进 $\pi^{S}$，训练时只是在开卷。

## 为什么必须加 privileged-margin

不加约束的话，composer 有一条最小化 KL 的捷径：让 $p^{T}\to p^{S}$。特权变成没信息的噪声，损失照样往下走，教师却什么有用的东西都没给。所以要定义 token 级的特权

$$
\delta_{t,n}=\log\pi^{T}(a_{t,n}\mid\bm{s},\bm{c}_{\phi})-\operatorname{sg}[\log\pi^{S}(a_{t,n}\mid\bm{s})],
$$

再用轨迹验证结果 $A(\bm{\tau})=2 r(\bm{\tau})-1$ 加权，要求平均特权 $\Delta(\phi)\ge m$，论文里 $m=0.05$。意思是成功轨迹上，教师要比学生更偏好实际走的那个 token；失败轨迹上反过来压。$\Delta\lt m$ 时对偶变量 $\beta$ 把惩罚抬上去。另外还有一项把 $\bm{c}_{\phi}$ 锚在 cold-start 的 $\phi_0$ 附近，防止 latent 表示漂得太远。

SR-OPSD 用 $\pi_{\mathrm{ref}}$ 插值，防的也是自教师塌成学生，只是 LOPD 的塌缩发生在可学习的上下文上，SR-OPSD 的发生在 EMA 权重上。

## 和其他方法怎么比

别把它背成又一个新公式，放在家族里比一比更清楚。和 OPSD 比，它不需要 gold chain of thought（CoT，即分步推理过程），特权从经验检索来，适合 agent、代码这种成功轨迹比标准解答好找的领域。和 u-OPSD 比，它不需要可解析的答案空间，也不把多数票当文本教师。和 π-Distill 比，它不用联合训一个会读文本 PI 的教师，教师骨干冻住，学的只是 composer。和 GRPO 比，它还是要环境 $r$ 来算 margin，但稠密监督落在 distillation KL 上，sampling 轨迹（rollout）预算可以更小，论文报的 rollout 比 GRPO / Skill-SD 少约 $30\%$。

光有检索是不够的，把同样的轨迹当文本塞给教师，就又是一种手写特权。ablation 要回答的是：可学习的压缩比「检索 + 原文拼接」多出了什么。

## 追问

**latent 会不会泄漏给学生？**
架构上学生的上下文里没有 $\bm{c}_{\phi}$。实现上要保证 embedding 注入只进教师的前向，评测时把检索关掉。

**没有成功经验怎么办？**
composer 的 cold-start 依赖成功轨迹库，冷启动还是要靠 RS、弱教师或者少量 demo，见 `pt-rejection-sampling-vs-rl`。LOPD 不是从零开始自我对弈。

**这和 agent 的记忆、技能库是一回事吗？**
不是。训练时的 latent 是教师特权，推理时并不存在。Skill 文本可以当检索源，但 LOPD 的出发点就是别把技能格式写死成教师的条件。

**KL 是哪个方向？**
这篇用的是 $D_{\mathrm{KL}}(p^{S}\|p^{T})$，和 Zhao 默认的 $D(p_T\|p_S)$ 正好相反，又是一层命名坑。先说期望在谁身上取，再报左右。
