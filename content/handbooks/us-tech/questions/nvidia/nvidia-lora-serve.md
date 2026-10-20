---
id: nvidia-lora-serve
section: nvidia
order: 10
level: A
title: NVIDIA：多 LoRA 同服务，基础权重共享、adapter 切换成本
quick: >-
  底座 $W$ 只放一份。每个 adapter 是一组低秩 $A,B$，输出 $xW+(xB)A$。同服务的内存主项仍是底座和
  KV，不是 LoRA。切换成本：adapter 已经在 HBM 里只是换指针；要从 CPU 抓进来，才是一次小拷贝。同一
  batch 混多种 LoRA，要 grouped GEMM，不能假设所有行共用一个 $W'$。
tags:
  - NVIDIA
  - LoRA
  - Serving
  - TensorRT-LLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: NVIDIA TensorRT-LLM
    url: https://github.com/NVIDIA/TensorRT-LLM
    type: primary
  - title: S-LoRA — Serving Thousands of Concurrent LoRA Adapters
    url: https://arxiv.org/abs/2311.03285
    type: primary
  - title: Triton Inference Server
    url: https://github.com/triton-inference-server/server
    type: primary
---

## 题怎么来的

NVIDIA 推理栈（TensorRT-LLM / NIM / Triton）把多 LoRA 当成一等功能：很多客户模型是同一底座加各自 adapter。我会按三件事答：底座怎么共享、切换一次 adapter 贵在哪、一个 batch 里混 8 个 LoRA 和 8 次独立 forward 差在哪。不要答「我们为每个客户 deploy 一份 70B」。

## 底座共享

LoRA：$W'=W+BA$（或 $W+\alpha BA/r$）。$W$ 是 $[D_{\mathrm{in}}, D_{\mathrm{out}}]$，$B$ 是 $[D_{\mathrm{in}}, r]$，$A$ 是 $[r, D_{\mathrm{out}}]$，$r\ll D$。前向两种写法等价：显式拼出 $W'$，或

$$
y = xW + (xB)A.
$$

Serving 走后者：底座 GEMM 所有请求共用，再加两次瘦 GEMM。$x$ 是 $[B, T, D]$（逐 token 生成（decode） 时 $T=1$）。

显存：70B bf16 底座大约 140GB 量级，一份就够痛。单个 adapter 每层两个线性、若干层，常常几十到几百 MB。一千个 LoRA 仍可能小于再复制一份底座。所以正确图是：HBM 里一份 $W$ 加 adapter 池（热的在 GPU，冷的在 CPU / NVMe）。S-LoRA 把 adapter 也分页，和 KV 的 paged 思想同类，见 `nvidia-paged-kv`。

## 切换成本

分清三种「切」。

1. 进程级换模型：把整份 $W$ 卸了再装另一份。秒级，不可接受。多 LoRA 就是为了避免这个。
2. 请求级换 adapter，底座不动：若 $A,B$ 已在 HBM，切换是绑一份指针 / 改 kernel 参数，微秒到亚毫秒。若在 CPU，HtoD 拷贝按 adapter 字节走，通常远小于一次 70B 权重加载，但仍可能比一步 decode GEMM 显眼：decode 本身就很短。
3. 同一 batch 多种 adapter：没有单一 $W'$。要对 batch 维做 segmented / grouped GEMM（Punica 的 SGMV 一类）：同一 LoRA 的行打成一段，一段一次瘦 GEMM。实现复杂，但底座那次大 GEMM 仍然只做一遍。

热池策略：LRU 留 $K$ 个 adapter 在 GPU。$K$ 太大挤 KV；$K$ 太小，切客户时反复 HtoD，p99 出现「偶发尖刺」。面试把尖刺归因到 adapter miss，不要怪底座。

Compute：额外 FLOPs 大约 $2\cdot B\cdot T\cdot D\cdot r$ 量级（每个 LoRA 线性）。Prefill $T$ 大时这笔能看见；decode $T=1$ 时通常远小于读 KV。所以 decode 路径上，LoRA 的主要风险是调度和内存，不是算术。

## 和 Triton 怎么接

一种是每个 LoRA 当 Triton 里一个「虚模型」，共享同一份 TensorRT-LLM 引擎实例，请求带 adapter id。另一种是 Python backend 自己维护池。不要为每个 LoRA 起一个 `instance_group` 把 $W$ 复制 N 份，那是把 Triton 的多模型理解反了，见 `nvidia-triton-infer`。

不同 LoRA 的 KV 不能因为 输入提示（prompt） 文本相同就 prefix 共享：投影矩阵已经不同。只有同一 adapter、同一前缀才有共享资格。

## 追问

- **$r$ 从 8 加到 64，延迟怎么走？** Prefill 的 LoRA GEMM 近似线性于 $r$；decode 更可能仍是 KV 带宽墙，$r$ 加四倍用户不一定感觉得到。要 profile 两条路径，不要只报 FLOPs。
- **能把 LoRA merge 进 $W$ 吗？** 单 adapter 服务可以，省掉瘦 GEMM，但失去多租户。多 LoRA 同服务不要 merge。
- **和 prompt tuning / prefix 比？** Prefix 改的是输入 token / KV 前缀，多租户时 KV 变长；LoRA 改权重，KV 长度不变。显存账不同。
- **精度？** 底座 FP8 / INT8 时，adapter 常留较高精度再乘回去。量化底座加随机初始化 LoRA 混在一起要单独看误差，不要假设和 bf16 LoRA 同一套指标。FP8 训练配方见 `nvidia-fp8`，不要和推理 INT8 混，见 `nvidia-int8-quant`。
