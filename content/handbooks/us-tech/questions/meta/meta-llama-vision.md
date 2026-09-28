---
id: meta-llama-vision
section: meta
order: 25
level: A
title: Meta：Llama 3.2 Vision / Mllama——cross-attn 视觉编码器怎么接
quick: >-
  不是把视觉 token 拼进自注意力序列。冻结 Llama 3.1 语言模型，ViT 出图表示，若干层 gated cross-attn 用文本
  $Q$、图像 $K/V$ 注入。适配器和编码器可训，LM 权重不动，所以是 3.1 的 drop-in。别讲成 LLaVA 投影层。
tags:
  - Meta
  - Llama
  - Vision
  - Cross-attention
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Llama 3.2 — Revolutionizing edge AI and vision with open, customizable models
    url: https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/
    type: primary
  - title: Llama 3.2 Vision model card
    url: https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD_VISION.md
    type: primary
  - title: Mllama — Hugging Face Transformers
    url: https://huggingface.co/docs/transformers/main/en/model_doc/mllama
    type: secondary
  - title: Flamingo — a Visual Language Model for Few-Shot Learning
    url: https://arxiv.org/abs/2204.14198
    type: secondary
---

Llama / 多模态岗会问 3.2 视觉怎么接到 3.1 上。公开答案在 Connect 博客和 vision model card：**另训的 image encoder + 一组 cross-attention adapter，训练时故意不更新语言模型参数。** Hugging Face 实现名叫 Mllama。不要发明 Llama 4 的融合方式；3.2 能讲到的就是 Flamingo 式 cross-attn，不是 Chameleon 那种离散早融合，见 `meta-early-fusion`。切块和上下文预算见 `meta-anyres`。

## 三块，不要画成「ViT 输出直接当词 embedding」

1. **视觉编码器。** 公开实现是两段 ViT：约 $32$ 层局部编码（按 tile）再约 $8$ 层 global，让不同切块互相看见。中间若干层和最后一层拼接再投影到 LM 隐空间。图像先按长宽比切成最多 $4$ 块正方形 tile（Meta Guard 3 Vision 卡片写每块 $560\times 560$），不是整图强行缩成一张正方形。
2. **语言模型。** 11B-Vision 挂在 Llama 3.1 8B 栈上（约 $40$ 层），90B-Vision 挂在 70B 上。名字里的 11B / 90B 是 **LM + 视觉** 合计，别当成又训了一个 11B 稠密 LM。文本自注意力、RoPE、GQA 仍按 3.1，见 `meta-llama-gqa`。
3. **Adapter。** 在 LM 若干层插入 cross-attn。11B 公开默认层号 $[3,8,13,18,23,28,33,38]$，大约每 $5$ 层一块。文本 token 当 $Q$，视觉表示当 $K/V$。**没有 RoPE，没有因果 mask**：图像不是从左到右的词。Query/Key 上再做 RMSNorm。残差用可学门控，初始化近 $0$，插进去时不立刻打坏已冻住的 3.1 表示，和 Flamingo 的 gated xattn 同一思路。

文本序列里只有少量 image 占位符，告诉模型「这里有图」；视觉信息不走 LM 自注意力的 $T$ 维。这和 LLaVA 把几百个视觉 token 拼进同一条因果序列是两种系统。

```python
def gated_xattn(x, vis, wq, wk, wv, wo, g):
    # x: [B, T, D] 文本; vis: [B, N, D] 视觉（N = tiles * patches）
    q = rmsnorm(x) @ wq
    k, v = vis @ wk, vis @ wv
    q, k = rmsnorm(q), rmsnorm(k)          # 无 RoPE
    attn = softmax((q @ k.transpose(-2, -1)) / d ** 0.5) @ v
    return x + tanh(g) * (attn @ wo)       # g 初值 0，起步近似恒等
```

Shape 口头报：自注意力仍是 $[B, T, D]$；cross-attn 的 $K/V$ 是 $[B, N, D]$，$N$ 跟 tile 数走，不跟 $128\mathrm{k}$ 文本窗走。Decode 每一步新 token 都要对全部视觉 $K/V$ 做一次 cross-attn，视觉 KV 算一次可缓存。

## 为什么冻 LM

博客写得很死：adapter 训练时 **更新编码器 + cross-attn，不更新 LM**。目的是文本能力不回退，视觉版当 3.1 的 drop-in。训练分两段：先大规模脏图文对，再中等规模高质量 / 知识增强对；后训练跟文本类似，SFT、rejection sampling、DPO，合成题用 Llama 3.1 滤和扩。数据量公开写约 $6\mathrm{B}$ 图文对，知识截止 2023-12。指令数据另有公开视觉指令集和约 $3\mathrm{M}$ 合成例。

错法：说「3.2 从零训了一个原生多模态 Transformer」，那是 Chameleon / Gemini 叙事，见 `google-gemini-mm`。错法二：冻视觉编码器只训一层 MLP，那是 LLaVA 连接器，3.2 明确改了 encoder。错法三：把 SAM 当视觉塔，见 `meta-segment-anything`，任务都不是 LM。

Serving：视觉 encoder 是额外 prefill，和文本 prefill 不同池。Cross-attn 的 $K/V$ 按图缓存，图不变就别重算。多图、高分辨率会线性抬 $N$，见 `meta-anyres`。安全闸门要能看图，见 `meta-mm-safety`。

## 追问

- **为什么不用 LLaVA 式拼接？** 拼进去会吃 $128\mathrm{k}$ 窗，图一多文本被挤掉。Cross-attn 把视觉放到旁路 KV，LM 权重还能冻住。
- **冻 LM 会不会视觉推理弱？** 会有上限：语言侧不能为了「读图」改表示。换来的是文本基准不塌、发版简单。要更强交错推理，得走早融合或解冻，见 `meta-early-fusion`。
- **90B 是 90B 稠密 LM 吗？** 不是。70B 文本栈加视觉组件，卡片写约 $88.8\mathrm{B}$。
- **占位符算不算视觉 token？** 占位符只占几个文本位置。计算量在 encoder 和 cross-attn 的 $N$ 上，不要用「一张图 = 1 个 token」或「一张图 = 两千个 LM token」两头糊弄。
- **和 Flamingo 的差别？** 骨架同类（gated xattn + 冻 LM）。3.2 挂的是现成 Llama 3.1、GQA、切块 encoder，产品目标是 drop-in，不是从零训 Perceiver。
