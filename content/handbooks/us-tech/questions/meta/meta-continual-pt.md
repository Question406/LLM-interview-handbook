---
id: meta-continual-pt
section: meta
order: 18
level: A
title: Meta：continual pretrain / 领域自适应，灾难遗忘怎么防
quick: >-
  从 Llama 权接着训领域数据，比从零便宜，但分布一偏，通用能力会掉。公开配方是：回放旧 mix、重热再衰减学习率、领域不要 $100\%$
  纯度。Code Llama 和 Llama 3 的 code expert 都是这条；验收必须同时报领域和通用榜。
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

FAIR / Llama 岗把「再训 500B 代码」当工程题。Gururangan 的 Don't Stop Pretraining 把 DAPT 说清楚了；Code Llama 和 Llama 3 Herd 给了 Meta 公开实例。别把 CPT 说成 SFT：目标仍是 next-token，数据是无监督领域语料，学习率比 SFT 大、token 比 SFT 多几个数量级。

## Meta 公开的两条分叉

Code Llama：从 Llama 2 初始化。Llama 2 大约 $2\mathrm{T}$ token，其中代码只有约 $80\mathrm{B}$。再在**代码为主**的 mix 上训 $500\mathrm{B}$（70B 是 $1\mathrm{T}$），论文写大约 $85\%$ 代码。7B 对照从零训同一 mix：从零的终点 loss，大约只相当于 CPT 跑到一半。结论：**通用预训练是领域继续训的免费初始化**，不是浪费。后面还有 infill 目标、长窗微调到更大 $T$。图上能看到：代码变强时，Llama 2 的 helpfulness 奖励模型分数往下掉。这是遗忘的公开形状，不是传闻。

Llama 3 code expert：从**主预训练 run 中途分叉**，再继续约 $1\mathrm{T}$，其中代码大于 $85\%$。末段做 repo 级长窗微调到 $16\mathrm{k}$，再按主模型那套 SFT / DPO，但数据偏向代码。这个专家用来产代码人工标注和 rejection sampling，不是替代 405B chat。Herd 把这条明确写成 Gururangan / Code Llama 同类。

和 `meta-llama3-pretrain` 的差别：主模型在同一 run 里微调 mix（加数学、多语言），仍是「一个通用 mix」；CPT 是**另起一条权**，领域浓度高一个数量级。退火 $40\mathrm{M}$ 高质量 upsample 也不是 CPT，量级差太远。

## 遗忘从哪来，公开论文怎么挡

新数据分布 $D_{\mathrm{new}}$ 和旧 $D_{\mathrm{old}}$ 的梯度不是正交的。只看领域 PPL 会觉得在涨，MMLU、多语言、指令跟随已经在掉。SFT 遗忘更像「格式锁死」；CPT 遗忘更像 **token 统计被领域占满**。

Ibrahim 等人（2024）在「英语→英语弱偏移」和「英语→德语强偏移」上表明：不必上复杂正则，三件套就能接近从零重训所有数据：

1. **学习率重热再衰减。** 余弦已经收到尾巴时，直接拿微小 LR 去吞几百 B 新 token，适应不动；突然用高峰 LR 只打新数据，旧知识被冲掉。要像新的预训练 schedule 一样 warmup + decay，但峰值通常低于从零。
2. **回放。** 新 batch 里掺旧 mix。公开实验里，中等回放往往比把同样 FLOPs 换成更大模型更划算；回放到很高则不如把参数量做大。面试给工作点：先 $10\%\sim 30\%$ 旧数据扫，画领域榜和通用榜，不要背「必须 $25\%$」。
3. **别把领域纯度收到 $100\%$。** Code Llama 留了约 $15\%$ 非代码，就是回放的一种。

没有旧数据时：用当前模型合成旧域文本再回放，或蒸馏旧 checkpoint 的 logits。效果一般弱于真回放，但比纯新域好。LoRA / adapter 能限制漂移，适合「还要保持通用 chat」的产品 CPT；要吃满领域 FLOPs，还是全参 + 回放。

验收板：领域（HumanEval / 医学 QA）、通用（MMLU 子集、PPL on old mix）、安全拒答、短上下文。只报领域，评委会当成没做过遗忘。评测怎么组套餐见 `meta-llama-eval`。

## 一个具体错法

错法：主预训练余弦已经接近 $0$，接着 CPT 还用那个 LR。要么学不动，要么你手抖把 LR 拉高却没有 warmup，loss 尖刺、通用能力断崖。

错法二：换词表再 CPT。embedding 行对不上，见 `meta-llama3-tokenizer`。要扩矩阵并初始化新 id，这是另一个项目。

错法三：把评测集的训练劈开混进领域语料。8B 会涨、大模型涨得少，Herd 退火实验已经展示过这种假增益。

长窗 CPT 和领域 CPT 可以叠：Code Llama 就是先领域再长窗。长窗改的是 $T$ 和 RoPE（`meta-yarn-ntk`），领域 CPT 改的是数据分布，不要混成一个旋钮。

## 追问

- **从零训领域模型呢？** Code Llama 7B 对照说从零更亏 token。只有领域数据量已经是通用预训练量级、且你完全不在乎通用能力时才考虑。
- **和长窗 CPT 是一回事吗？** 都是继续预训练。长窗改 $T$ 和 RoPE，领域 CPT 改数据分布。可以叠。
- **多久算遗忘？** 每个 $N$ token 跑一次保留集。等作业结束再看，权已经漂了。
- **SFT 能不能代替 CPT？** 指令数据太少，装不进仓库级 API。领域知识用 CPT；格式和拒答用 SFT。Llama 3 是先专家 CPT，再专家对齐。
