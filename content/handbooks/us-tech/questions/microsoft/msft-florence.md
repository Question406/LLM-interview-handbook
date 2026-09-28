---
id: msft-florence
section: microsoft
order: 19
level: A
title: Microsoft：Florence / 视觉基础模型怎么接到生成（公开）？
quick: >-
  Florence-2 是提示式 seq2seq 视觉模型：任务写在文本提示里，输出也是文本（caption、框、多边形）。接到 LLM 时把它当结构化感知器，不要当成聊天
  VLM。OCR / 检测走 Florence，推理和引用走生成模型。FLD 公开是约 54 亿条标注、1.26 亿张图，不是聊天语料。
tags:
  - Microsoft
  - Florence
  - Vision
  - Grounding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Florence-2 — Advancing a Unified Representation for a Variety of Vision Tasks
    url: https://arxiv.org/abs/2311.06242
    type: primary
  - title: Florence-2 (Microsoft Research)
    url: https://www.microsoft.com/en-us/research/publication/florence-2-advancing-a-unified-representation-for-a-variety-of-vision-tasks/
    type: primary
  - title: Visual Instruction Tuning (LLaVA)
    url: https://arxiv.org/abs/2304.08485
    type: secondary
  - title: Azure AI Vision / Image Analysis
    url: https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/overview
    type: secondary
---

Azure / Copilot Vision 岗会问「视觉基础模型和多模态 LLM 怎么接」。公开锚点是 Florence-2：一张图加任务提示，encoder-decoder 吐出文本形式的 caption、框、短语接地、分割多边形。它不是 LLaVA 那种「图 token 拼进聊天 LLM」。Azure Vision 产品线也把统一视觉表征接到 OCR / 描述。接到生成时，Florence 是感知器，LLM 是推理器。不是逐字真题。

## 输出是文本，但是视觉合同

Florence 把检测和 OCR 收成语言：框写成相对坐标字符串，OCR 写成字加位置。好处是一套权重多任务；坏处是坐标是生成出来的，不是 NMS 后处理的硬框。接到 Copilot 时：

1. **感知。** 提示选任务：密集 caption、OCR、接地、区域建议。得到结构化 $E$（框、字、置信）。
2. **检索 / 权限。** 若证据来自租户文档，ACL 仍按 `msft-copilot-ground` 裁。Florence 不负责权限。
3. **生成。** LLM 只在 $E$ 上说话。要引用就指回框 id 或 OCR span。对不上就拒。

和 `msft-llava` 的差别：LLaVA 把网格 token 留在 LLM 上下文里，贵但端到端；Florence 先压成短文本，LLM 上下文便宜，空间细节取决于第一步有没有抽出来。UI 截图「点这个按钮」更适合 Florence 出框再让 agent 点；「这张照片在讲什么」可以 LLaVA / Phi-Vision，见 `msft-phi-vision`。

FLD 公开规模是约 54 亿条标注、1.26 亿张图，用迭代伪标。面试讲「视觉任务需要空间层次标注，不是再堆聊天」，不要编 Azure 内部配比。导出 ONNX 时分辨率档要固定，见 `msft-onnx-export`。

## 失败模式

- **坐标幻觉。** 模型写出看起来合法的框，点下去是空白。评测用 IoU / 中心是否落在可点区域，不要用 caption BLEU。
- **OCR 数字。** 金额、版本号单独计。生成模型会把错 OCR 说得很自信。
- **双重视觉。** 又跑 Florence 又把原图送进 VLM，延迟和 TPM 双计，见 `msft-azure-tpm`。需要细节时才把 ROI 切给 VLM。
- **把 Florence 当 chatbot。** 它不会工具循环，也不会遵守仓库 ACL。循环在 `msft-copilot-agent`。

延迟：检测 / OCR 应在百毫秒到一秒内给出可点框；语言推理另算。能用专用头就不要先跑一轮 7B 聊天。Azure 上 Image Analysis 和开源 Florence-2 权重不是同一 SLA，面试以当时文档为准。

我会先问产品要的是框、字，还是开放描述。再画感知 → 证据 $E$ → 生成。统一 seq2seq 省模型数，不省接地契约。检测 / OCR 用 Florence，开放描述用 VLM；评测把框 IoU 和 caption 流畅分开报。

## 追问

- **为什么不全部交给 Phi-Vision？** 小 VLM 能描述，框和密集 OCR 仍是 Florence 更稳。分工，不替代。
- **框用文本表示会不会不准？** 会。高风险点击要二次校验（IoU、低置信重跑检测器）。
- **和 LLaVA 训练的关系？** Florence 是视觉多任务预训练；LLaVA 是把网格对齐进 LLM。可以 Florence 出短 $E$ 再指令微调 LLM，见 `msft-llava-train`。
- **视频？** 公开 Florence-2 主图。视频要抽帧或另接时序模型，不要假装一张图模型能看完整段会议。
