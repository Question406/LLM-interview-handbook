---
id: pt-pi-distill
section: posttrain
order: 242
level: S
title: 前沿 Agent 只给动作不给 CoT 时，π-Distill 怎么把特权信息迁走？
quick: >-
  训练时教师看特权 $\mathbf{I}$（常是成功动作轨迹），学生不看；同一套权重联合训。教师在 PI 下最大化奖励并靠近学生，学生用教师轨迹做
  IS + $D_{\mathrm{KL}}(\pi^T\|\pi^S)$。同一篇里的「OPSD」是学生采样的 RL + 反向
  $D_{\mathrm{KL}}(\pi^S\|\pi^T)$，和 Zhao 的分布匹配 OPSD 不是一个算法。
tags:
  - OPSD
  - Agent
  - Distillation
  - Privileged Information
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-20
sources:
  - title: Privileged Information Distillation for Language Models
    url: https://arxiv.org/abs/2602.04942
    type: primary
  - title: Self-Distilled Reasoner (OPSD)
    url: https://arxiv.org/abs/2601.18734
    type: secondary
---

多轮工具场景里，前沿模型常常只暴露动作、藏 CoT。标准 SFT 需要教师思维链；没有它，行为可观察、推理不可观察。π-Distill 把成功动作轨迹当成 **训练时特权信息** $\mathbf{I}$，同一套 $\theta$ 切成

$$
\pi^{T}_{\theta}(\mathbf{o}\mid s,\mathbf{I}),\qquad \pi^{S}_{\theta}(\mathbf{o}\mid s).
$$

推理只部署 $\pi^{S}$。陷阱有两个：把它答成普通 KD；以及把这篇的 OPSD 和 Self-Distilled Reasoner 当成同一公式，见 `pt-opsd`、`pt-self-opd-family`。

## 师生联合训，教师也在学怎么用 PI

非前沿模型看了 PI 也不一定会用，硬把 $\mathbf{I}$ 塞进教师会造成师生分布鸿沟，学生跟不上。π-Distill 让教师 **在 PI 下采样**，一边最大化环境奖励，一边用反向 KL 贴住学生，避免教师跑到学生从未见过的模式：

$$
J_{\mathrm{Teacher}}=\mathbb{E}_{\mathbf{o}\sim\pi^{T}}\big[R\big]-\beta D_{\mathrm{KL}}\big(\pi^{T}(\cdot\mid s,\mathbf{I})\,\big\|\,\operatorname{sg}[\pi^{S}(\cdot\mid s)]\big).
$$

学生在教师轨迹上做重要性加权的奖励，再用正向 KL 把教师分布盖住：

$$
J_{\mathrm{Student}}=\mathbb{E}_{\mathbf{o}\sim\pi^{T}}\Big[\frac{\pi^{S}}{\operatorname{sg}[\pi^{T}]}R\Big]-\beta D_{\mathrm{KL}}\big(\operatorname{sg}[\pi^{T}]\,\big\|\,\pi^{S}\big).
$$

总目标 $J=\alpha J_{\mathrm{Teacher}}+(1-\alpha)J_{\mathrm{Student}}$。$\alpha=1$ 几乎只训教师；$\alpha=0$ 只蒸学生。采样在教师，学生是 **off-policy**。作者把它看成变分 EM：E 步改进带 PI 的近似后验，M 步迁到无 PI 策略。

PI 越强（完整成功轨迹 vs 短提示），教师越容易成功，但 $\pi^{T}$ 和 $\pi^{S}$ 差得越大，迁移越难。面试收口： **最大化 PI 效用的同时压师生鸿沟，并防止塌成同一个分布。**

## 同一篇里的 OPSD：学生采样 + 反向 KL

$$
J_{\mathrm{OPSD}}=\mathbb{E}_{\mathbf{o}\sim\pi^{S}}\big[R\big]-\beta D_{\mathrm{KL}}\big(\pi^{S}(\cdot\mid s)\,\big\|\,\operatorname{sg}[\pi^{T}(\cdot\mid s,\mathbf{I})]\big).
$$

这是 on-policy RL，把 PI 教师当稠密锚，几何上接近 Thinking Machines OPD / RLHF 的 reverse KL，**不是** Zhao 那篇在学生前缀上写全词表 $D(p_T\|p_S)$、教师常冻初始、甚至可以没有环境奖励的 OPSD。被问到「你们 OPSD」先问 arXiv：`2601.18734` 还是 `2602.04942`。

经验上 π-Distill 对 PI 的信息量和鸿沟更敏感；这篇的 OPSD 更吃 PI 里到底有没有足够内容。PI 只是动作、没有隐藏思维时，联合训的教师可以学会「怎么利用动作示范」，学生再学「不看示范怎么做」。

## 和普通 SFT + RL

SFT on 动作轨迹：off-policy 克隆可见行为，exposure bias 仍在，且没有 CoT 可克隆。SFT + GRPO：终局奖励稀疏，50-step 工具链 credit 粗，见 `arl-credit`。π-Distill 用 PI 让教师更容易成功，再把成功模式迁到无 PI 学生，不要求前沿 CoT。评测必须 **关掉 $\mathbf{I}$**。训练日志里教师成功率高、学生不动，就是鸿沟没压住，或 $\alpha$ 把更新全留给了教师。

## 追问

- **$\mathbf{I}$ 从哪来？** 前沿成功轨迹、规则整理的动作序列、环境反馈都可以。信息量不够则教师 $\approx$ 学生，KL 没信号；太强则学生跟不上。
- **和 Zhao OPSD 怎么选？** 数学题有 GT、单轮推理：Zhao。多轮工具、只有动作示范、还要环境奖励：π-Distill 或这篇的 RL-OPSD。
- **教师和学生不同步更新会怎样？** 教师独自变强等于又一个外部专家，学生变成普通 off-policy KD，鸿沟回来。联合训是为了让教师走学生跟得上的高奖励模式。
- **特权泄漏？** 评测 prompt、工具返回里不能残留 $\mathbf{I}$。字段名、trajectory id 泄漏等于开卷。
