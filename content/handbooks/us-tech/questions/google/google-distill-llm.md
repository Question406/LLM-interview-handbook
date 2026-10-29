---
id: google-distill-llm
section: google
order: 23
level: S
title: Google：大模型蒸到服务模型，on-policy distillation 和 SFT 差在哪
quick: >-
  SFT 在教师提供的前缀上学习，学生上线后一旦走偏，可能没有见过如何纠正。On-policy distillation
  改用学生自己生成的前缀，让教师给这些状态提供 logits 或标签，分布更贴近 serving，但每步生成与教师前向也更贵。
tags:
  - Google
  - Distillation
  - On-policy
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: >-
      GKD — Generalized Knowledge Distillation for Auto-regressive Sequence
      Models
    url: 'https://arxiv.org/abs/2306.13649'
    type: primary
  - title: 'Distilling Step-by-Step — Cheaper Training than RL, Better Output than SFT'
    url: 'https://arxiv.org/abs/2305.02301'
    type: primary
  - title: Gemma 2 — Improving Open Language Models at a Practical Size
    url: 'https://arxiv.org/abs/2408.00118'
    type: primary
---

SFT 和 on-policy distillation 的主要区别，是学生在哪种前缀上学习。SFT 主要沿教师轨迹，on-policy 则让学生先生成，再让教师评价它真会走到的状态。比如学生写到一半用了一个与教师不同的词，后续前缀已偏离离线答案，on-policy 的监督还能覆盖这个位置。

教师或人给 prompt $x$ 写完成 $y^\star$，SFT 优化：

$$
\mathcal{L}_{\mathrm{SFT}} = -\sum_t \log p_\theta(y^\star_t \mid x, y^\star_{1:t-1})
$$

条件里的 $y^\star_{1:t-1}$ 来自教师，数据可存档，训练便宜稳定。问题是 serving 前缀来自 $p_\theta$，学生跑偏后，离线 cross entropy（CE）没有在这些状态上教它如何恢复，这就是 exposure bias。Offline KD 在教师轨迹上做 token KL，能匹配整个分布而非单个 argmax 标签，但前缀仍是离线的。教师太强、学生容量太小时，学生也难以表达教师长尾，forward KL 可能让概率变平，单背温度 $T=2$ 不足以解释这种差别。

Google 的 GKD（Agarwal et al.）从学生或学生与教师混合策略 sampling $y\sim p_\theta$，在这些前缀上匹配教师 $p_T$。可选 forward KL、reverse KL 或 JS：正向偏 mean-seeking，倾向覆盖整个分布；反向偏 mode-seeking，更集中于高概率模式。要多样覆盖还是一个高概率答案，决定了取舍，方向本身也是超参。

每步因此多出学生生成和教师前向，可只在学生 token 上取 logits，成本高于纯 SFT。GKD 用 $\lambda$ 在离线教师轨迹与学生轨迹间插值：学生很弱时，纯 on-policy 生成质量低，教师信号可能噪声较大；一直停在纯 SFT，又保留上线跑偏的问题。学生生成还应与 serving decoding 策略对齐，例如线上温度 0.7，训练却贪心，就又引入分布差异。

它与 RLHF 的监督来源不同。RLHF 优化奖励，用 reference policy KL 作锚；on-policy distillation 直接用教师 logits，没有 reward model 的 calibration 和 reward hacking 问题，但会继承教师偏见。只有教师答案、拿不到 logits 时，只能退回 SFT / 序列级 CE，无法监督前缀上其他高概率错词；容量以外的分布也不能保证无损蒸给学生。

Gemma 2 公开写了从更大教师 distillation。Gemini 很大，而 Flash / Gemma 量级服务模型更关心延迟、成本、激活参数、KV 和 decode 步数。distillation 还可传递拒答、工具格式、多模态接口，或让短窗口学生复现教师长原则 prompt 的行为，这与 context distillation 相关。Distilling Step-by-Step 用教师理由作额外监督，小学生也能学习推理格式，不一定要 RL；投机草稿也可由 distillation 得到。

MoE 教师蒸到稠密学生，传的是激活分布，路由行为和“专家 3 的功能”不会直接搬过去。蒸完之后也常需窄领域 SFT / RL 处理产品策略、安全与工具，能力和行为先验本身不等于完成上线验收。

相关：`google-cot-reason`、`google-spec-decode`、`google-gemini-moe`
