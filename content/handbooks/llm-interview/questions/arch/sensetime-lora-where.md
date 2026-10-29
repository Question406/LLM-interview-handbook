---
id: sensetime-lora-where
section: arch
order: 191
level: A
title: 商汤应用实习：LoRA 原理、超参加在 Transformer 哪些模块？
quick: >-
  LoRA 冻结原权重，用 $W'=W+\frac{\alpha}{r}BA$ 加一个低秩更新，通常挂在 Attention 和 MLP 的 Linear
  层上。$r$ 控制更新的容量，$\alpha/r$ 控制更新的尺度。QLoRA
  是先把基座量化、再训同一套适配器；多模态模型还要分别决定视觉塔和语言模型挂在哪。
tags:
  - SenseTime
  - LoRA
  - QLoRA
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 商汤大模型算法应用实习面经（已offer）
    url: 'https://www.nowcoder.com/feed/main/detail/2762070c2c52472da06bf9ee59518d79'
    type: candidate-first-hand
  - title: 商汤大模型算法实习二面（已oc）
    url: 'https://www.nowcoder.com/feed/main/detail/363fb9aab5dc4507a5bfca6efb049fbf'
    type: candidate-first-hand
---

## 真题记录

- 公司：商汤
- 岗位：大模型算法应用实习一面；另一帖二面问 LoRA / QLoRA
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“LoRA 原理、常见超参、一般加在 Transformer 哪些模块”**；**“LoRA 和 QLoRA？”**

LoRA 是冻结 $W$，在 Linear 层上加一个低秩残差；常见超参是 $r$ 和 $\alpha$，挂载位置一般是 Attention 的 $W_q,W_k,W_v,W_o$ 和 MLP 的 gate/up/down。它并不是再训一层小网络。QLoRA 也算不上新算法，只是把基座权重量化到 4bit，再挂同一套适配器。商汤这类岗位还会追问多模态模型挂在哪，所以视觉侧和语言侧都要讲到，只答语言侧的 q/v 不够。初始化细节见 `tencent-lora-ab-init`，这里先把超参和挂载点讲清楚。

## 原理和超参：$r$ 是容量，$\alpha/r$ 是步长

$$
W'=W+\frac{\alpha}{r}BA,\qquad B\in\mathbb{R}^{d\times r},\; A\in\mathbb{R}^{r\times k}.
$$

可训练参数从 $dk$ 降到 $r(d+k)$。$r$ 太小会 underfitting；太大就接近全参扰动，在小的 OCR / 指令集上容易 overfitting，见 `arch-lora`。$\alpha$ 和学习率是耦合的：有效的更新尺度大约是 $\alpha/r$，只改 $r$ 不改 $\alpha$，更新尺度就跟着变了。常见的默认值是 $\alpha=2r$，或者固定 $\alpha=16$，你用的是哪种约定要说清楚。Dropout 打在 $BA$ 上，冻结的 $W$ 不参与。推理时可以把 $\frac{\alpha}{r}BA$ merge 回 $W$；有多个适配器时要按任务路由，不能随意直接相加。

## 挂在哪：Linear 可以，LayerNorm 别当残差插槽

语言侧优先挂 Attention 的 $W_q,W_k,W_v,W_o$ 和 MLP 的 gate/up/down，见 `meituan-lora-not-after-ln`。别插在 LayerNorm / RMSNorm 之后当随手的加性扰动：Norm 已经 calibration 过激活尺度，再加一个不受约束的可训练变换，训练初期容易出现数值突变。Embedding / lm_head 看任务，只有 vocabulary 变化较大时才考虑训练它们，比如新增语言或特殊 token。

多模态是商汤应用岗的高频追问。视觉塔默认冻结，只训投影（MLP / Q-Former / linear projector）和语言侧的 LoRA。任务更依赖 OCR 或定位时，再解冻视觉塔的最后几层，或者给 ViT 的 Linear 层加低秩更新。别在语言、视觉两侧无差别地全开 $r=64$。

QLoRA 是用 NF4 量化基座再加 LoRA，激活仍保持较高精度，省的是基座的显存，目标函数没变，见 `arch-qlora`。二面如果只问「LoRA 和 QLoRA」，答一句「量化基座 + 同一套适配器」就行；没被追问初始化，就不必展开 A 高斯、B 全零。

## 追问

**只挂 q/v 行不行？**
行，原论文常这么做。不过做指令跟随时，MLP 也全挂往往更稳。挂在哪可以用 ablation study 比较，见 `code-lora`。

**$r$ 怎么选？**
从 8/16 开始试，比较 overfitting 程度和下游任务的提升。原帖的风险点就在小 OCR 集上把 $r$ 开得过大，容量比数据还大。

**QLoRA 的精度掉在哪？**
掉在量化误差和反量化噪声上，LoRA 的公式没变。PAGED optimizer、双重量化是工程上的做法，原理上没有差别。

**多个适配器怎么推理？**
按任务路由，或者加权 merge。同时 load 多个 $BA$ 时要盯着显存和数值，也别把已经 merge 过的权重再 merge 一次。

**视觉侧冻结，会不会学不动？**
不太会。投影先把模态对齐，语言侧的 LoRA 负责改条件生成。数据很少时先冻住视觉塔；域差别大，再解冻，或者给视觉的 Linear 挂一个更小的 $r$。
