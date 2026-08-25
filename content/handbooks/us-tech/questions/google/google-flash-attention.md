---
id: google-flash-attention
section: google
order: 6
level: S
title: Google/DeepMind 岗：FlashAttention 省的是 HBM 往返，不是 FLOPs 公式变了
quick: >-
  Attention 的 FLOPs 仍是 $O(T^2 d)$。标准实现把 $[T,T]$ 的分数矩阵写进 HBM 再读回来做 softmax，墙钟砸在带宽上。FlashAttention
  在 SRAM 里分块、在线 softmax，HBM 流量降到大约 $O(T^2 d^2/M)$，输出仍是精确注意力。
tags:
  - Google
  - DeepMind
  - FlashAttention
  - IO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention with IO-Awareness
    url: https://arxiv.org/abs/2205.14135
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

论文是 Dao 等人的 IO 感知精确注意力，不是 Google 出品。Google / DeepMind 训练和推理岗仍会问，因为你们在 TPU 上一样会被 **把 $[T,T]$ 物化进 HBM** 打死。开口先钉：公式没变，变的是存储层次上的往返次数。KV head 数那条杠杆见 `google-gqa-mqa`。

## 标准注意力慢在写回，不在乘加次数

令序列 $T$、头维 $d$。一次 head 的注意力：

$$
S=QK^\top/\sqrt{d},\quad P=\mathrm{softmax}(S),\quad O=PV
$$

FLOPs 仍是 $\Theta(T^2 d)$ 量级。朴素实现会把 $S$ 和 $P$ 以 $[T,T]$ 落到 HBM（GPU 上的高带宽显存；TPU 上对应片外 HBM）。现代加速器算力涨得比 HBM 快，attention 经常是 **memory-bound**：时间 $\approx$ 字节 / 带宽，不是 FLOPs / 峰值算力。

论文给的 HBM 访问量级：标准实现 $\Omega(Td + T^2)$；FlashAttention $O(T^2 d^2 / M)$，其中 $M$ 是片上 SRAM 容量。$d$ 和 $M$ 取 A100 一类常见值时，HBM 往返能少数倍。这就是墙钟。

具体数量级：$T=4096$ 时 $[T,T]$ 的 $P$ 仅 bf16 就要约 32MB 量级，还要写再读、正向再反向。A100 片上 SRAM 只有约 192KB/SM，HBM 带宽大约 1.5–2 TB/s，算力却是几百 TFLOP。把 32MB 来回搬几次，时间就被带宽吃掉。近似注意力论文爱报「FLOPs 从二次变线性」，但若仍把中间矩阵换来换去，墙上时钟不一定赢——FlashAttention 的对比对象就是这类「降 FLOPs 却不降 IO」的工作。

## 算法：分块 + 在线 softmax + 反向重算

SRAM 放不下整个 $S$。把 $Q,K,V$ 切成能进 SRAM 的 tile。对一块 query，依次流过 key/value 块，在片上累加输出。

Softmax 不是分块可结合的普通求和：每一行需要全局 max 和全局分母。在线 softmax 维护运行中的 $m$（目前最大值）和 $\ell$（目前指数和）。来下一块分数，先 rescale 已有分子分母，再累加。数值上等价于一次性 softmax，所以叫 **exact**，不是 Linformer 那种近似。

反向：不把 $P$ 存回 HBM。前向只留下 softmax 归一化统计，反向在片上重算注意力。重算 **增加 FLOPs**，但少读一个 $[T,T]$，在这个硬件比例下仍然更快。面试听到「重算一定更慢」要反驳：那是把 FLOPs 当成时间模型了。

实现上还把 QK、scale、mask、softmax、PV 融进一个 kernel，避免每步都 round-trip。融合是 IO 故事的一部分，不是「CUDA 写得好看」。

## TPU / Gemini 岗怎么落地

Google 面不会要你默 CUDA。要你迁移这个层次模型：

- Prefill / 训练长上下文：激活里那个 $[T,T]$ 先爆，Flash 式核把注意力激活从二次降到近似线性（仍存 $O,Q,K,V$ 和统计量）。
- Decode：每步 $T_{\mathrm{q}}=1$，主要 IO 是读历史 KV，不是物化 $T\times T$。这时 GQA / 量化 cache 比 Flash 更一等；Flash 仍避免多余写回。
- TPU 没有和 GPU 一样的 CUDA 编程模型，但 XLA 融合、Pallas / Splash Attention 一类，做的是同一件事：tile 留在 VMEM，别把完整注意力矩阵吐到 HBM。mesh 切分见 `google-tpu-mesh`。

错法：说 FlashAttention 把复杂度降到 $O(T)$；说它改变了 $QK^\top V$ 的数学；把它和 MoE 稀疏混成「都是少算」。MoE 少的是 FFN 激活参数，见 `google-gemini-moe`。

## 追问

- **和梯度检查点什么关系？** 检查点在层间丢激活、反向重算整层。Flash 在注意力内部不存 $P$，粒度更细，专门打 $[T,T]$ 这块 IO。
- **数值会不会和朴素实现不一致？** 在线 softmax 与分块浮点顺序不同，会有 ulp 级差。评测应用下游指标，不要用 bit exact 当回归。
- **窗口注意力还需要 Flash 吗？** 需要。窗口已经降了 FLOPs，但小块上仍不该把局部 $S$ 写到 HBM 再读。
- **为什么近似注意力墙上不一定更快？** 它们降的是算术次数，往往增加不规则访存。Flash 针对的是带宽，算术几乎不少。
- **Decode 一步还吃 Flash 红利吗？** $T_q=1$ 时主要 IO 是读 KV cache。Flash 仍避免多余写回，但长 decode 的一等杠杆是 GQA / 量化 cache，不是再融一次 softmax。
