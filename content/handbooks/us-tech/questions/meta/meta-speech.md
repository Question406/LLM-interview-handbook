---
id: meta-speech
section: meta
order: 31
level: A
title: Meta：语音 token / 语音 LLM 公开概念（别编内部 ASR 栈）
quick: "公开锚点是 Spirit LM：把 Llama 2 7B 续训到 HuBERT 离散单元上，和 BPE 交错做 next-token。声学细节另走 EnCodec 一类 codec token。这不是 Llama 3.2 产品，也不是生产 ASR。别讲内部语音栈或未公开的 Llama 语音权重。"
tags:
  - Meta
  - Speech
  - Spirit LM
  - Tokens
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Spirit LM — Interleaved Spoken and Written Language Model
    url: https://arxiv.org/abs/2402.05755
    type: primary
  - title: HuBERT — Self-Supervised Speech Representation Learning by Masked Prediction of Hidden Units
    url: https://arxiv.org/abs/2106.07447
    type: primary
  - title: EnCodec — High Fidelity Neural Audio Compression
    url: https://arxiv.org/abs/2210.13438
    type: secondary
  - title: SeamlessM4T
    url: https://ai.meta.com/research/publications/seamlessm4t/
    type: secondary
---

语音岗在 Llama 面试里容易答飞：去讲生产 ASR、对齐、内部级联。公开能讲的是 **语音离散化和语音 LLM**。FAIR 的 Spirit LM（2024）把 Llama 2 7B 继续预训练到语音单元上；AudioCraft 的 EnCodec 给的是 codec token；SeamlessM4T 是编码器和解码器翻译，不是 decoder-only LLM。Llama 3.2 发布的是视觉和端侧小模型，**没有**官方语音 LM。不要发明 Llama 4 音频内部。续训和 `meta-continual-pt` 同一类风险：文本能力会不会塌。

## 两条离散化，不要并成「语音 token」

**语义单元（HuBERT）。** 自监督 Transformer 对声学帧做掩码预测，再 k-means 聚类。常见约 $50\mathrm{Hz}$（$20\mathrm{ms}$ 一帧），码本几百到上千。连续相同簇会 **去重**，否则停顿和长元音把序列拉爆。Spirit LM Base 走这条：音素级、内容为主，韵律弱。

**声学 codec（EnCodec）。** 神经压缩：RVQ 多层残差量化，重建波形。帧率看配置，常在 $75$–$150\mathrm{Hz}$ 量级，多层 codebook 还要乘。适合生成可听的语音 / 音乐，语义更脏。Spirit LM Expressive 在 HuBERT 之外再交错 pitch / style 单元，为的是把韵律留下，仍不是把 EnCodec 当主词表。

口算：一分钟语音，HuBERT 去重前约 $60\times 50=3000$ 个单元；同一句话的 BPE 可能只有几十到两百。语音 LLM 的上下文开销是文本的十几倍，serving 不能按「再开一个模态开关」来想。交错时用特殊前缀标记文本段和语音段，随机在词边界切模态，强迫对齐。

```python
def hubert_stream(units):
    # units: 50 Hz 的簇 id
    dedup = [u for i, u in enumerate(units) if i == 0 or u != units[i - 1]]
    return ["SPEECH"] + dedup
```

Shape：文本 $[B, T_{\mathrm{txt}}, D]$，语音 $[B, T_{\mathrm{sp}}, D]$，拼在序列维。位置编码要能区分模态；别假定 RoPE 的「词距离」对 $20\mathrm{ms}$ 帧还有同样含义。

## Spirit LM 实际在训什么

公开配方：Llama 2 7B 当起点，混 **纯文本、纯语音、词级交错的语音与文本平行句**，仍是 next-token。交错用自动对齐的小平行语料，在词边界插入模态切换。这样 few-shot 能做 ASR（语音进、文本出）、TTS（文本进、语音单元出再 vocoder）、语音分类。它不是为生产词错误率优化的 CTC / RNN-T 系统。

和级联 ASR→LLM→TTS 的差别：级联每段可独立升级、延迟和错误会级联；交错 LM 把对齐学进同一套权重，但解码语音单元不等于可上线的音色和延迟。SeamlessM4T 走的是编码器和解码器多语言语音翻译，评测是 BLEU / ASR 指标，不要和 Spirit LM 的 few-shot 混报。

常见误区是：说 Llama 3 自带语音。Herd 没有把语音当一等模态发布。错法二：把 HuBERT 簇当字符。簇没有字母表，ASR 是 LM 在交错训练里学到的转写，不是码本自带的。错法三：现场画内部流式 ASR、端侧唤醒、电话栈，那不是公开 Llama 题。

Vocoder 是另一段：LM 只吐离散单元，波形要 HuBERT-vocoder 或 EnCodec decoder。单元去重丢了时长，TTS 会发飘，所以 Expressive 才把 pitch / style 交错回去。Serving 上语音 逐 token 生成（decode） 的 token 率按帧率走，和文本 tokens/s 不是同一个 SLO。

## 追问

- **为什么去重？** 长元音和静音会重复同一簇，不去重就把上下文预算给声学平稳段。去重会丢时长，所以 Expressive 才另加 pitch / style。
- **能否当生产 TTS？** 研究演示可以。稳定音色、流式、叠字、安全（克隆）都还要 vocoder 和策略层。别把 few-shot 样例当 SLA。
- **和视觉 3.2 同一套融合吗？** 不是。3.2 是冻 LM + cross-attn；Spirit LM 是把离散单元塞进同一条因果序列，更接近早融合，见 `meta-early-fusion`。
- **上下文怎么定预算？** 先按帧率估 $T_{\mathrm{sp}}$，再决定下采样或切块。一分钟语音可以吃掉几千 token，和长文档抢窗。
- **内部 ASR 能不能讲？** 不要。面试停在公开论文：HuBERT、EnCodec、Spirit LM、Seamless。生产级联可以当对比，但别编系统名和数字。
