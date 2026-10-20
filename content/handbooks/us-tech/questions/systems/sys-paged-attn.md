---
id: sys-paged-attn
section: systems
order: 6
level: S
title: 系统：PagedAttention 块表、复制、前缀共享
quick: "KV 切成固定 token 数的块，逻辑序列经 block table 映射到不连续物理页。分配按需、结束即回收，几乎消掉外部碎片。 相同前缀用 copy-on-write 共享物理块；写时再拆页。注意力公式不变，改的是寻址。"
tags:
  - vLLM
  - NVIDIA
  - KV Cache
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: vLLM — Easy, Fast, and Cheap LLM Serving with PagedAttention
    url: https://vllm.ai/blog/2023-06-20-vllm
    type: secondary
  - title: PagedAttention — Hugging Face TGI
    url: https://huggingface.co/docs/text-generation-inference/main/conceptual/paged_attention
    type: secondary
  - title: Paged Attention, IFB, and Request Scheduling — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/paged-attention-ifb-scheduler.html
    type: secondary
---

## 题怎么来的

vLLM 的 SOSP'23 论文、Hugging Face TGI、NVIDIA TensorRT-LLM 都把 KV 做成分页。NVIDIA 岗爱问 kernel 怎么按 block table gather（实现细节见 `nvidia-paged-kv`）；OpenAI serving 爱问为什么 continuous batching 离开分页会 OOM，以及 KV 在代码里怎么长（见 `openai-kv-cache-impl`）。先把「像虚拟内存」讲清楚，再讲复制和前缀共享，别说成改了注意力公式。

## 块表：逻辑连续、物理可散

传统为每条请求预留 `max_len` 连续 KV：内部浪费（实际长度远小于预留）和外部碎片（空闲区凑不出一整段）。PagedAttention 把 cache 切成固定 token 数的 block（论文里常用 16），每条序列一份 **block table**：逻辑块号到物理块号。Attention kernel 按表去 gather K/V，再算 $QK^{\top}$ 和加权 $V$。数学不变，变的是寻址。

按需分配：逐 token 生成（decode） 每写满一块再要新页。请求结束只释放该请求的页引用；只有缓存及其他请求也不再持有、引用数降到0，页才回free list。完整生命周期与COW实现见 [[kv-prefix-paged-cow]]。这才让 `sys-cont-batch` 的「结束就补位」在显存上可行。没有分页，调度器有策略也没地方放新 KV，只能按 max length 预留，并发被碎片打死。

页大小是权衡：太小，表项和间接访问多，kernel 难向量化；太大，块内内部碎片回来，接近连续预留。实现里常见十几到几十 token 一页。TGI 直接用了 vLLM 的 CUDA kernel；TensorRT-LLM 自己做 paged KV，语义同一套。

一般不把 KV 换出到 CPU 当「缺页」。PCIe 太慢，decode 走带宽墙。分配失败通常是抢占：把某条请求的 KV 踢回 CPU 或直接暂停，不是去盘上取。类比操作系统到映射和碎片为止，别讲成真的 swap。

## 复制和前缀共享

并行采样、beam、同一 system 输入提示（prompt） 的多用户，逻辑前缀相同。block table 可以让多条序列指向同一批物理块，引用计数加一。这是共享，不是把 KV 拷一份。新 token 要写时 **copy-on-write**：先把该块复制成私有页再写，避免改到别人的前缀。

论文里的数字：naive 系统 KV 浪费可到百分之六十到八十；分页把浪费压到接近块内碎片那几个百分点，吞吐相对 Orca / FasterTransformer 常见两到四倍，长序列更明显。收益来自更高并发（同样 HBM 能多塞请求），不是单步 softmax 更快。Decode 仍是 memory-bound。

举个形状：16 token 一页、上下文 2k、实际生成 200。连续预留浪费约 1800 token 的槽；分页只多浪费最后一页里未写满的那几格。八路并行采样共享同一输入提示 前缀时，那 2k 只占一份物理页，直到各路开始写自己的 token 才 CoW 拆页。

Kernel 侧不要忽略 gather 成本：block table 在 GPU 上，按页间接访问 K/V。页太碎，L2 命中差；页太大，内部碎片回来。虚拟内存类比停在映射、不到 swap，因为 decode 走 HBM 墙，PCIe 换页会把 TPOT 打穿。

和 FlashAttention、KV 量化分层：Flash 减单步 HBM I/O；分页减分配碎片；量化让每页更窄。页里可以是 FP8 KV，算子仍按表 gather。不要说「vLLM 等于 PagedAttention」，它还叠了 continuous batching 和调度。前缀跨请求的缓存策略见 `sys-prefix-cache`。

错误说法：PagedAttention 是近似注意力；页表存在 CPU 上每步往返；没有分页也能靠把 `max_num_seqs` 开大吃满 GPU。前两个错在机制，后一个错在碎片会先 OOM。

## 追问

- **是近似 attention 吗？** 不是。$K/V$ 物理上不连续，kernel 按 block table gather 再算，数值应与连续 KV 一致。
- **块表存在哪？** 每条序列一份小表，通常在 GPU 上给 kernel 查。元数据远小于 KV 本身。
- **为什么 copy-on-write 而不是一开始复制？** 共享前缀可能几千 token。写时再拆，省的是那一段物理页，直到真正分叉。
- **和操作系统换页完全一样吗？** 映射和碎片像。生产上很少把 KV 换到 CPU；缺页是分配失败或抢占，不是去磁盘取。
- **页大小 16 是不是魔法数？** 不是。要能被 kernel tile 整除，又不能让块内碎片回到连续预留。改页大小要一起改 attention kernel。
- **CoW 和 prefix cache 是一层吗？** 不是。CoW 是页级共享原语；prefix cache 是跨请求命中策略。没有分页，前缀共享就得 memcpy。
- **Beam / 并行采样为什么特别吃分页？** 公共前缀可以共享物理页，分叉后再 CoW。连续预留会把每条 beam 的 max length 都占满。

## 相关题

- [[nvidia-paged-kv]]：几乎是同一道题的 NVIDIA 问法，多讲 block size 写成 1 会怎样和抢页失败。
- [[coding-paged-table]]：白板写 block table 和 append 的编程版。
- [[kv-prefix-paged-cow]]：把 refcount 和 CoW 完整写出来的练习，含分配失败回滚。
- [[meta-vllm]]：Meta 问法，把分页、continuous batching 和 GQA 放在一起讲。
- [[sys-prefix-cache]]：CoW 之上那一层：跨请求怎么判断前缀算不算命中。
- [[openai-continuous-batching]]：有了分页之后，每步换 batch 成员的调度那一侧。
