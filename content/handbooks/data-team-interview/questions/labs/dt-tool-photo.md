---
id: dt-tool-photo
section: labs
order: 43
level: A
title: OpenAI：用户上传工具照片做识别，训练数据从哪来？
quick: "来自许可产品目录、厂商授权图、受控拍摄和验证过的合成数据。用户上传的识别图片只说明产品需要认它，没有明确的训练许可，就不能用作基座训练或固定评测。难例从评测失败和许可长尾 SKU 里挖，评测用按时间留出的新 SKU 和内部拍摄图。"
companies:
  - apple
tags:
  - OpenAI
  - Multimodal
  - Privacy
  - Apple
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: OpenAI Machine Learning Interview Questions (AceOffer catalog)
    url: https://aceoffer.app/interviews/openai/machine-learning-questions
    type: secondary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

训练图片来自许可产品目录、厂商授权图、受控拍摄和验证过的合成数据。用户在对话里上传一张扳手照片，只说明产品需要认得出扳手；没有明确的训练许可，原图不进训练。

这题出自 AceOffer 记录的 OpenAI ML 轮：产品让用户上传真实工具照片、问模型这是什么，问你怎么改进训练。目录里的标题是「Improve Tool / Image Recognition Model Training」，报到 6 次，最近一次在 2025 年 12 月。常见的标准答案是拿用户图当难例回灌，卡在数据通道上：用户上传是为了得到识别结果，拿去训练基座需要单独、明确的使用许可。难例照样能挖，换一个有许可的来源就行。

难例从评测失败和许可的长尾 SKU 里挖。光照、遮挡、手持模糊这些条件，用受控拍摄和合成来补。稀有工具类别要设配额，免得训练数据几乎全是锤子这类常见工具。用 CLIP 过滤的话，阈值对合成 caption 要单独校准，见 `dt-clip-filter-code`。

## 追问

**评测集怎么建？**
用按时间切出的新 SKU 和内部拍摄图做门禁，不用用户上传集。

**用户 opt-in「帮助改进」呢？**
那是单独的通道，按用户同意的范围使用，见 `dt-privacy-feedback`。即便开了，也先聚合失败类型再合成复现，不把原图写进预训练 shard。

**识别错了怎么回灌？**
记录失败类型，比如反光金属、半遮挡，再用许可图复现，不存用户的那一张。

**没有厂商授权的老工具怎么认？**
用许可的博物馆或手册图，或者在产品侧做检索。不要为了认一个锤子去爬论坛相册。

相关：多模态数据的完整讨论见 `dt-multimodal-data`。
