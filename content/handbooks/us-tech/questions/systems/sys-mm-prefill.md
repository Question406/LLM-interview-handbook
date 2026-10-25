---
id: sys-mm-prefill
section: systems
order: 26
level: S
title: 系统：多模态 prefill，视觉 encoder 与 LLM 形状、batch 不齐
quick: "多模态 prefill 先跑视觉 encoder，再投影并插入文本序列，LLM 处理的长度包含 $T_{\\mathrm{vis}}$。分辨率不同，视觉 token 可从几百涨到几千，直接补齐成稠密 batch 会浪费计算。调度时要分别看 encoder、LLM prefill 和 decode，结合缓存、分组与拆池控制长尾。"
tags:
  - vLLM
  - Google
  - DistServe
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Optimization and Tuning — vLLM
    url: https://docs.vllm.ai/en/latest/configuration/optimization.html
    type: primary
  - title: Disaggregated Encoder — vLLM
    url: https://docs.vllm.ai/en/latest/features/disagg_encoder.html
    type: primary
  - title: "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving"
    url: https://arxiv.org/abs/2401.09670
    type: primary
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: https://arxiv.org/abs/2312.11805
    type: secondary
---

多模态 prefill 要分别调度视觉 encoder 和 LLM：前者把图片变成特征，后者把这些特征和文字一起处理，组成 $[B,T,d]$ 的输入并建立 KV。比如同样一张图，边长从 224 到 896，视觉 token 可以从约 256 到 4096；若与纯文本请求一起补齐，计算和首 token 延迟都会增加。下面依据 vLLM 多模态与拆 encoder 的公开方案、DistServe 的 PD 分离分析 serving，模型侧见 `google-gemini-mm`。

典型开源 VLM（LLaVA / Qwen-VL 一类）的处理链路分为四步：

1. **Vision encoder。** 图切 patch，ViT 前向。$T_{\mathrm{vis}}$ 跟分辨率走，不跟「几张图」走。边长 224、patch 14，大约 $16\times 16=256$ 个 token；边长 896 就是约 4096。视频再乘帧。输出常是 packed `[sum_i T_{\mathrm{vis},i}, D_{\mathrm{vis}}]`，或硬 pad 成 `[B_{\mathrm{img}}, T_{\max}, D_{\mathrm{vis}}]`。
2. **Projector。** $D_{\mathrm{vis}}\to d_{\mathrm{llm}}$，形状变成 LLM hidden。
3. **拼接。** 按 chat template 里的图占位符，把视觉向量插进文本 embedding。LLM prefill 的序列长是 $T_{\mathrm{text}}+T_{\mathrm{vis}}$，不是 $T_{\mathrm{text}}$。
4. **LLM prefill / decode。** 之后才有 KV。Encoder 输出本身不是 KV；KV 是 LLM 层写出来的。Encoder cache（EC）和 KV cache 是两层，vLLM disagg encoder 专门传 EC。

Batch 不齐出在三处：

**图和文本混部。**
同一步里有的请求 $T_{\mathrm{vis}}=0$，有的 $T_{\mathrm{vis}}$ 几千。硬 pad 到 $T_{\max}$ 会让纯文本行做大量 mask 废计算。
**图和图像之间。**
分辨率、裁剪、动态分辨率（NaViT / Qwen 的 `grid_thw`）让 $T_{\mathrm{vis}}$ 差很多。Encoder 若要求整齐的 `[B, 3, H, W]`，就要 pad 像素或按分辨率分组统计。
**占位符和 feature 对不齐。**
模板说这张图占 256 个 token，encoder 却出了 1024，embedding 对不上，是正确性 bug，不是慢。调度切块时不要把一张图的视觉 token 从中间切开。Chunked prefill 的文本块可以切，图块不行，见 `sys-chunked-prefill`。

口算：LLM 70B prefill 吃 $[T,d]\times[d,d]$；ViT 是另一套小得多的权重。Encoder 相对 LLM 往往更轻，但高清、多图、并发时 Conv / ViT 仍能占满 首个 token 的等待时间（TTFT）。默认把 encoder 跟 LLM 一起做 TP、切 encoder 权重，小 ViT 的 GEMM 更瘦、还要同步。vLLM 公开了 encoder 按图做 batch 维 DP、LLM 仍 TP 的旋钮。文档给过 TP$=8$ 大约一成 TTFT / 吞吐，未优化的 Conv3D 还能再挖一截。这项公开配置说明 encoder 和 LLM 可以采用不同并行方式。

Encoder 偏 compute、形状乱；LLM decode 偏带宽、要稳定的瘦 GEMM。同一 GPU 上：一条 4k 视觉 token 的 encoder+prefill 可以占满 SM 几百毫秒，在飞 decode 的 每个 token 的生成间隔突然变长。这和纯文本长 输入提示（prompt） 同一类伤害，见 `sys-prefill-decode-disagg`，只是前面多了一段 encoder。

我会按负载选择以下处理方式：

**Processor / encoder cache。**
同一张图重复出现，缓存 processor 输出或 EC，不要每轮重跑 ViT。
**分辨率分组统计 + ragged pack。**
相近 $T_{\mathrm{vis}}$ 组 batch；跨度太大就拆步。
**Chunked prefill。**
只切文本后缀；视觉段一次齐。
**E 与 PD 分离。**
Encoder 单独实例，EC 经 connector 注入 prefill 池。纯文本请求绕过 encoder。vLLM 文档把好处写成：独立扩容、缩短 TTFT 关键路径、跨进程复用 EC。短图、低并发不要拆，多一次传输。

Prefix / radix：文本系统提示可以命中；图的 KV 只有 LLM 算过之后才有。EC 命中不等于 KV 命中。图变一个像素，视觉 token 变，从占位符起整段 LLM 前缀都要重算，见 `sys-prefix-cache`、`sys-radix-tree`。

错误说法：一张图等于一个 token；encoder TP 一定比 DP 好；chunked prefill 可以从一张图中间切开；多模态 batch 就是把 pixel 和 text 拼成一个稠密 `[B, T, d]`。前两条把形状说错了，后两条把调度和正确性搞混了。

监控：encoder 时间、LLM prefill 时间、视觉 token 直方图、$T_{\mathrm{vis}}$ 对 TTFT 的贡献、EC hit。把这些阶段分开统计，才能看出平均 tokens/s 掩盖的图像处理成本。

## 追问

**为什么不能和文本请求同一个 padded batch？**
$T_{\mathrm{vis}}$ 可以从 0 到几千。Pad 让纯文本行做废 GEMM，KV 也按 $T_{\max}$ 预留。要 ragged / packed，或按模态分步。

**Encoder TP 和按图 DP 差在哪？**
前者切小 ViT 权重，通信多、GEMM 瘦；后者复制权重、按图并行，适合 encoder 相对 LLM 很小的时候。

**视觉 token 进不进 prefix cache？**
进的是 LLM 算完的 KV。Encoder 输出要另缓存。图一变，两边都 miss。

**什么时候上 disaggregated encoder？**
图流量大、纯文本不能被 encoder 堵住、想单独扩 encoder 卡。短图低并发，传输是税。

**Chunked prefill 能切图吗？**
不要切单个 multimodal item。占位符计数和 feature 行必须一步对齐。

**和 DistServe 什么关系？**
DistServe 拆 prefill/decode。多模态再拆 encoder，变成 E / P / D 三池，KV 和 EC 都要搬家，体积各自算。
