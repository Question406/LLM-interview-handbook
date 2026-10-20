---
id: google-gemini-moe
section: google
order: 5
level: S
title: Google：Gemini 系 MoE 面试怎么讲路由、专家容量和 decode 成本
quick: "路由为每个 token 选 top-$k$ 专家，专家满了按 capacity 丢 token。稀疏省的是训练 FLOPs；decode 时读专家权重和 all-to-all 才是耗时，不会便宜 $E$ 倍。"
tags:
  - Google
  - Gemini
  - MoE
  - Routing
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Gemini 1.5 — Unlocking multimodal understanding across millions of tokens of context
    url: https://arxiv.org/abs/2403.05530
    type: primary
  - title: Switch Transformers — Scaling to Trillion Parameter Models with Simple and Efficient Sparsity
    url: https://arxiv.org/abs/2101.03961
    type: primary
  - title: GShard — Scaling Giant Models with Conditional Computation and Automatic Sharding
    url: https://arxiv.org/abs/2006.16668
    type: primary
---

Gemini 1.5 技术报告只确认 Pro 是稀疏 MoE Transformer，并回溯 Google 从 Shazeer 2017 到 Switch / GShard / GLaM 的线。专家个数、$k$、容量系数没有公开成可背的超参。 现场用 Switch 的语言讲机制，声明「Gemini 具体 $E,k$ 我不知道」，比编一个 $k=2$ 安全。注意力侧的 KV 另一题，见 `google-gqa-mqa`。

## 路由：每个 token 一张小票

MoE 层把稠密 FFN 换成 $E$ 个专家。路由器对 token 隐状态做线性 + softmax（或 sigmoid），挑 top-$k$ 个专家。激活参数大约是

$$
\theta_{\mathrm{act}} \approx \theta_{\mathrm{attn}} + k\cdot\theta_{\mathrm{expert}}
$$

总参数里专家是 $E\cdot\theta_{\mathrm{expert}}$。$E$ 变 8 倍，训练 FLOPs 不必变 8 倍，这是报告里「质量接近更大稠密模型、训练算力更低」的来源。

Switch 把 $k$ 收到 1，通信简单；GShard 常用 top-2。面试别教条「必须 top-2」。$k=1$ 省 dispatch，$k>1$ 质量更稳、逐 token 生成（decode） 更贵。负载均衡 auxiliary 损失（loss） 逼 token 别全涌进同一个专家，否则其余专家得到的训练信号太少，稀疏退化成「几个稠密 FFN + 一堆废权重」。

## 专家容量：不讲这句话等于没做过

令一层里要路由的 token 数为 $n$（大约 $B\cdot T$）。每个专家的槽位

$$
C=\left\lceil \gamma\cdot n / E\right\rceil
$$

$\gamma$ 是 capacity factor，常见 $1.0$：$1.25$。路由器按分数往专家里塞，塞满就 drop：这个 token 的 MoE 输出走残差 / 零，等于这层 FFN 没算。$\gamma$ 太小，掉 token 伤害质量；太大，专家 padding 变多，all-to-all 体积涨，稀疏的吞吐红利没了。

训练 batch 大，$n/E$ 还能填满专家。Decode 一步 $n$ 很小：$B$ 是并发请求数，每步 $T=1$。此时 $C$ 按公式会小到可笑，实现上会给最小容量、或者改成「有请求就调用被点名的专家」。面试要自己切场景：输入预填充（prefill，即处理输入并建立缓存） 像训练，decode 不像。

All-to-all：token 按专家编号 gather 到持有那份权重的芯片，算完 scatter 回来。Shape 从 `[B, T, D]` 变成「每个专家一段变长」。变长 + padding 是 TPU 上 MoE 变慢的常见原因，和 mesh 切分绑在一起，见 `google-tpu-mesh`。

## Decode 成本：稀疏计算不保证生成耗时同比减少

训练 / prefill：每个 token 只跑 $k$ 个专家，矩阵很大、算力密度高，稀疏划算。

Decode：

- 权重运动。 被点名的专家要从 HBM 读进计算单元。并发低时，你付的是「读很大一块 FFN」的带宽，不是 $k/E$ 的 FLOPs 故事。专家并行把不同专家放不同芯片，单 token 还可能跨芯片取专家，延迟比稠密 FFN 更差。
- 路由本身很便宜，别把它说成瓶颈。瓶颈是 dispatch 和专家 GEMM 的启动开销。
- 小 batch 不均衡。 16 个并发请求可能 12 个进同一专家，芯片间打满 / 空转并存。容量和 load balance 是训练概念，serving 要看专家热度。
- 和 GQA 叠加。 MoE 砍的是 FFN 计算；decode 实际耗时经常仍在读 KV。长上下文先砍 $H_{\mathrm{kv}}$，见 `google-gqa-mqa`，再谈专家并行。

总参数用来讲记忆容量和磁盘；延迟要用激活参数 + 通信拓扑 + 并发。「Gemini 很大所以 MoE」因果反了：是要用给定激活预算换更大容量，才上 MoE。

## 追问

- **专家会不会变成按任务分工？** 可能出现领域特化，不是调度器保证的。Pathways 愿景里的「一模型多任务」不要画成「专家 3 = 翻译」，见 `google-palm-pathways`。
- **drop 的 token 要补算吗？** 训练常丢弃并靠残差；推理为了质量会提高 $\gamma$ 或允许溢出到备份专家。补算等于把容量缺口变成尾延迟。
- **共享专家（shared expert）干什么？** 所有 token 都过的公共 FFN，降低路由器压力、留一条总在的计算。公开 Gemini 没把这写成必选项，当作可选工程。
- **MoE 和量化谁先？** 先让路由和容量在目标并发下不掉质量，再量化专家权重。量化解决 HBM，不解决 all-to-all 的短消息延迟。

## 相关题

- [[google-moe-routing]]：同为 Google 的 MoE 题，和本题高度重合；那题更落到实现，讲 permute、pad 到容量和 decode 时怎么改 EP 拓扑。
- [[openai-moe-aux-loss]]：本题提到的负载均衡展开成 aux loss 公式，以及路由塌缩怎么从直方图和路由熵上发现。
- [[meta-llama-moe]]：Llama 4 的 shared + top-1、dropless 方案，和本题的容量丢 token 正好是两种取舍。
- [[sys-expert-parallel]]：本题 decode 成本里 all-to-all 那部分的系统展开，讲 EP 怎么切卡、热点专家怎么拖尾。
- [[xai-grok-moe]]：同样追问 decode 时 MoE 为什么不便宜，换成 Grok-1 的 8 专家 top-2 公开配置来讲。
