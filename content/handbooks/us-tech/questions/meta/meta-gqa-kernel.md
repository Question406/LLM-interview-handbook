---
id: meta-gqa-kernel
section: meta
order: 20
level: A
title: Meta：GQA 实现——repeat KV、kernel 融合，别只背论文配置
quick: >-
  Cache 里只存 $H_{\mathrm{kv}}$ 组。计算时要么把 KV `repeat_interleave` 成 $H_q$，要么 kernel 里用 $h_q //
  g$ 去索引。省的是 HBM 上的 KV 体积和 decode 读带宽；在 HBM 里先 repeat 再送 attention，等于把省下来的又花回去。
tags:
  - Meta
  - Llama
  - GQA
  - Kernel
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
  - title: FlashAttention-2
    url: https://arxiv.org/abs/2307.08691
    type: primary
  - title: PyTorch scaled_dot_product_attention GQA
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
    type: primary
---

`meta-llama-gqa` 问的是 70B 为什么 $32$ 个 query head、$8$ 个 KV head。本题问实现：repeat 发生在哪、cache 存几组、kernel 融什么。Llama / 推理岗白板常画 shape，不接受只背「GQA 是 4:1」。公式选型也可以对照 `google-gqa-mqa`。

## Shape 和 repeat 发生在哪

Llama 2 70B：$H_q=32$，$H_{\mathrm{kv}}=8$，$g=H_q/H_{\mathrm{kv}}=4$，$d=256$。投影后：

- $Q$：$[B, H_q, S_q, d]$
- $K,V$：$[B, H_{\mathrm{kv}}, S_{kv}, d]$

参考实现（Meta 早期 `llama` 仓库的 `repeat_kv`）是把 KV 沿 head 维 `repeat_interleave(g)`，变成 $[B, H_q, S_{kv}, d]$，再走普通 MHA。数学上每组 $4$ 个 query 点同一份 K/V。

**Cache 必须仍是 $H_{\mathrm{kv}}$ 组。** Decode 每步写 $8$ 组，不是 $32$ 组。若把 repeat 后的张量写进 cache，显存和读带宽回到 MHA，GQA 白做。正确时间线：从 cache 读 $[B, 8, S, d]$ → 计算时逻辑 repeat 或 kernel 内索引 → 输出 $[B, 32, 1, d]$。

```python
def repeat_kv(x, n_rep):
    # x: [B, H_kv, S, D]
    if n_rep == 1:
        return x
    b, h, s, d = x.shape
    x = x[:, :, None, :, :].expand(b, h, n_rep, s, d)
    return x.reshape(b, h * n_rep, s, d)
```

`expand` 不分配；`reshape` 若后面 kernel 要 contiguous，仍可能物化成 $4\times$ 体积。这就是「naive GQA」在 decode 上不省带宽的原因。

## Kernel 融合：别把 KV 在 HBM 里摊开

FlashAttention / PyTorch SDPA 的 GQA 路径：**不 materialize repeat**。线程块按 query head 调度，KV head 用整数除法 `h_kv = h_q // g` 去取。同一组 $4$ 个 query 共用 SRAM 里那一份 K/V tile。I/O 从「读 $32$ 份 KV」变成「读 $8$ 份、SRAM 里复用」。这才是 decode 墙钟下降的来源。

PyTorch：`scaled_dot_product_attention(..., enable_gqa=True)`，要求 $H_q$ 能整除 $H_{\mathrm{kv}}$。math 后端仍可能 `repeat_interleave`；flash / mem-efficient 后端走索引。面试要说：**API 开了 GQA 不等于没 repeat**，得看实际 backend。`TORCH_LOGS=kernel` 或 profiler 里若先看到巨大的 `repeat_interleave` 再看到 attention，就是走了慢路径。

Prefill 和 decode 账不同。Prefill 是大 GEMM / FlashAttention，算力墙，GQA 省的主要是 KV 写体积。Decode $S_q=1$，几乎没大 GEMM，时间砸在读历史 KV；这时 naive repeat 最亏。长窗（Llama 3.1 的 128k）把 $S_{kv}$ 拉大，融合路径的相对收益更大。量化 KV、paging 是下一层，见 `sys-kv-quant`、`sys-paged-attn`。

RoPE 只转 $Q,K$，在 repeat **之前**按 $H_{\mathrm{kv}}$ 转 K。先 repeat 再转，会做 $4\times$ 重复旋转。位置 id 仍按 cache 长度，见 `meta-llama-rope`。

## 训练侧别踩的坑

Llama 2/3 是**训练时就是 GQA**，K/V 投影输出就是 $H_{\mathrm{kv}}$ 组。不要训成 MHA 再在推理 repeat——那是 GQA 论文的 upcycle，有转换误差。训练 prefill 用融合 kernel 即可，不必为了「和 decode 一致」去物化 repeat。

`torch.compile` 可能把 `expand + reshape` 融掉，也可能 graph break 后留下一次拷贝。和 FSDP 一样，用 break 日志说话，见 `meta-pytorch-compile`。不要保证 compile 之后 naive repeat 就免费。

## 追问

- **$g$ 必须是 $4$ 吗？** 必须整除。$32/8=4$ 是 Llama 2 70B 的工作点，不是定理。8B Llama 3 也是 GQA，head 数按 conf，不要背成所有尺寸都 $32/8$。
- **MQA 是 $H_{\mathrm{kv}}=1$，kernel 更简单吗？** 索引更简单，质量更脆。70B 对话质量敏感，Meta 停在 GQA。kernel 上 MQA 是 GQA 的 $g=H_q$ 特例。
- **repeat 在 batch 维做可以吗？** 不要。repeat 的是 head，不是 batch。把 KV 在 batch 维扩会把不同请求的 cache 搅在一起。
- **和 TP 一起怎么切？** Query head 按 TP 切；每张卡上的 $H_q$ 仍要能整除本地 $H_{\mathrm{kv}}$。切乱了 GQA 组跨卡，还要为 KV 再通信，见 `sys-3d-parallel`。
