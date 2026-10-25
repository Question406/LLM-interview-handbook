---
id: msft-florence
section: microsoft
order: 19
level: A
title: Microsoft：Florence / 视觉基础模型怎么接到生成（公开）？
quick: "Florence-2 用任务提示生成 caption、OCR、框和多边形，可作为 LLM 前面的结构化感知器。先抽取视觉证据，再让生成模型推理并引用框或 OCR span；坐标与数字单独验证。它的 FLD 是约 54 亿条视觉标注、1.26 亿张图，不能当成聊天语料理解。"
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

Florence-2 适合先把图像变成框、文字和描述，再让 LLM 基于这些证据推理。比如 UI 截图要点按钮，可以先用 Florence 定位框，再交给 agent 执行；开放式照片描述则可考虑 LLaVA / Phi-Vision，见 `msft-phi-vision`。

公开模型是图像加任务提示的 encoder-decoder，用文本输出 caption、短语定位、相对坐标框和分割多边形。Azure Vision 也将统一视觉表征用于 OCR / 描述。本卡是公开方案讨论，未声称逐字真题。

## 先把感知结果变成可引用证据

任务提示选择密集 caption、OCR、定位或区域建议，产出结构化 $E$，如框、字和置信信息。框是生成出的坐标字符串，OCR 带文字与位置；同一权重支持多任务，但生成坐标仍需验证，不能当成 NMS 后处理的硬框。

来自租户文档的视觉证据先按 `msft-copilot-ground` 做 ACL，Florence 本身不处理权限。生成模型只基于 $E$ 回答，引用指向框 id 或 OCR span；没有对应支持时拒答。

LLaVA 将网格 token 保留在 LLM 上下文，更偏端到端，成本也更高；Florence 压为短文本，节省语言上下文，但第一步没提取的空间细节后续就无法直接推断，见 `msft-llava`。

FLD 的公开规模约 54 亿条标注、1.26 亿张图，使用迭代伪标，强调视觉任务与空间层次的监督。不要据此编造 Azure 内部配比。导出 ONNX 时固定分辨率档，见 `msft-onnx-export`。

## 按视觉任务验收

坐标输出合法仍可能落在空白处。框用 IoU（交并比）或中心是否处于可点区域评估，金额、版本号等 OCR 数字单独统计，caption BLEU 不能说明这些操作正确。高风险点击要二次校验，低置信时重跑检测器。

Florence 跑完再把原图全送 VLM，会重复消耗延迟与 TPM；需要细节时再裁 ROI，见 `msft-azure-tpm`。它也不会自己处理工具循环或仓库 ACL，agent 部分见 `msft-copilot-agent`。

检测 / OCR 可把百毫秒到一秒作为预算示例，语言推理另算，专用任务无须先过一轮 7B 聊天。Azure Image Analysis 与开源 Florence-2 权重也不是同一 SLA，部署时按相应文档核验。产品先明确要框、文字还是开放描述，再决定感知、证据和生成的分工。

## 追问

**为什么不全用 Phi-Vision？**
开放描述与密集 OCR、框定位的需求不同。可以比较小 VLM 与 Florence 的本域结果，再按任务分工。

**与 LLaVA 训练怎么结合？**
Florence 做视觉多任务预训练，LLaVA 对齐网格与 LLM；也可先输出短 $E$，再指令微调 LLM，见 `msft-llava-train`。

**Florence-2 能直接处理完整视频吗？**
公开 Florence-2 主要面向图像，视频需抽帧或接时序模型。
