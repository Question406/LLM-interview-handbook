---
id: sensetime-lora-where
section: arch
order: 191
level: A
title: 商汤应用实习：LoRA 原理、超参加在 Transformer 哪些模块？
quick: >-
  $W'=W+\frac{\alpha}{r}BA$，通常插 Attention 与 MLP 的 Linear，不插
  LayerNorm。$r$ / $\alpha$ 控制容量和步长；QLoRA 是量化基座再挂适配器。多模态还要说明视觉塔与语言模型各挂哪里。
tags:
  - SenseTime
  - LoRA
  - QLoRA
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 商汤大模型算法应用实习面经（已offer）
    url: https://www.nowcoder.com/feed/main/detail/2762070c2c52472da06bf9ee59518d79
    type: candidate-first-hand
  - title: 商汤大模型算法实习二面（已oc）
    url: https://www.nowcoder.com/feed/main/detail/363fb9aab5dc4507a5bfca6efb049fbf
    type: candidate-first-hand
---

## 真题记录

- 公司：商汤
- 岗位：大模型算法应用实习一面；另一帖二面问 LoRA / QLoRA
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“LoRA 原理、常见超参、一般加在 Transformer 哪些模块”**；**“LoRA和 QLoRA？”**

这块容易把 LoRA 讲成「再训一层小网络」，或把 QLoRA 说成新算法。LoRA 是冻结 $W$ 后在 Linear 上加低秩残差；QLoRA 只是把基座权重量到 4bit 再挂同一套适配器。商汤这岗还会追多模态挂哪，不要只背语言侧 q/v。初始化细节见 `tencent-lora-ab-init`，本题先把挂载点与超参讲清。

## 原理与超参：$r$ 是容量，$\alpha/r$ 是步长

$$
W'=W+\frac{\alpha}{r}BA,\qquad B\in\mathbb{R}^{d\times r},\; A\in\mathbb{R}^{r\times k}.
$$

可训练量从 $dk$ 降到 $r(d+k)$。$r$ 太小欠拟合；$r$ 过大接近全参扰动，小 OCR / 指令集上容易过拟合，见 `arch-lora`。$\alpha$ 与学习率耦合：有效更新尺度约 $\alpha/r$，改 $r$ 时若不同时改 $\alpha$，步长会漂。常见默认 $\alpha=2r$ 或固定 $\alpha=16$，必须说清你用的约定。Dropout 打在 $BA$ 上，不是打在冻结的 $W$ 上。推理可把 $\frac{\alpha}{r}BA$ merge 回 $W$，多适配器则要路由，不能无脑加。

## 挂哪：Linear 可以，LayerNorm 不要当残差插槽

语言侧优先 Attention 的 $W_q,W_k,W_v,W_o$ 与 MLP 的 gate/up/down，见 `meituan-lora-not-after-ln`。不要插在 LayerNorm / RMSNorm 之后当随意加性扰动：Norm 已经校准激活尺度，再挂未约束可训练变换容易初期尖刺。Embedding / lm_head 看任务：词表域变化大（新语言、特殊 token）才考虑。

多模态（商汤应用岗高频）：视觉塔默认冻结，只训投影（MLP / Q-Former / linear projector）和语言侧 LoRA；OCR / 定位重的任务再松视觉塔最后几层或给 ViT Linear 挂低秩。不要语言、视觉两侧无差别全开 $r=64$。QLoRA：NF4 量化基座 + LoRA，激活仍较高精度，省的是基座显存不是新目标函数，见 `arch-qlora`。二面若只问「LoRA 和 QLoRA」，一句「量化基座 + 同一适配器」即可，不要再展开成第三遍 A 高斯 B 全零，除非被追初始化。

## 追问

- **只挂 q/v 行不行？** 行，原论文常用；指令跟随和 MLP 全挂往往更稳。用 ablation，不要教条。见 `code-lora`。
- **$r$ 怎么选？** 从 8/16 扫，看过拟合与下游增益。小 OCR 集 $r$ 过大是原帖风险点：容量大于数据。
- **QLoRA 精度掉在哪？** 掉在量化误差与反量化噪声，不是 LoRA 公式变了。PAGED optimizer、双重量化是工程，不是原理差。
- **多适配器怎么推理？** 按任务路由或加权 merge；同时 load 多个 $BA$ 要盯显存与数值。不要把 merge 过的权重再 merge 一次。
- **视觉侧冻结会不会学不动？** 投影先对齐模态，语言侧 LoRA 改条件生成。数据极少时先冻塔；域差大再解冻或给视觉 Linear 挂更小的 $r$。
