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
updatedAt: 2026-08-19
sources:
  - title: OS-Atlas
    url: https://arxiv.org/abs/2410.23218
    type: primary
---

跨平台 grounding 最容易被刷的方式，是在同一批 App 截图上既训练又测试，再宣称「泛化到桌面和手机」。换皮、换文案、同一设计系统不算未见 UI。面试官要听样本合同、隔离 split、以及 grounding 与端到端分开报。OS-Atlas 一类工作强调的是多平台元素定位数据，而不是把端到端成功率直接叫泛化。不要编造跨平台分数；写清 split 规则即可。

## 样本绑什么

一条训练样本绑定：指令、screenshot 和 / 或 DOM / a11y 树、候选元素或 bbox、目标元素、动作类型、坐标或文本参数、执行后状态。坐标必须带截图版本、分辨率和 DPR，否则跨设备标签是错的——Android 逻辑像素、macOS 点、浏览器 CSS 像素不是一回事。混合真实与合成时，生成器不能复制评测模板，也不能留下稳定视觉捷径（永远红按钮、永远屏幕正中可点）。平台差异（状态栏、刘海、窗口装饰、触控 vs 点击）要作为显式特征或独立桶，而不是默默平均掉。缺执行后状态，模型只会点，不会知道点完对不对。

## Split 怎么才算未见

按未见 app、未见网站、未见布局家族、跨平台、跨任务语义切开。同一站点换 CSS、同一 Android 包换皮肤，只能当弱 OOD。训练 / 评测去重要做截图近重复和模板 ID，而不只是文件名。分别报告：point / bbox 命中或 IoU、action validity、full-task success。只报端到端，会让「记住流程」冒充「会定位」；只报 grounding，又会忽略执行与状态验证。跨平台数字必须按 OS 切片，平均掉 Windows 崩、Android 好没有意义。

## 证明不是背 benchmark

若只在熟悉页面上好，先查数据泄漏：评测截图近重复、任务模板重叠、合成器偷看测试布局。真正的泛化要在独立环境（未见 App 商店页、未见桌面软件、不同 OS 主题）重测。可被刷的点：测试集与训练集共享设计系统还称为 zero-shot；用端到端成功反推 grounding 已泛化；把同一 Electron 壳换皮当新平台。面试口径：泛化证据是隔离 split 上的 grounding 指标，外加独立环境抽检，而不是同一模板上的 e2e 涨点。报告必须写清：split 键（app / 站点 / 平台 / 模板 ID）、近重复去重阈值、坐标空间（CSS / 逻辑像素 / 截图像素）、grounding 与 e2e 分列。缺 split 说明的跨平台数字，默认当成同分布刷分。发布前做一次「截图近重复扫描」：训练与测试的感知哈希重叠要写进附录。重叠高就先洗数据，再谈架构。跨平台泛化不是平均分好看，而是未见 app 桶没有崩。

训练日志记录每条样本的 app、平台、模板 ID，评测按这些键做 leave-one-out。坐标空间在数据管道入口就统一到截图像素，禁止各平台各用各的原点。这比换 backbone 更能避免假泛化。

面试官要听隔离 split 和坐标空间，不听「我们覆盖了四个 OS」。同一设计系统换皮不是未见 UI。grounding 和 e2e 必须分列，否则流程记忆会冒充定位能力。

## 追问

- **为什么 grounding 和执行要拆开？** 点对了但没提交、或流程对但点错，改进对象完全不同。
- **合成数据最大风险？** 模板泄漏和捷径：模型学「点最亮的按钮」，到真实灰按钮就崩。
- **跨平台最常见的标签错？** 把 Android 逻辑像素当成截图像素，或忽略状态栏偏移。
- **同一套组件库换肤算 OOD 吗？** 只算弱 OOD；强泛化要未见 app 与未见布局家族，并按平台单独报表，不要把崩掉的 OS 平均掉后对外宣称已经具备跨平台泛化能力。
