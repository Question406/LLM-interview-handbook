---
id: google-gqa-mqa
section: google
order: 2
level: A
title: Google：MHA、MQA、GQA 怎么选？KV 显存差多少？
quick: >-
  MHA 是 $H$ 组独立 K/V；MQA 全 query head 共用 1 组 K/V；GQA 是 $H_{\mathrm{kv}}$ 组，$1 <
  H_{\mathrm{kv}} < H$。Decode 显存和带宽跟 $H_{\mathrm{kv}}$ 成正比。Gemini / PaLM 一类推理优化默认从
  MQA/GQA 讲起，不要只背公式。
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

Google 论文把 MQA 做出来，GQA 是折中。国内也高频，系统写法见 `arch-gqa`。美国 Google / DeepMind 推理岗会把它问成「你怎么给 decode 降 KV」，而不是名词对比。

## 三档

注意力仍是 $QK^\top V$。变的是 $K,V$ 的 head 数。

$$
\mathrm{KV\ bytes} \approx 2 \cdot L \cdot T \cdot H_{\mathrm{kv}} \cdot d_{\mathrm{head}} \cdot \mathrm{bytes}
$$

$L$ 层数，$T$ 上下文。$H_q$ 只影响当前 token 的 Q 投影，几乎不影响 cache。Decode 每步都要把历史 KV 从 HBM 读进来，所以 $H_{\mathrm{kv}}$ 直接打在带宽上。

- MHA：$H_{\mathrm{kv}}=H_q$，质量上限，cache 最大。
- MQA：$H_{\mathrm{kv}}=1$，cache 降到约 $1/H_q$，质量在长上下文上往往先掉。
- GQA：例如 $H_q=32,H_{\mathrm{kv}}=8$，cache $\approx 1/4$。Llama 2 70B 公开配置就是这个量级。

训练时 GQA 要对齐：同一组 query head 共享 KV 投影。从已有 MHA checkpoint 升 GQA，GQA 论文用 mean pool 已有 KV heads 初始化，比随机更好。

## 面试怎么落到 Gemini 式系统

先问服务的是 prefill 还是 decode。Prefill 是计算密集，MQA 省不了多少 FLOPs；decode 是内存密集，MQA/GQA 是一等杠杆。再问上下文：8k 和 1M 的 KV 差两个数量级，GQA + 量化 cache 才够塞。

MQA 掉点通常来自 KV 表达不够，不是 softmax 写错。补救：加 $H_{\mathrm{kv}}$、加窗口注意力、加 MLA 一类低秩 KV（那是 DeepSeek 的另一条线，见 `kuaishou-gqa-mqa-mla`）。Google 面到这就停在 GQA 也可以。

实现注意：attention kernel 里要把 $K$ repeat 成 $H_q$ 组，或走 GQA 专用 kernel。Shape 错了会在 head 维广播翻车。手写一步 decode 见 `code-kv-cache-step`。

## 追问

- **训练也要用 MQA 吗？** 可以全程 GQA；也可以 MHA 训练、推理再 merge。后者有转换误差，要在验证集上量。
- **和多 query 的「query」混淆？** MQA 的 query 仍是多 head，少的是 key/value head。
- **TPU vs GPU？** 带宽/计算比不同，但 KV 随 $T$ 线性涨这件事不变。TPU 上更要关心 padding 和 SPMD 切分，那是另一题。
