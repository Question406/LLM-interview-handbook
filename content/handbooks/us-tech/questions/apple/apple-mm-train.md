---
id: apple-mm-train
section: apple
order: 16
level: S
title: Apple：端侧 / 云侧多模态训练，视觉塔冻结还是联合，分辨率怎么选？
quick: "我会先定任务需要的分辨率和视觉 token 数，再决定是否解冻视觉塔。MM1 的公开消融中，低分辨率时冻结更好，高分辨率或偏离预训练分辨率时解冻更好；端侧还要按 ANE 静态档位训练和导出，云侧切块方案不能直接搬过去。"
tags:
  - Apple
  - Multimodal
  - Training
  - Vision Encoder
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: MM1 — Methods, Analysis and Insights from Multimodal LLM Pre-training
    url: https://machinelearning.apple.com/research/mm1-methods-analysis-insights
    type: primary
  - title: MM1 (arXiv)
    url: https://arxiv.org/abs/2403.09611
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Visual Instruction Tuning (LLaVA)
    url: https://arxiv.org/abs/2304.08485
    type: secondary
---

我会先定分辨率和视觉 token 数，再决定冻结还是联合训练视觉塔。MM1 的公开消融说明，分辨率和 token 数对效果的影响更大，连接器在 SFT 后差距很小；低分辨率冻结更好，高分辨率则更需要适配编码器。

比如训练只见过基础分辨率，线上却要读 1344px 的图，视觉塔就要适应插值和切块；端侧固定档位则要兼顾 ANE 和约 3B 的解码预算。LLaVA 两阶段训练可以拿来对照，但不能当作 Apple 内部配方。端云模型分工见 `apple-foundation-models`。

## 先定分辨率，再决定冻哪一段

记图像边长 $R$、patch $P$，网格

$$
N_{\mathrm{vis}}=\frac{R}{P}\times\frac{R}{P}.
$$

MM1 把 $R\in\{224,336\}$、$N_{\mathrm{vis}}\in\{64,144\}$ 做消融：涨分辨率或涨 token，zero-shot / few-shot 都升；平均池化、注意力池化、卷积 abstractor 在 SFT 后几乎打平。因此改连接器前，先检查分辨率和视觉 token 预算是否足够。

冻还是解冻，跟 $R$ 和预训练分辨率是否一致绑在一起：

- 低 $R$、和视觉塔预训练一致。冻编码器。MM1 补充材料：低分辨率冻塔比解冻大约高 2.2 分。LLaVA 更狠：两阶段都冻 ViT，只动投影和（第二阶段）LLM，见 `msft-llava-train`。小数据上解冻会把 CLIP / DFN 的几何先验洗掉。
- 高 $R$、或推理要切块 / 插值。联合训编码器。MM1：1344px 解冻大约高 2.9 分，因为预训练停在基础分辨率，没有插值和切块。端侧若永远 336，就不要为了「联合听起来更端到端」去解冻。
- 连接器。只在对齐阶段是唯一可训模块时才关键。预训练已经把图文空间拉近之后，它不是瓶颈。

端侧和云侧不要共用一套解冻策略。手机要静态 shape、功耗、3B 级解码，见 `apple-ane`、`apple-vision-edge`。云侧 server 模型可以上高 $R$、多图、解冻塔。把云侧 AnyRes 图直接蒸馏到端侧，位置统计会漂。

## 数据配比和产品边界

MM1 的公开结论：caption、图文交错、纯文本要混。缺交错，多图推理和 in-context 图例会下降；缺纯文本，语言能力回退。面试讲「三类数据都要、比例以论文表为准」，不要编一套 Apple Intelligence 私有配比。

Foundation model 公开原则是不用用户私有数据训基础模型。相册、屏幕、消息不能当 SFT。个性化走本地检索和 adapter，见 `apple-personalize`、`apple-diff-privacy`。评测把 OCR / UI 定位和自然图 VQA 切开，见 `apple-multimodal`、`apple-afm-eval`。

训练 224、线上 1344 时要做分辨率适配；解冻范围也要按任务和数据量验证。视觉 token 和文本共享 KV 预算，提高图像分辨率时要确认文本空间是否仍够，见 `apple-ondevice-kv`。



先问产品要看清的最小字号和是否离线。再写 $R$、$N_{\mathrm{vis}}$、冻哪些参数三列表。端侧默认冻塔、固定档位、少 token；PCC 才谈联合和高分辨率。主动说失败：解冻后 ANE 图和训练图算子不一致；高 $R$ 把通知摘要的文本预算吃光。

## 追问

**为什么不从头训视觉塔？**
对比预训练已经学到了几何和 OCR 先验。数据不够时解冻是在用 LLM 梯度毁编码器。
**连接器都差不多，还要不要 MLP？**
要，但别当主创新。LLaVA-1.5 两层 MLP 是便宜的对齐容量，MM1 说它改变不了分辨率不够的事实。
**端侧能不能动态分辨率？**
训练可以多档，导出必须是静态桶，见 `apple-ane`。桶之间用 pad，不要运行时 `interpolate`。
**和纯 caption 预训练的差别？**
caption 对不齐「指这块」。屏幕理解和区域定位任务需要区域标注，见 `apple-multimodal`。
