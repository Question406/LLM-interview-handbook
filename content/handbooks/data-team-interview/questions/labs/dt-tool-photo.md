---
id: dt-tool-photo
section: labs
order: 43
level: A
title: OpenAI：用户上传工具照片做识别，训练数据从哪来？
quick: "训练图可以来自许可产品目录、厂商授权图、受控拍摄和验证过的合成数据。评测用按时间留出的新 SKU 和内部拍摄图。用户上传用于识别的图片，不能默认作为基座训练数据或固定评测数据。"
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

识别头的训练图片可以来自许可目录、厂商图、受控拍摄和验证过的合成数据。用户在对话中上传扳手照片，只说明产品需要识别它，不能默认拿原图训练 AFM。端侧数据可以留给 on-device adapter，回传训练基座需要单独明确使用通道。

不这么选的理由：AceOffer 记过 OpenAI ML 轮：产品让用户上传真实工具照片、问模型这是什么，你怎么改进训练。标准答会说拿用户图做难例回灌。苹果这轮通道先明确固定下来。

接到苹果：难例仍然要挖，来源换成评测失败和许可长尾 SKU。光照、遮挡、手持模糊用受控拍摄和合成补。对稀有工具类别设置配额，避免训练数据几乎都被锤子这类常见工具占据。门禁用时间切新 SKU 和内部拍摄，不用用户上传集。CLIP 过滤阈值对合成 caption 要单独校准，见 `dt-clip-filter-code`。多模态例子讲到底见 `dt-multimodal-data`。

公开锚点：AceOffer OpenAI ML 目录「Improve Tool / Image Recognition Model Training」，报到 6 次，最近一次 2025 年 12 月。

## 追问

- **用户 opt-in 帮助改进呢？** 单独通道，默认关，见 `dt-privacy-feedback`。即便开了，也先聚合失败类型再合成复现，不把原图写进预训练 shard。
- **没有厂商授权的老工具怎么认？** 许可博物馆 / 手册图，或产品侧检索，不要为了认一个锤子去爬论坛相册。
- **识别错了怎么回灌？** 记的是失败类型（反光金属、半遮挡），用许可图复现，不要存用户那一张。
