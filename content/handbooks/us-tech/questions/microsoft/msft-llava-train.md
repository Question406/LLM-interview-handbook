---
id: msft-llava-train
section: microsoft
order: 17
level: S
title: Microsoft：LLaVA 两阶段训练，对齐再指令，视觉 token 数？
quick: "第一阶段冻 ViT 和 LLM，只训投影，图文 caption 对齐。第二阶段仍冻 ViT，打开 LLM 和投影，视觉指令微调。视觉 token 数由分辨率决定：224 约 256，336 约 576。别说成从头训视觉塔。"
tags:
  - Microsoft
  - LLaVA
  - Training
  - Multimodal
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Visual Instruction Tuning (LLaVA)
    url: https://arxiv.org/abs/2304.08485
    type: primary
  - title: Improved Baselines with Visual Instruction Tuning (LLaVA-1.5)
    url: https://arxiv.org/abs/2310.03744
    type: primary
  - title: Phi-3 Technical Report
    url: https://arxiv.org/abs/2404.14219
    type: secondary
---

微软多模态岗把 LLaVA 当白板题。不是背 class 名，是两阶段冻谁、视觉 token 怎么进序列。论文：Liu 等人先用过滤后的 CC 图文对训投影，再用 GPT-4 生成的多轮视觉指令做 监督微调（SFT）。LLaVA-1.5 换成 336px、MLP 投影、加学术 VQA / ShareGPT。产品不一定叫 LLaVA，Phi-Vision / Copilot Vision 仍是这条。Token 预算见 `msft-llava`；冻塔对照见 `apple-mm-train`。不是逐字真题。

## 两阶段，冻的是不同的东西

记视觉编码器 $f_v$、投影 $W$、语言模型 $\theta$。

**阶段 1（特征对齐）。** 冻 $f_v$ 和 $\theta$，只训 $W$。数据是短 caption。目标是让网格特征落到词嵌入空间。LLaVA-1.0 用线性层；1.5 用两层 MLP。学习率相对高、数据相对少。解冻 LLM 会在这点把语言能力洗掉。

**阶段 2（视觉指令）。** 仍冻 $f_v$，打开 $W$ 和 $\theta$。数据是「看图回答 / 多轮」。学习率降一个数量级。这才是「visual instruction tuning」这个词的意思，不是从零训 ViT。

视觉 token 数：

$$
N_{\mathrm{vis}}=\frac{H}{P}\times\frac{W}{P}.
$$

224 / $P=14$ → 256；336 → 576。它们和文本抢同一条上下文。高分辨率靠切块，$g$ 块加全局约 $(g+1)\times 576$。训练用 256、推理切到 2880，位置和投影统计都会漂。

常见误区是：两阶段都解冻 ViT（小数据毁 CLIP 几何）；只做阶段 1 就当 chatbot；把「instruction tuning」说成 基于人类反馈的强化学习（RLHF）。LLaVA 原论文没有 强化学习（RL） 阶段。

## 数据和评测

阶段 1 要干净图文对，噪声 caption 会把对齐拉歪。阶段 2 要多样任务：对话、OCR、推理，不能只有「描述这张图」。合成指令会带教师幻觉和基准泄漏，评测要新鲜题，见 `msft-phi-data`。

评测切开：通用 VQA、OCR / 表格、定位（框或区域）、幻觉拒答。单一 accuracy 会掩盖「会聊天但读不准数字」。推理分辨率必须进评测配置，见 `msft-llava`。

Phi 小模型上更要守冻塔，见 `msft-phi-vision`。Azure 上视觉 token 进 TPM，见 `msft-azure-tpm`。导出 ONNX 时分辨率档要和训练一致，见 `msft-onnx-export`。

我会先在白板上写冻/解冻表，再写 $N_{\mathrm{vis}}$，再问产品要看清什么。AnyRes 增加推理开销，不是免费质量。两阶段用不同学习率和数据；混成一轮「全解开训到底」是常见错法，小模型上尤其容易毁语言。评测切开 VQA / OCR / 定位 / 幻觉拒答，推理分辨率要进配置。

## 追问

- **为什么阶段 2 还冻 ViT？** CLIP 已经在图文对比上训过。指令数据量远小于对比预训练，解冻容易过拟合到合成风格。
- **什么时候解冻编码器？** 分辨率和预训练差一档、或领域图（UI、医学）和自然图差很远。MM1 高分辨率消融是对照，见 `apple-mm-train`。
- **Q-Former 呢？** 另一条对齐：可学习 query 压成少 token。LLaVA 用网格换细节。选哪条先看 OCR / 定位要不要。
- **多图怎么训？** 把多张图的视觉 token 串起来，块间分隔要固定。训练必须出现多图样本，否则推理时后图会被忽略。
