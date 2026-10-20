---
id: apple-ane
section: apple
order: 7
level: S
title: Apple：Neural Engine 约束（静态 shape、算子白名单）对 Transformer 设计的影响？
quick: >-
  ANE 要静态 shape、有限算子、fp16/int8、张量布局接近 $[B,C,1,S]$，Linear 常改成 $1\times 1$
  Conv。动态核、可变长 nucleus、IEEE $-\infty$ mask、随意 reshape 都会整段掉出 ANE。Transformer
  要按这些约束改注意力、KV、采样，而不是把 GPU 图原样导出。
tags:
  - Apple
  - Neural Engine
  - Transformer
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Deploying Transformers on the Apple Neural Engine
    url: https://machinelearning.apple.com/research/neural-engine-transformers
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: On-Device Llama 3.1 with Core ML
    url: https://machinelearning.apple.com/research/core-ml-on-device-llama
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

Apple 2022 就把 Transformer 往 ANE 上搬写成公开指南；2024 的 AFM 明确 on-device 跑在 Neural Engine 上，并提到高效 KV 更新。面试不是问「ANE 是 NPU 吗」，是问你敢不敢为芯片改模型。GPU 上漂亮的动态图，在这里会变成 CPU 回退和拷贝，把 30 token/s 打穿。量化细节见 `apple-ondevice-quant`，采样见 `apple-topk-sample`。

## 硬件认什么图

公开实现和后续 Core ML 路径里，反复出现的约束可以收成四条：

1. 静态 shape。输入、输出、中间张量两次调用不能变。Decode 不能让 KV 沿时间维长一格，除非那一格在导出时就按 $S_{\max}$ 分配好。做法：cache 预分配 $[B,H_{\mathrm{kv}},S_{\max},d_h]$，用 position 写入当前槽；或只读 cache 加外置拼接，模型返回本步新 $k,v$。Core ML 的 stateful 模型把 KV 登记成跨 `predict` 存活的 state。编译产物往往是一组入口，每个对应一个 `(context_len, extend_len)`。
2. 布局和算子。ANE 更适合处理卷积。`Linear` 的 $[B,S,D]$ 常改写成 $1\times 1$ Conv2d，激活排成 $[B,D,1,S]$（BC1S）。最后一维要按 64 字节对齐；写成 1 会触发离谱 padding。Rank 超过 5 直接拒。dtype 主 fp16 / int8；Python 里随手写的 fp32 字面量可能生成 ANE 无法处理的缓冲，整段切到 GPU。
3. 白名单与驻留。不在 ANE 的 op（某些 gather、动态分支、奇怪的 softmax 轴）会让编译器切图，中间结果来回拷。小模型上拷贝比计算还贵。原则是整网留在 ANE，而不是「大部分在 ANE」。
4. Softmax / mask。大空间维上的 softmax 不好切块。公开 ANE Transformer 会按 head 拆 softmax 以保住 L2。Mask 用有限大负数，不要赌 $-\infty$，原因在 `apple-ondevice-quant`。有的实现里 score 甚至是 $KQ$ 而不是 $QK^\top$，mask 的 shape 跟着转置，写成 GPU 习惯可能悄悄出错。

Apple 还公开用 Talaria 看每层时延和功耗，指导 palettization 比特。面试提到「不是只看 BLEU，还看这一层会不会掉出 ANE」就对味了。

## Transformer 要改的设计，不是只改导出脚本

这些约束会反向逼架构：

- GQA / 共享 embedding。 AFM on-device 用 grouped-query attention、输入输出 embedding 共享，词表 49k。KV 带宽和驻留是一等公民，和 `google-gqa-mqa` 同一笔账，只是墙从 HBM 换成了手机 DRAM / ANE SRAM。
- 固定块 输入预填充（prefill，即处理输入并建立缓存）。 一次吃 64 或 128 个新 token，用 mask 盖住 padding。变长 输入提示（prompt） 就 pad 到下一个编译好的档位。档位太稀，浪费算力；太密，二进制膨胀。
- 解码步尽量没有数据依赖控制流。 Top-k 固定 $k$ 比 nucleus 友好。MoE 路由、条件 adapter 切换，都要嘛静态 max expert，要嘛在 CPU 上换 weight 再跑一段纯静态图。AFM 的做法是整基础模型不变，热插拔几十 MB 的 LoRA，见 `apple-personalize`。
- KV 更新必须是 ANE 认的 slice。 随机 scatter 容易回退。Apple 文里专门写了 neural engine 上的 KV update，面试要能说出「预分配加定点写入 / 只读拼接」两种，不要画一个 `torch.cat` 就结束。
- 2025 的 KV sharing。 模型切成两块，第二块复用第一块末层 KV，cache 降约 37.5%，prefill 还可以跳过第二块。这是为端侧带宽改深度结构，不是训完再剪枝的边角。

视觉侧 HyperDETR 一类文章还说明：为了整网留在 ANE，他们把 decoder 和 Transformer 路径解耦，用 $1\times 1$ 动态卷积出 mask。语言侧同样精神：宁可改模块边界，也不要在 ANE 里塞一个编译不过的 attention 变体。

## 我会怎么答设计题

先问上下文上限和是 prefill 还是 逐 token 生成（decode）。再画三张图：训练用的 GPU 图、导出前的 ANE 图（Conv、BC1S、静态档位）、运行时的 cache 状态。主动列失败模式：某层 LayerNorm 手写分解后掉 CPU；mask 用了 $-\infty$ 出 NaN；nucleus 让采样回 CPU 占了好几毫秒。验收：Instruments / Core ML 的 compute unit 全是 Neural Engine，以及 greedy 下与 CPU 参考逐 token 一致。哪一层掉出 ANE，先看这条 op 的 shape、dtype 和是否在白名单，再谈「再量化一点」。

## 追问

- **为什么不一直用 GPU？** GPU 带宽和功耗对后台常驻的 Siri / 输入法不友好。ANE 是能效路径。Llama 3.1 那篇 Core ML 文在 Mac 上走 GPU，是另一条产品线，别和 iPhone AFM 混。
- **动态 shape 将来会不会有？** 即使运行时弹性变好，面试仍按今天的静态档位答。产品要的是可预测时延，见 `apple-siri-latency`。
- **FlashAttention？** ANE 不是那套 CUDA tiling。等价物是编译器认的切头 softmax 加驻留，不要把论文 kernel 名直接搬过来。
- **算子不在白名单怎么办？** 改写成 Conv / 高阶 LayerNorm / 静态 slice，或接受这段在 CPU 并把它移出热路径。不要在热路径上「先对了再优化」。采样见 `apple-topk-sample`：固定 $k$ 比可变 nucleus 更容易留在同一张静态图里。掉出 ANE 的第一反应是查 compute unit，不是先加更大的模型。
