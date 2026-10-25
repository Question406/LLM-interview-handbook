---
id: google-gqa-mqa
section: google
order: 2
level: A
title: Google：MHA、MQA、GQA 怎么选？KV 显存差多少？
quick: "MHA 为每个 query head 保留独立 K/V，MQA 让所有 query head 共用一组 K/V，GQA 则用 $H_{\\mathrm{kv}}$ 组，满足 $1 < H_{\\mathrm{kv}} < H$。Decode 的 KV 显存和读取带宽都与 KV head 数成正比，我会根据质量和目标并发选择共享程度。"
tags:
  - Google
  - GQA
  - MQA
  - KV Cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: GQA — Training Generalized Multi-Query Transformer Models
    url: https://arxiv.org/abs/2305.13245
    type: primary
  - title: Fast Transformer Decoding — One Write-Head is All You Need (MQA)
    url: https://arxiv.org/abs/1911.02150
    type: primary
---

要降低 decode 的 KV 开销，可以让多个 query head 共享 K/V。MQA 共享得最彻底，所有 query head 共用一组；GQA 保留几组，在质量和带宽之间折中。比如把 32 组 KV 减到 8 组，cache 约变成原来的四分之一。MQA 来自 Google 论文，系统写法也见 `arch-gqa`。

注意力仍是 $QK^\top V$，共享改变的是 $K,V$ 的 head 数。先算一条请求的 KV 占用：

$$
\mathrm{KV\ bytes} \approx 2 \cdot L \cdot T \cdot H_{\mathrm{kv}} \cdot d_{\mathrm{head}} \cdot \mathrm{bytes}
$$

$L$ 层数，$T$ 上下文。$H_q$ 只影响当前 token 的 Q 投影，几乎不影响 cache。Decode 每步都要把历史 KV 从 HBM 读进来，所以 $H_{\mathrm{kv}}$ 直接影响带宽需求。

- MHA：$H_{\mathrm{kv}}=H_q$，质量上限，cache 最大。
- MQA：$H_{\mathrm{kv}}=1$，cache 降到约 $1/H_q$，质量在长上下文上往往先掉。
- GQA：例如 $H_q=32,H_{\mathrm{kv}}=8$，cache $\approx 1/4$。Llama 2 70B 公开配置就是这个量级。

训练时 GQA 要对齐：同一组 query head 共享 KV 投影。从已有 MHA checkpoint 升 GQA，GQA 论文用 mean pool 已有 KV heads 初始化，比随机更好。

先问服务的是 输入预填充（prefill，即处理输入并建立缓存） 还是 逐 token 生成（decode）。Prefill 是计算密集，MQA 省不了多少 FLOPs；decode 是内存密集，MQA/GQA 是重要的优化手段。再问上下文：8k 和 1M 的 KV 差两个数量级，GQA + 量化 cache 才够塞。

MQA 掉点通常来自 KV 表达不够，不是 softmax 写错。补救：加 $H_{\mathrm{kv}}$、加窗口注意力、加 MLA 一类低秩 KV（那是 DeepSeek 的另一条线，见 `kuaishou-gqa-mqa-mla`）。Google 面到这就停在 GQA 也可以。

实现时，attention kernel 里要把 $K$ repeat 成 $H_q$ 组，或走 GQA 专用 kernel。形状不对时，head 维的广播会出错。手写一步 decode 见 `code-kv-cache-step`。

## 追问

**训练也要用 MQA 吗？**
可以全程 GQA；也可以 MHA 训练、推理再 merge。后者有转换误差，要在验证集上量。

**和多 query 的「query」混淆？**
MQA 的 query 仍是多 head，少的是 key/value head。

**TPU vs GPU？**
带宽/计算比不同，但 KV 随 $T$ 线性涨这件事不变。TPU 上更要关心 padding 和 SPMD 切分，那是另一题。

## 相关题

- [[apple-ondevice-kv]]：把 GQA 和 8-bit KV 放到端侧算账，并发约为 1、最大长度静态预分配。
- [[google-tpu-decode]]：同为 Google 问法，把 GQA 放进 TPU decode 的 MXU 利用率和带宽墙里讲。
- [[meta-vllm]]：回答 GQA 之后为什么还要 PagedAttention：一个省每 token 的宽度，一个省预留长度和碎片。
- [[meta-llama-gqa]]：Meta 问法，用 Llama 2 70B 的 32 个 query head、8 个 KV head 把这里的公式算成具体数字。
- [[coding-mq-attn]]：MQA 的白板实现，K、V 只有一个 head，怎么对 query heads broadcast。
- [[coding-gqa-repeat]]：GQA 的白板实现，KV head 怎么 `repeat_interleave` 成 query heads、shape 怎么断言。
