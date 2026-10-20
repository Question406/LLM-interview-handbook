---
id: meta-mm-safety
section: meta
order: 32
level: A
title: Meta：视觉+文本安全——Llama Guard 多模态和截图越狱
quick: >-
  Guard 3 Vision 挂在 Llama 3.2 11B 上，判的是「图+文 prompt」或「图+文 prompt 加文本回复」，不是纯图像分类，也不是纯文本
  Guard。截图把违禁步骤写成图上的字，文本通道是无害的「请补全列表」。只拦文本会漏。公开论文测过对抗，别保证越狱为零。
tags:
  - Meta
  - Llama Guard
  - Multimodal
  - Safety
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Llama Guard 3 Vision — Safeguarding Human-AI Image Understanding Conversations
    url: https://arxiv.org/abs/2411.10414
    type: primary
  - title: Llama Guard 3 11B-Vision model card
    url: https://github.com/meta-llama/PurpleLlama/blob/main/Llama-Guard3/11B-vision/MODEL_CARD.md
    type: primary
  - title: Llama 3.2 — vision and edge models
    url: https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/
    type: primary
  - title: FigStep — Jailbreaking Large Vision-Language Models via Typographic Visual Prompts
    url: https://arxiv.org/abs/2311.05608
    type: secondary
---

3.2 一出视觉，安全就不能只跑 8B 文本 Guard。Connect 博客和 PurpleLlama 卡片把 **Llama Guard 3 11B Vision** 写成配套闸门。文本 Guard 的分类头、taxonomy、和基座分工见 `meta-llama-guard`；本题只收 **多模态面**：它看什么、不看什么、截图 / 排版字怎么漏。不要给可复制的越狱配方，讲威胁类型和防线即可。

## Guard 3 Vision 在判什么

它是 3.2-Vision 上微调的分类 LM，不是另接 $[D,2]$ 头。输入：策略文本 + **一张图** + 用户文字（输入提示（prompt） 分类），或再加模型回复（response 分类）。输出仍先 `safe` / `unsafe`，再跟类别。分数读首个 token 的概率。卡片写得很死：

- **不是** 图像安全分类器（单图无字不保证）；
- **不是** 文本安全分类器（纯文本请用 Guard 3 8B / 1B）；
- 优化英语、**每条请求一张图**；多轮要把 image 占位符放在那一张出现的那一轮；
- 图像按 3.2 同样切成约 $4$ 块 $560\times 560$，见 `meta-anyres`。分辨率和长宽比一变，分类会漂。

训练是混合人标和合成：人写的图文对、用越狱手法从内部 Llama 引出违规回复、再用 405B 或人打标。taxonomy 对齐 MLCommons，并强调 **认人 / 从照片反查真实身份** 这类视觉特有风险。Herd 对文本 Guard 的警告同样适用：系统安全上升，误拒也可能上升。报 FPR，不要只报「更安全」。

延迟：11B 视觉模型在处理输入的 prefill 阶段包含编码器计算和切块，比 8B 文本 Guard 贵一截。只对带图请求开 Vision Guard；纯文本走 8B/1B。模板必须和训练一致，多一个角色头，首 token 分布就偏。

## 截图越狱为什么发生

文本对齐把「如何制造 X」写在字面上会拒。FigStep 一类公开攻击把同一内容 **排版进图**：编号列表、步骤标题渲染成像素，旁边的文本只说「图里有一份空列表，请补全每一项」。文本通道无害，有害语义走视觉 embedding。论文把原因写成：视觉嵌入上的安全对齐远弱于文本。切片再拼（FigStep-Pro）是为了绕过「整张图 OCR 就能当文本拦」的简单补丁。面试提到「排版字 + 无害指令」这一类即可，不要逐步教怎么绕。

另一类是 **真视觉危害**：暴力、性、真实人脸，字面上没有违禁句。只 OCR 再送文本 Guard 会漏。反过来，密密麻麻的小字截图，ViT 切块可能读不清，Guard 3 Vision 自己也说分类随图像尺寸变。所以防御需要结合多种检查，不能只用一个模型。

我会画三层：

1. **输入。** 带图请求走 Vision Guard；纯文本走文本 Guard。OCR 可作辅助信号，不能当唯一闸门。
2. **主模型。** 3.2 后训练里有安全数据，见 `meta-llama-vision`，行为对齐不是分类器。
3. **输出。** 回复再跑 response 分类；工具 / 检索片段要一并送进，否则「引用了有害段落」会漏。

常见误区是：用文本 Guard 扫用户句子、图直接进 3.2。错法二：把 Vision Guard 当 NSFW 图像模型去扫 Feed。错法三：保证对抗鲁棒：论文明确测过越狱，只说是起点。生成式图像本身不在 3.2 输出里（它不出像素）；Chameleon 那种能出图的早融合要另加图像安全，见 `meta-early-fusion`。

## 追问

- **为什么不 OCR 完当文本拦？** OCR 漏艺术字、手写、低分辨率；真视觉危害没有字。OCR 可作特征，不能替换多模态分类。
- **和 Prompt Guard 是一个吗？** 不是。Prompt Guard 拦注入，Code Shield 拦代码；Vision Guard 是图文对话危害分类。
- **多图、多语言？** 公开不保证。多图不要默认同一套阈值；非英要自己测。
- **误拒怎么收？** 调阈值、补硬负例（ innocuous 截图、梗图）、产品政策微调。和文本一样，FPR 是产品数字。
- **要不要复述越狱步骤？** 不要。面试停在威胁类型：排版字、无害指令、切片绕 OCR。防御讲 Guard 覆盖视觉通道 + 不单靠 OCR。

部署上把 Vision Guard 和主模型当成两个 checkpoint、两套模板、两次 prefill。图尺寸、切块数、聊天头必须和 3.2 / Guard 训练时一致，否则首 token 的 `safe`/`unsafe` 分布会偏，阈值全部失效。和文本 Guard 一样，策略写在 输入提示里可以换 taxonomy，但换了要在自己的政策集上重画 PR，不能只声称它能零样本适应。
