---
id: meta-continual-pt
section: meta
order: 18
level: A
title: Meta：continual pretrain / 领域自适应，灾难遗忘怎么防
quick: "领域继续预训练从已有 Llama 权重接着学 next-token，能比从零省训练量，但领域过纯会损失通用能力。可重新 warmup 再衰减学习率、回放旧 mix，并持续同时评领域、通用与安全；领域 CPT 改数据分布，长窗 CPT 改 $T$ 与 RoPE，两者可以叠加。"
tags:
  - Meta
  - Llama
  - Continual Pretraining
  - Forgetting
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Code Llama — Open Foundation Models for Code
    url: https://arxiv.org/abs/2308.12950
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Don't Stop Pretraining — Adapt Language Models to Domains and Tasks
    url: https://arxiv.org/abs/2004.10964
    type: primary
  - title: Simple and Scalable Strategies to Continually Pre-train Large Language Models
    url: https://arxiv.org/abs/2403.08763
    type: primary
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: secondary
---

领域继续预训练可以利用已有通用模型，更省 token 地学习领域语料，但要同时控制灾难遗忘。它仍做 next-token 预测，使用无监督领域数据，学习率比 SFT 大、token 数多几个数量级，不能用指令微调代替。

Code Llama 给了具体例子：从 Llama 2 初始化，后者约 $2\mathrm{T}$ token 中代码约 $80\mathrm{B}$，再用约 $85\%$ 代码的 mix 训练 $500\mathrm{B}$，70B 版本为 $1\mathrm{T}$。7B 的同 mix 从零对照，最终损失约相当于 CPT 训练一半时，说明通用初始化能减少后续训练量。之后还做 infill 与长窗微调，但图中 helpfulness RM 分随代码能力上升而下降，也显示了遗忘。

Llama 3 Herd 的 code expert 则在主预训练中途分叉，再训约 $1\mathrm{T}$，代码超过 $85\%$，末段做 repo 级长窗到 $16\mathrm{k}$，再按主模型流程做偏代码的 SFT / DPO。它用于产代码人工标注与 rejection sampling，并非取代 405B chat。Herd 将它与 Gururangan 的 Don't Stop Pretraining、Code Llama 放在同类路径中。

这与主 run 调整数学、多语言 mix 不同，后者仍在一个通用训练里；CPT 从已有权重另开领域浓度更高的训练，见 `meta-llama3-pretrain`。末期 upsample $40\mathrm{M}$ 高质量数据的退火，规模也与这里不同。

## 怎样减少遗忘

新 $D_{\mathrm{new}}$ 与旧 $D_{\mathrm{old}}$ 的梯度可能互相干扰，只看领域 PPL 下降，可能漏掉 MMLU、多语言与指令跟随退化。SFT 容易锁定回答格式，CPT 则会让 token 统计被新领域占据。

Ibrahim 等人 2024 比较英语到英语的弱偏移与英语到德语的强偏移，发现重新 warmup 后衰减学习率、混入旧数据的简单方法，就能接近从零训练所有数据。不能沿用已接近 $0$ 的余弦末端 LR 去适应几百 B 新 token，也不能没有 warmup 突然升到高峰 LR；新 schedule 的峰值通常低于从零预训练。

回放比例可以从 $10\%\sim 30\%$ 旧 mix 扫起，同时画领域与通用曲线，无需认定必须 $25\%$。公开实验中，中等回放有时比同 FLOPs 换大模型更划算，比例很高时又不如增加参数。Code Llama 约 $15\%$ 非代码也体现了避免 $100\%$ 领域纯度。

没有旧数据时，可以让当前模型合成旧域文本，或 distillation 旧 checkpoint logits，通常弱于真实回放，但比只用新域好。LoRA / adapter 可限制漂移，适合还想保留通用 chat 的产品；希望充分利用领域训练计算量时，仍可全参配回放。

验收每 $N$ token 跑保留集，同时看领域 HumanEval / 医学 QA、通用 MMLU 子集与 old-mix PPL、安全拒答及短上下文，见 `meta-llama-eval`。等结束才查，权重可能已漂远。换 vocabulary 需另行扩 embedding 并初始化新 id，见 `meta-llama3-tokenizer`，不能直接接着训。领域语料也要去除评测训练划分污染，Herd 退火中 8B 涨而大模型涨得少，提示这类假增益。

长窗与领域可以先后结合，如 Code Llama 先领域再长窗。前者改 $T$、RoPE，见 `meta-yarn-ntk`，后者改数据分布。

## 追问

**什么时候从零训领域模型？**
Code Llama 7B 对照显示从零更费 token。领域数据已到通用预训练量级、又不在乎通用能力时才考虑。

**SFT 能替代 CPT 吗？**
指令数据太少，难覆盖仓库级 API 等领域知识。CPT 学领域，SFT 学格式与拒答，Llama 3 专家也是先 CPT 再对齐。

**如何及时发现遗忘？**
按固定 token 间隔跑旧域保留集，别只追新领域损失。
