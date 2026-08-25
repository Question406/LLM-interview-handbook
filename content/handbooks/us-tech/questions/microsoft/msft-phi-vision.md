---
id: msft-phi-vision
section: microsoft
order: 16
level: S
title: Microsoft：Phi vision / 小模型多模态，token 预算和适配器？
quick: >-
  Phi-3.5-Vision 约 4.2B，CLIP 网格加动态切块；Phi-4-Multimodal 用 Mixture-of-LoRAs 把视觉 / 语音接上冻住的语言模型。小模型上下文更紧，先算视觉
  token 再谈「能看清字」。别把 4B 当 13B LLaVA 用。
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

SLM / Copilot 端侧岗会问「Phi 怎么看图」。公开锚点：Phi-3.5-Vision 约 4.2B，CLIP ViT-L/14 加 phi-3.5-mini，动态切块吃高分辨率和多图；Phi-4-Multimodal 把视觉和语音用 LoRA + 模态路由接到冻住的语言模型，避免三种模态互相洗。数据质量叙事仍是教科书轴，见 `msft-phi-slm`、`msft-phi-data`。不是逐字真题。投影和 token 预算同构于 `msft-llava`，只是池子更小。

## 小模型上，$N_{\mathrm{vis}}$ 更贵

网格仍是

$$
N_{\mathrm{vis}}=\frac{H}{P}\times\frac{W}{P}.
$$

336px、$P=14$ 就是 576。动态切 $g$ 块再加全局缩略，粗算 $(g+1)\times 576$。Phi 上下文公开到 128k 量级，但 4B 的 KV 和 Azure TPM 先爆，见 `msft-long-context`、`msft-azure-tpm`。产品上：

- 自然图问答：单块 576 往往够。
- 截图小字、表格：必须切块或先 OCR，然后 **减文本、减多图**。
- 多图：三张 576 已经 1728，系统提示还没算。

Phi-4 的 Mixture-of-LoRAs：底模冻住，视觉一条 LoRA，语音一条。推理按模态组合加载，互不干扰。面试别说「我们把 ViT 和 LLM 全解开一起训」——那是 13B 数据配方，4B 上很容易毁语言。对齐阶段仍可只训投影 / LoRA，指令阶段再松 LLM，细节见 `msft-llava-train`。

错法：训练 224、线上 AnyRes 切满还不做适配；把 Phi 当 OCR 引擎却不评字段级准确；语音和视觉抢同一套 LoRA。公开报告强调模态扩展要隔离。

## 评测和产品位

Phi 的主张是高质量数据让小模型打过更大脏模型。视觉同样：合成指令会泄漏 TextVQA 风格。评测要新鲜截图、内部 UI、表格数字，不要只报公开 VQA。幻觉「图里有猫」和文本接地同类：对不上区域就拒，见 `msft-copilot-ground`。

产品位：手机 / 边缘 / Copilot 里的「看一眼」用 Phi；仓库级文档理解用更大 VLM 或 Florence 出结构再生成，见 `msft-florence`。ONNX 导出要静态分辨率档，见 `msft-onnx-export`。视觉 token 进 TPM，和文本同一本账。

我会先问窗口、是否端侧、要看清的最小字号。再写 $N_{\mathrm{vis}}$ 预算。主动说：小模型不是「免费多模态」，是更狠的 token 税。Azure 账单按视觉 token 计，和文本同一本 TPM。

Azure 账单按视觉 token 计，和文本同一本 TPM。先写预算再谈「能看清字」。

面试收尾主动报失败模式和评测切片，不要停在架构名词。

## 追问

- **为什么不 Q-Former 压成 32 个？** 能压，损空间细节。Phi 走 LLaVA 网格是为了简单和 OCR。预算用切块数管，不用再加一层抽象器当创新。
- **语音和视觉能否同轮？** Phi-4-Multimodal 公开支持组合。仍要算两条前缀的和。会议录音加白板照片，先抽 ASR 再少留图 token。
- **和 LLaVA-1.5 13B 比？** 架构像，容量不同。13B 能硬吃 2880 视觉 token 的任务，4B 要先裁。
- **污染？** 视觉指令若从评测图改写而来，榜会虚。切片见 `msft-phi-data`。
