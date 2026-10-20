---
id: meta-vllm
section: meta
order: 29
level: A
title: Meta：vLLM 伺候 Llama——PagedAttention 和 continuous batching 公开怎么讲
quick: "PagedAttention 按块分配 KV，消掉按 max_len 预留的空洞；continuous batching 每步补位。GQA 只缩小每 token 的 KV，分页仍要；共享 system prompt 走 prefix cache。"
tags:
  - Meta
  - Llama
  - vLLM
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
    url: https://blog.vllm.ai/2023/06/20/vllm.html
    type: primary
  - title: vLLM documentation
    url: https://docs.vllm.ai/en/latest/
    type: secondary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: secondary
---

Llama serving 岗几乎必问 vLLM。分页和 continuous batching 的机制卡在 `sys-paged-attn`、`sys-cont-batch`。本题收 **Llama 上你要主动补的三笔账**：GQA 已经很瘦的 KV 为什么还要分页、聊天模板的 prefix cache、视觉版的 encoder 不走同一套页表。公开论文和文档够答；不要假装见过 Meta 生产集群的调度器。

## 为什么 GQA 之后还要分页

Llama 3 70B 公开是 $64$ 个 query head、$8$ 个 KV head，cache 大约是 MHA 的 $1/8$，见 `meta-llama-gqa`。这只缩小 **每个 token 的 KV 字节**，不解决 **按 `max_len` 连续预留** 的碎片。一条实际生成 $200$ token、槽位按 $8\mathrm{k}$ 开的请求，内部浪费仍是几千格。分页把 KV 切成固定 token 数的块（论文常用 $16$），逻辑序列经 block table 映射到不连续物理页。Attention 公式不变，变的是寻址。

和 Orca 配套：每个 逐 token 生成（decode） step 结束的序列立刻还页，waiting 里补人。没有分页，iteration 调度有策略也没地方放新 KV，并发被碎片打死。页太小，表项和 gather 多；太大，块内碎片回来。这是权衡，不是魔法数。

口算 70B、bf16、80 层、$8$ 个 KV head、head dim $128$：每 token 约 $2\times80\times8\times128\times2\mathrm{B}\approx 320\mathrm{KB}$。连续预留 $8\mathrm{k}$ 是约 $2.5\mathrm{GB}$ / 序列；实际生成 $200$ token 只该占约 $64\mathrm{MB}$。分页让并发吃的是「真长度之和」，不是「max_len × 批大小」。GQA 已经把宽度从 MHA 的约 $2.5\mathrm{MB}$/token 砍到 $320\mathrm{KB}$；剩下的洞是长度预留，分页才管得着。

Llama 3.1 $128\mathrm{k}$ 窗把这件事放大：几乎没有请求真用满窗，连续预留会使大量 GPU 显存用于未使用的预留槽位。分页按需长，最后一页内部碎片是唯一系统性浪费。70B / 405B 还要 TP：每张卡一份 sharded KV，页表仍按序列，不要把 TP 和 paging 说成一个开关。

## Prefix cache 和 chunked 输入预填充（prefill，即处理输入并建立缓存）

多用户同一条 system 输入提示（prompt）、同一套 Llama 3 聊天模板，前缀 KV 可以共享物理页，写时 copy-on-write。命中条件：token id、权重、LoRA、位置语义都一致。模板加一个 `begin_of_text` 或换 chat template 版本，必须从分叉处断开，见 `sys-prefix-cache`。这是 Llama 聊天服务的默认利润，不是「再开一个 cache 产品」。

长 prompt 插入 decode batch 会把 memory-bound 的 decode 打成一段巨大 prefill。工程上用 chunked prefill：长 prompt 切块，块之间仍插入 decode，见 `sys-chunked-prefill`。Llama 405B 更狠时 prefill / decode 分池，见 `sys-prefill-decode-disagg`。调度目标是 SLO 内 goodput，不是瞬时 tokens/s。`max_num_seqs` 开到 KV 爆边，P99 TPOT 先坏。

投机解码可以叠：草稿用 8B、目标用 70B，接受率高时 decode 步数下降。分页照样按目标模型的 KV 走；草稿有自己的小 cache。别说「vLLM 等于投机」，它是内存和调度，投机是上层加速。

## 视觉 Llama 不要假定同一套页表

3.2 Vision 的文本自注意力 KV 仍可分页。视觉 $K/V$ 在 cross-attn 旁路，按图、按 tile 数长，见 `meta-llama-vision`、`meta-anyres`。图不变应缓存视觉表示；用户只追加一句文本，不要重跑 ViT。vLLM 后来加了多模态，但面试要先画：**文本页表管 $T$，视觉 $N$ 另算。** 把 PagedAttention 说成「图也不占显存」，是错的。

常见误区是：PagedAttention 是近似注意力。错法二：页表在 CPU 上每步往返。错法三：没有分页只要把 `max_num_seqs` 开大。前两个错机制，后一个错在碎片先 OOM。

和 TensorRT-LLM 的 in-flight batching 是同一调度语义，见 `nvidia-inflight-batch`；和 TGI 也同源。现场报 vLLM 即可，但要承认不是 Meta 公开的唯一服务栈。量化 KV、投机、多机 TP 都可以叠在分页之上，不要说成互相替代。

## 追问

- **GQA 已经省 KV，分页还有多大头？** GQA 省的是每 token 宽度；分页省的是预留长度和并发碎片。两笔乘在一起，不是替代。
- **和 FlashAttention 什么关系？** Flash 减单步 HBM I/O；分页减分配碎片。页里可以是 FP8 KV，算子仍按表 gather，见 `sys-kv-quant`。
- **405B 一张机跑不了怎么办？** TP（再加 PP）切权重，分页切的是每卡上的 KV 池。两层正交。
- **前缀共享和 beam 是一层吗？** 都用引用计数 + CoW。Prefix cache 跨请求；beam 是同一请求内分叉。没有分页就得 memcpy。
- **多模态 serving 的 SLO 怎么定？** 拆 encoder 时延、文本 prefill、decode TPOT。图尺寸一变，encoder 先抖，不要只盯 tokens/s。

## 相关题

- [[sys-paged-attn]]：PagedAttention 块表和 CoW 的通用系统题，不绑定 Llama，也不谈多模态。
- [[nvidia-paged-kv]]：NVIDIA 问法，多讲碎片来源、block size 取舍和抢页。
- [[coding-paged-table]]：要求白板写出 block table 和 append 逻辑的编程版。
- [[openai-continuous-batching]]：把 continuous batching 单独拿出来，讲 iteration-level 调度在省什么。
- [[sys-prefix-cache]]：展开共享 system prompt 那一段：什么情况下才算命中、多用户共享有什么风险。
- [[google-gqa-mqa]]：GQA 怎么选、每 token 的 KV 省多少，是本题「GQA 之后还要分页」的前半句。
