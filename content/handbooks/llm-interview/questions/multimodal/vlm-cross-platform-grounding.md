---
id: vlm-cross-platform-grounding
section: multimodal
order: 1
level: S
title: 如何训练跨 Web、Windows、macOS、Android 的 GUI grounding / action model，并证明它对未见 UI 的泛化而非记住 benchmark？
quick: 数据应把指令、视觉/结构化观察、目标元素和动作绑定，并按应用、站点、平台和任务模板做严格隔离 split。分别报告 grounding 与端到端执行，不能用同一套 UI 模板训练和测试后宣称泛化。
tags:
  - GUI Grounding
  - VLM
  - Generalization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: OS-Atlas
    url: https://arxiv.org/abs/2410.23218
    type: primary
---

基本训练样本需要 instruction、screenshot/DOM/可访问性树、候选元素或 bbox、目标元素、动作类型、坐标/文本和执行后状态。混合真实与合成数据时，合成生成器不能泄露评测模板或稳定的视觉捷径。

split 要按未见 app、未见网站、未见布局、跨平台和跨任务语义分开；同一网站换皮或相同模板不同文案不算强泛化。grounding accuracy、point/bbox IoU、action validity 与 full-task success 也应分开报告。

若视觉模型只在 benchmark 熟悉页面上好，先检查训练数据去重、截图近重复和任务模板泄露，再讨论模型架构。真正的泛化需要在独立环境重新验证。
