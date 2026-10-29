---
id: nvidia-cuda-graph
section: nvidia
order: 16
level: A
title: NVIDIA：CUDA Graph 在 decode 上的收益和动态 shape 限制
quick: >-
  CUDA Graph 把 decode 的短核和依赖录成一次提交，replay 时减少 CPU launch 间隙，小
  batch、低延迟请求收益更明显。我会按真实 batch 分布捕获几档图，匹配不上就 padding 或 eager；同时预分配 KV 和
  workspace，避免地址、形状变化让图失效。
tags:
  - NVIDIA
  - CUDA Graph
  - Decode
  - TensorRT-LLM
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: CUDA C++ Programming Guide — CUDA Graphs
    url: >-
      https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#cuda-graphs
    type: primary
  - title: Tuning CUDA Graph Batch Sizes for Higher Output Throughput — TensorRT-LLM
    url: >-
      https://nvidia.github.io/TensorRT-LLM/latest/blogs/tech_blog/blog20_Tuning_CUDA_Graph_Batch_Sizes_for_Higher_Output_Throughput.html
    type: secondary
  - title: Torch Compile and Piecewise CUDA Graph — TensorRT-LLM
    url: >-
      https://nvidia.github.io/TensorRT-LLM/latest/features/torch_compile_and_piecewise_cuda_graph.html
    type: primary
  - title: >-
      NVIDIA TensorRT-LLM Supercharges Large Language Model Inference on NVIDIA
      H100 GPUs
    url: >-
      https://developer.nvidia.com/blog/nvidia-tensorrt-llm-supercharges-large-language-model-inference-on-nvidia-h100-gpus/
    type: secondary
---

## 可以这样回答

CUDA Graph 能把 decode 的一串短核合成一次提交，减少 CPU launch 造成的空隙。例如一步有 40 个核、每次 launch 用 $5\,\mu\mathrm{s}$，host 开销就有 $0.2\,\mathrm{ms}$。它适合形状和地址稳定的路径；TensorRT-LLM 文档中主要给 decode 建图，prefill 的形状依赖输入长度，很难用一张图覆盖。

Prefill：$T$ 大，一次 GEMM / FMHA 就能把 GPU 喂饱，launch 几个微秒可以忽略。

## 技术备查

CUDA Graph 能把 decode 的一串短核合成一次提交，减少 CPU launch 造成的空隙。例如一步有 40 个核、每次 launch 用 $5\,\mu\mathrm{s}$，host 开销就有 $0.2\,\mathrm{ms}$。它适合形状和地址稳定的路径；TensorRT-LLM 文档中主要给 decode 建图，prefill 的形状依赖输入长度，很难用一张图覆盖。

## 什么时候能省下明显的延迟

Prefill：$T$ 大，一次 GEMM / FMHA 就能把 GPU 喂饱，launch 几个微秒可以忽略。

Decode：每条序列 $Q$ 是 $[B, 1, D]$。一层里仍是 QKV GEMM、attention（读整段 KV）、输出投影、MLP。核很多，每个都短。HBM 墙在读 KV，见 `nvidia-flash-attn`；但即便核本身是带宽墙，CPU 排队 launch、每个核前的间隙加起来可以和 GPU 工作同一个数量级，尤其 $B$ 小、TPOT 指标紧的时候。Graph 把这串核和它们的依赖录成一次提交，replay 时 GPU 自己往下走。

沿用上面的估算，70B 在 $B=8$ 时一步 GPU 工作也可能只有一两毫秒，$0.2\,\mathrm{ms}$ 就不可忽略。$B$ 很大、GEMM 已经很长时，graph 的相对收益会下降，所以重点看小 batch 和低延迟 decode。

这里要区分两类瓶颈。Decode 网格太小时，split-K / FlashDecoding 用来填满 SM；CUDA Graph 减少核之间的 CPU 间隙。即使把 occupancy 从 40% 调到 70%，launch 间隙仍可能存在，见 `nvidia-occupancy`。我会在 Nsight Systems 看 launch 间隙，在 Nsight Compute 看核内的算力或带宽瓶颈。

## 动态 shape 卡在哪

CUDA Graph 捕获的是：核的 launch 配置、固定（或更新受限）的内核参数、以及当时的设备指针。下一步如果 $B$ 变了、某个 tensor 重新 malloc 了、控制流走了另一条，这张图就不能用。LLM 正好两处在动：

1. **In-flight 的瞬时 batch。** 每步进出请求，$B$ 不是常数，见 `nvidia-inflight-batch`。
2. **KV 长度 $T$。** 每步加一格。Attention 的 grid、block table、有效长度都在变。Paged KV 让容量池的基址可以稳住，但「这一步 gather 哪些页」仍是动态的，见 `nvidia-paged-kv`。

TensorRT-LLM 会在运行前按一组 `batch_sizes` 分别捕获 decode 图（文档提醒每张图可能到一两百 MB 额外显存）。padding 打开时，真实 $B$ pad 到下一个已捕获尺寸，空槽浪费算力。默认若按 2 的幂跳，高并发区间相邻尺寸能差到几百，padding 的浪费很大；官方后来把默认间隔收紧。因此图只能覆盖离散的 batch 档位，IFB 的 $B$ 对不上时就 pad 或退回 eager。

Prefill / 混合步：token 数随 prompt 变，一张图罩不住。Piecewise CUDA Graph 把 attention 留在 eager（变长、paged、MLA 分支），前后 GEMM 分段捕获；attention 写成 in-place，输出缓冲由 graph 段预分配，指针才稳。动态维只放行 `num_tokens`。这承认了动态部分的限制，并非整模型都能进入图。Chunked prefill 的混合步更是如此，见 `nvidia-chunked-prefill`。

形状变化后切换档位或回到 eager，不要每步 recapture。捕获要先跑一遍路径，成本远高于 replay。

Graph 也可以在 replay 前更新 kernel 参数和部分指针，但 launch 维和拓扑必须还是捕获时那套。Decode 把 KV 写进预分配的 paged 池，基址不变，才能 replay；一旦 `malloc` 出新缓冲，图就废了。所以 serving 要先把 KV 池和 workspace 一次留够。Nsight Systems 上若仍看到每步一串短核，就是没走 graph，或 IFB 把 $B$ 打出了桶。

## 追问

**Padding 到 `max_batch_size` 一张图行不行？**
行，捕获简单，空槽在小流量时把带宽和算力都浪费掉。要用真实 $B$ 分布选桶。

**sampling / 停词能进图吗？**
数据相关分支（EOS、ragged 写出）常把图打断。很多实现 graph 打到 logits 为止，sampling 留 host 或单独核。

**和 `torch.compile` 一起？**
TRT-LLM 的引擎路径不要外包一层 compile。PyTorch 运行时那条才用 piecewise + compile。两条编译器叠在一起会抢图。

**动态 shape 的 TensorRT profile 能替代 graph 吗？**
Profile 让引擎接受一段形状范围，仍是多次 launch。Graph 是 launch 合并。两者正交，profile 不取消「$B$ 必须落在已捕获桶里」。
