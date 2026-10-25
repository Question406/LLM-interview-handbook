---
id: msft-llava-train
section: microsoft
order: 17
level: S
title: Microsoft：LLaVA 两阶段训练，对齐再指令，视觉 token 数？
quick: "LLaVA 先冻结 ViT 和 LLM，只训练投影对齐图文，再冻结 ViT、训练投影和 LLM 做视觉指令微调。视觉 token 与文本共享上下文，224px 约 256 个、336px 约 576 个。数据、学习率和推理分辨率分别管理，并按 VQA、OCR、定位与幻觉验收。"
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

LLaVA 两阶段先对齐特征，再学习视觉指令：第一阶段只训练投影，第二阶段开放语言模型与投影，视觉塔继续冻结。比如训练用 256 个视觉 token，线上突然改成切块后的 2880 个，投影和位置统计可能漂移，需要适配与单独评测。

公开论文 Liu 等先用过滤 CC 图文对训投影，再用 GPT-4 合成多轮视觉指令做 SFT。LLaVA-1.5 换到 336px、MLP 投影，并加入学术 VQA / ShareGPT。产品未必叫 LLaVA，Phi-Vision / Copilot Vision 仍要处理相同预算问题。本卡并非逐字真题；token 预算见 `msft-llava`，冻塔对照见 `apple-mm-train`。

## 两阶段分别学什么

记视觉编码器 $f_v$、投影 $W$、语言模型 $\theta$。特征对齐阶段冻结 $f_v$ 与 $\theta$，只更新 $W$，用短 caption 让网格特征映射到词嵌入空间。1.0 使用线性层，1.5 使用两层 MLP，学习率相对高，数据相对少；此时解冻 LLM 容易损害语言能力。

视觉指令阶段继续冻结 $f_v$，训练 $W$ 和 $\theta$，学习率降一个数量级。数据包含看图回答与多轮对话，需要覆盖对话、OCR 和推理，只有「描述这张图」不够。原论文没有 RL 阶段，visual instruction tuning 也不等于从零训练 ViT。

视觉 token 数 $N_{\mathrm{vis}}$ 按 patch 网格计算：

$$
N_{\mathrm{vis}}=\frac{H}{P}\times\frac{W}{P}.
$$

224、$P=14$ 对应 256，336 对应 576。高分辨率切为 $g$ 块，再加全局图，约 $(g+1)\times 576$，这些 token 与文本共享上下文。AnyRes 的额外细节要付推理成本。

## 数据与分辨率共同验收

阶段 1 先清理 caption 噪声，避免把特征对齐拉偏；阶段 2 的合成指令要检查教师幻觉与基准泄漏，用新鲜评测验证，见 `msft-phi-data`。小数据同时解冻 ViT 容易破坏 CLIP 几何，只完成投影对齐也不足以成为 chatbot。

分别测 VQA、OCR / 表格、框或区域定位、幻觉拒答，记录推理分辨率，避免总 accuracy 掩盖读不准数字。Phi 小模型尤其要检查冻塔与语言回归，见 `msft-phi-vision`。Azure 视觉 token 计入 TPM，见 `msft-azure-tpm`；ONNX 分辨率档也应与训练一致，见 `msft-onnx-export`。

## 追问

**为什么第二阶段仍冻 ViT？**
CLIP 的图文对比预训练远大于指令数据，继续冻结有助于避免过拟合合成风格。

**什么时候考虑解冻？**
分辨率跨档，或 UI、医学等领域明显偏离自然图时，依据对照实验判断，MM1 参考见 `apple-mm-train`。

**Q-Former 解决什么？**
用可学习 query 压缩 token，节约预算但可能损失 OCR / 定位细节，LLaVA 的网格则保留更多空间信息。

**多图怎么接？**
串接各图视觉 token，固定块间分隔，并在训练中提供多图样本，避免上线时后图被忽略。
