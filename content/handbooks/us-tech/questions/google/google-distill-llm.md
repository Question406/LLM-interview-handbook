---
id: google-distill-llm
section: google
order: 23
level: S
title: Google：大模型蒸到服务模型，on-policy 蒸馏和 SFT 差在哪
quick: >-
  SFT 是在教师轨迹上做 CE，学生前缀来自教师，离线、便宜、会暴露偏差。On-policy 蒸馏让学生自己滚序列，教师给这些前缀打
  logits / 标签，分布对着 serving 对齐。Gemma 一类服务模型常用教师蒸馏；别把「用教师数据微调」和「在学生分布上匹配教师」混成一句。
tags:
  - Google
  - Distillation
  - On-policy
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: GKD — Generalized Knowledge Distillation for Auto-regressive Sequence Models
    url: https://arxiv.org/abs/2306.13649
    type: primary
  - title: Distilling Step-by-Step — Cheaper Training than RL, Better Output than SFT
    url: https://arxiv.org/abs/2305.02301
    type: primary
  - title: Gemma 2 — Improving Open Language Models at a Practical Size
    url: https://arxiv.org/abs/2408.00118
    type: primary
---

Gemini 很大，线上很多表面要的是 Flash / Gemma 量级的延迟和价格。Google 研究岗问蒸馏，要听 on-policy 和 SFT 的分布差，不是背「温度 $T=2$ 的 KL」。GKD（Agarwal et al.）是 Google 把这件事写成 on-policy 的那篇；Gemma 2 公开写了从更大教师蒸馏。CoT 教师轨迹见 `google-cot-reason`。

## SFT：学生在教师的前缀上学

教师（或人）给 prompt $x$ 写完成 $y^\star$。学生最小化

$$
\mathcal{L}_{\mathrm{SFT}} = -\sum_t \log p_\theta(y^\star_t \mid x, y^\star_{1:t-1})
$$

前缀 $y^\star_{1:t-1}$ 来自教师，不来自学生自己。便宜、稳定、数据可存档。问题是暴露偏差：上线时前缀来自 $p_\theta$，训练时从没在这些前缀上挨过教师的纠正。学生一开始学得像，一跑偏就离开教师轨迹，后面的 CE 帮不上。

Token 级 KL 在教师轨迹上（offline KD）好一点：同一前缀上对齐整分布，不只是 argmax 标签。前缀仍是离线的。教师很强、学生很弱时，教师分布的长尾学生盖不住，forward KL 会逼学生抹平。

## On-policy：在学生自己滚出来的前缀上匹配教师

GKD 的核心：从学生（或学生与教师的混合）采样 $y\sim p_\theta$，再在这些前缀上让学生去匹配教师 $p_T$。广义上可以用正向 KL、反向 KL 或 JS。直觉：

- 学生会犯错的地方，教师当场给 logits，梯度打在 serving 真会走到的状态上。
- 反向 KL 偏 mode-seeking，学生集中覆盖教师的高峰，生成更尖；正向 KL 偏 mean-seeking，更想盖全，容易糊。

实现上每步要跑学生生成 + 教师前向（可只在学生 token 上取 logits）。比纯 SFT 贵。混合：一部分离线教师轨迹、一部分学生轨迹，用 $\lambda$ 插值，GKD 论文就是这个旋钮。学生太差时纯 on-policy 采样全是垃圾，教师信号噪；太早停在纯 SFT，上线一跑偏。

和 RLHF 别并成一句。RLHF 优化的是奖励，KL 打在参考策略上当锚。On-policy 蒸馏没有奖励模型，教师 logits 就是监督。没有 RM 的校准问题，也没有「奖励 hacking」；有的是教师自己的偏见会被学生原样接过来。

## 服务模型要蒸什么

Gemma 2：公开说知识蒸馏自更大教师，不只是小模型从头训。产品上蒸馏目标通常不是 MMLU 最高，而是：

- 延迟 / 成本：激活参数、KV、decode 步数。投机草稿模型也可以是蒸馏产物，见 `google-spec-decode`。
- 行为：拒答、工具格式、多模态接口。教师带长原则 prompt，学生要在短窗口里复现，这是 context distillation 的亲戚，别和 token KD 混名。
- 推理格式：Distilling Step-by-Step 用教师的理由当额外监督，学生更小也能跟理由，不一定要上 RL。

MoE 教师蒸稠密学生：路由行为蒸不走，蒸的是激活分布。别指望学生学会「专家 3 的功能」。教师若是 Gemini MoE，见 `google-gemini-moe`。

错法：说蒸馏一定无损（分布在学生容量外不可复现）；说 on-policy 就是 RL；只在教师轨迹上做 KL 却声称解决了暴露偏差。

## 追问

- **KL 方向怎么选？** 要覆盖教师多样输出，偏正向 KL；要一个高概率好答案，偏反向 KL 或 JS。GKD 把选择做成超参，不要背死。
- **学生生成用贪心还是采样？** 要对齐 serving。线上温度 0.7，蒸馏时贪心，前缀分布又偏了。
- **没有教师 logits 只有答案？** 退回 SFT / 序列级 CE。序列级没法纠正前缀上的其它高概率错词。能拿到 logits 就拿。
- **蒸馏之后还要不要 SFT / RL？** 常常还要。蒸馏给能力上限和行为先验；产品策略、安全、工具还要窄数据。顺序要说得出，别蒸完直接当上线。
