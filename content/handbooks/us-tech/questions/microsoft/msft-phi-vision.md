---
id: msft-phi-vision
section: microsoft
order: 16
level: S
title: Microsoft：Phi vision / 小模型多模态，token 预算和适配器？
quick: "Phi-3.5-Vision 约 4.2B，用 CLIP 网格与动态切块；Phi-4-Multimodal 用模态 LoRA 连接冻结语言底座。先算图像、语音和文本的总预算，再按小字、表格与定位需求裁图或 OCR，适配训练推理分辨率，并用新鲜视觉任务验收。"
tags:
  - Microsoft
  - Phi
  - Vision
  - SLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Phi-3 Technical Report
    url: https://arxiv.org/abs/2404.14219
    type: primary
  - title: Phi-4-Mini Technical Report — Compact Multimodal Models via Mixture-of-LoRAs
    url: https://arxiv.org/abs/2503.01743
    type: primary
  - title: Visual Instruction Tuning (LLaVA)
    url: https://arxiv.org/abs/2304.08485
    type: secondary
  - title: Phi cookbook vision inference
    url: https://github.com/microsoft/PhiCookBook/blob/main/md/01.Introduction/03/Vision_Inference.md
    type: secondary
---

Phi 多模态先要控制视觉 token，再选择投影或 LoRA 的适配方式。小参数并不让多图输入变便宜。例如三张图每张 576 个 token，已占 1728，系统提示、检索与输出还没计入。

公开 Phi-3.5-Vision 约 4.2B，用 CLIP ViT-L/14 与 phi-3.5-mini，动态切块支持高分辨率和多图；Phi-4-Multimodal 用 LoRA 与模态路由连接冻结语言模型，减少视觉、语音互相干扰。本卡来自公开方案；数据路线见 `msft-phi-slm`、`msft-phi-data`。

## 预算与适配一起设计

视觉 token 数 $N_{\mathrm{vis}}$ 与 `msft-llava` 的网格计算相同：

$$
N_{\mathrm{vis}}=\frac{H}{P}\times\frac{W}{P}.
$$

336px、$P=14$ 对应 576，切 $g$ 块加全局图约 $(g+1)\times 576$。公开窗口虽到 128k 量级，4B 的 KV 和 Azure TPM 仍要负担全部前缀，见 `msft-long-context`、`msft-azure-tpm`。

自然图问答可先测单块 576，小截图文字与表格需要切块或 OCR，再减少文本与多图。13B LLaVA-1.5 能处理的 2880 视觉 token 任务，4B 产品也应先考虑裁图。训练 224、线上 AnyRes 切满会改变位置与投影统计，必须适配。

Phi-4 的 Mixture-of-LoRAs 冻结基础语言模型，视觉和语音分别用 LoRA，按模态组合加载以隔离干扰。一般多模态对齐也可先只训投影 / LoRA，再在指令阶段调整 LLM，具体看 `msft-llava-train` 的配方，不能默认照搬 13B 全量解冻。

## 视觉任务单独验收

小模型如果承担 OCR，就测金额、日期等字段准确率。合成视觉指令可能泄漏 TextVQA 风格，使用新鲜截图、内部 UI 和表格数字，别只报公开 VQA。描述对不上区域时按 grounding 失败处理，见 `msft-copilot-ground`。

手机、边缘与 Copilot 的轻量视觉任务可考虑 Phi；仓库级文档理解可用更大 VLM，或 Florence 先出结构再生成，见 `msft-florence`。ONNX 导出固定分辨率档，见 `msft-onnx-export`。产品先定窗口、端侧要求和最小字号，再决定切块数与 OCR 路径。

## 追问

**为什么不压成 32 个 Q-Former token？**
能省预算，也会损失空间细节。网格路线可保留 OCR / 定位信息，切块数仍需控制。

**语音和视觉能同轮输入吗？**
Phi-4-Multimodal 公开支持组合，仍要算两种前缀总量。会议录音加白板可以先 ASR，再减少图 token。

**视觉污染怎么查？**
评测图的改写指令也会泄漏，使用 `msft-phi-data` 的公开、去污与新鲜私有切片分别验证。
