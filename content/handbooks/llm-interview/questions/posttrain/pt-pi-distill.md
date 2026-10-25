---
id: pt-pi-distill
section: posttrain
order: 242
level: S
title: 前沿 Agent 只给动作不给 CoT 时，π-Distill 怎么把特权信息迁走？
quick: "把前沿模型的成功动作轨迹当训练时的特权信息 $\\mathbf{I}$，同一套权重切成看 $\\mathbf{I}$ 的教师和不看的学生，联合训练：教师在 PI 下拿奖励、同时贴近学生，学生在教师轨迹上做 IS 加权，再用 KL 覆盖教师分布。推理只部署学生，评测要关掉 $\\mathbf{I}$。"
tags:
  - OPSD
  - Agent
  - Distillation
  - Privileged Information
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Privileged Information Distillation for Language Models
    url: https://arxiv.org/abs/2602.04942
    type: primary
  - title: Self-Distilled Reasoner (OPSD)
    url: https://arxiv.org/abs/2601.18734
    type: secondary
---
π-Distill 的做法是把前沿模型的成功动作轨迹当成训练时才有的特权信息 $\mathbf{I}$，同一套权重切成一个看得到 $\mathbf{I}$ 的教师和一个看不到的学生，两个一起训，最后只部署学生。之所以要这么绕，是因为多轮工具场景里前沿模型常常只暴露动作、把 CoT 藏起来，行为看得到，推理看不到，标准监督微调（SFT）要的教师思维链就没有了。

比如一个订机票的 agent 任务，前沿模型给出的只是一串调用：先查航班、再查座位、最后下单，中间为什么这么选完全看不到。π-Distill 让同一个模型在训练时看着这串动作去做任务，学会怎么利用示范，再让不看示范的自己去追这个分布。同一套 $\theta$ 被切成

$$
\pi^{T}_{\theta}(\mathbf{o}\mid s,\mathbf{I}),\qquad \pi^{S}_{\theta}(\mathbf{o}\mid s).
$$

推理时只部署 $\pi^{S}$。这题最容易栽两处：答成普通 KD，或者把这篇里的 OPSD 和 Self-Distilled Reasoner 当成同一个公式，见 `pt-opsd`、`pt-self-opd-family`。

## 师生联合训，教师也在学怎么用 PI

不是前沿的模型，看了 PI 也不一定会用。硬把 $\mathbf{I}$ 塞给教师，师生之间的分布会拉开一道鸿沟，学生跟不上。所以 π-Distill 让教师在 PI 下采样，一边最大化环境奖励，一边用反向 KL 贴住学生，免得教师跑到学生从来没见过的模式上：

$$
J_{\mathrm{Teacher}}=\mathbb{E}_{\mathbf{o}\sim\pi^{T}}\big[R\big]-\beta D_{\mathrm{KL}}\big(\pi^{T}(\cdot\mid s,\mathbf{I})\,\big\|\,\operatorname{sg}[\pi^{S}(\cdot\mid s)]\big).
$$

学生这边，在教师的轨迹上做重要性加权的奖励，再用正向 KL 去覆盖教师的输出分布：

$$
J_{\mathrm{Student}}=\mathbb{E}_{\mathbf{o}\sim\pi^{T}}\Big[\frac{\pi^{S}}{\operatorname{sg}[\pi^{T}]}R\Big]-\beta D_{\mathrm{KL}}\big(\operatorname{sg}[\pi^{T}]\,\big\|\,\pi^{S}\big).
$$

总目标是 $J=\alpha J_{\mathrm{Teacher}}+(1-\alpha)J_{\mathrm{Student}}$。$\alpha=1$ 几乎只训教师，$\alpha=0$ 只蒸学生。采样发生在教师那边，所以学生是 off-policy 的。作者把整个过程看成变分 EM：E 步改进带 PI 的近似后验，M 步把它迁到没有 PI 的策略上。

PI 越强，比如给完整的成功轨迹、不只是一句短提示，教师越容易成功，但 $\pi^{T}$ 和 $\pi^{S}$ 也差得越远，迁移越难。所以目标是在最大化 PI 效用的同时缩小师生分布差，还不能让两者塌成同一个分布。

## 同一篇里的 OPSD：学生采样加反向 KL

$$
J_{\mathrm{OPSD}}=\mathbb{E}_{\mathbf{o}\sim\pi^{S}}\big[R\big]-\beta D_{\mathrm{KL}}\big(\pi^{S}(\cdot\mid s)\,\big\|\,\operatorname{sg}[\pi^{T}(\cdot\mid s,\mathbf{I})]\big).
$$

这是用当前学生策略采样的强化学习，PI 教师当逐步的参考信号，几何上接近 Thinking Machines 的 OPD 或 RLHF 的反向 KL。它和 Zhao 那篇 OPSD 不一样，Zhao 是在学生前缀上算全词表 $D(p_T\|p_S)$，教师常冻在初始策略，甚至可以没有环境奖励。所以被问到「你们的 OPSD」，先问一句是哪篇 arXiv：`2601.18734` 还是 `2602.04942`。

经验上，π-Distill 对 PI 的信息量和师生鸿沟更敏感，这篇的 OPSD 更依赖 PI 本身有没有足够的信息。PI 只有动作、没有隐藏的思考时，联合训练的教师可以学会「怎么利用动作示范」，学生再学「不看示范怎么做」。

## 和普通的 SFT + RL 比

直接在动作轨迹上做 SFT，是 off-policy 地克隆可见行为，exposure bias 还在，而且没有 CoT 可以克隆。SFT 加 GRPO 的话，终局奖励太稀疏，一条 50 步的工具调用链里很难判断每一步贡献了多少，见 `arl-credit`。π-Distill 用 PI 让教师更容易成功，再把成功的模式迁到没有 PI 的学生上，不需要前沿模型的 CoT。

评测一定要关掉 $\mathbf{I}$。训练日志里教师成功率很高、学生不动，说明鸿沟没压住，或者 $\alpha$ 把更新全留给了教师。

## 追问

**$\mathbf{I}$ 从哪来？**
前沿模型的成功轨迹、用规则整理出来的动作序列、环境反馈都可以。信息量不够，教师就 $\approx$ 学生，KL 没信号；太强，学生又跟不上。

**和 Zhao 的 OPSD 怎么选？**
数学题、有 GT、单轮推理，用 Zhao 那套。多轮工具、只有动作示范、还要环境奖励，用 π-Distill 或者这篇里的 RL-OPSD。

**教师和学生不同步更新会怎样？**
教师自己越变越强，就成了又一个外部专家，学生退化成普通的 off-policy KD，鸿沟又回来了。联合训练就是为了让教师走学生跟得上的高奖励模式。

**怎么防特权泄漏？**
评测的输入提示和工具返回里不能残留 $\mathbf{I}$，字段名、trajectory id 漏出去都等于开卷。
