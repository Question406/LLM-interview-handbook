---
id: meta-pack-seq
section: meta
order: 22
level: A
title: Meta：sample packing、文档边界、attention mask 的坑
quick: "Packing 把短文档拼满 $T$，能减少 padding，但普通因果 mask 会让后面的文档读到前面的内容。需要隔离的训练用块对角 mask 或 FlashAttention `cu_seqlens`，并把每篇 `position_ids` 从 $0$ 重置；EOS 和 completion-only loss 都不能替代注意力隔离。"
tags:
  - Meta
  - Llama
  - Packing
  - Attention Mask
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Efficient Sequence Packing without Cross-contamination
    url: https://arxiv.org/abs/2107.02027
    type: primary
  - title: Hugging Face — packing with FlashAttention-2
    url: https://huggingface.co/blog/packing-with-fa2
    type: secondary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: secondary
  - title: FlashAttention-2
    url: https://arxiv.org/abs/2307.08691
    type: primary
---

Packing 把多篇短文档拼成一条，减少 padding 浪费；要避免串话，就同时处理注意力边界和位置。比如指令 A 与指令 B 拼在一起，普通因果 mask 会让 B 看到 A 的答案，SFT 就发生了泄漏。文档长度呈长尾时，直接 pad 到 $8\mathrm{k}$ / $128\mathrm{k}$ 可能让一半 FLOPs 花在 pad 上，长窗阶段 $T$ 越大，浪费越明显。

## 拼什么，mask 什么

一条 packed 样本：$\mathrm{doc}_1 \oplus \mathrm{eos} \oplus \mathrm{doc}_2 \oplus \cdots$，长度顶到 $T$。默认下三角因果 mask 里，后一篇的每个 token 都能看见前面所有篇。预训练有人把这当成「就是一条长网页」，监督微调（SFT） 里这是串话：指令 A 的答案泄漏给指令 B。

需要隔离时可以这样实现：

1. **块对角因果 mask。** 每篇内部下三角，篇与篇之间 $-\infty$。实现朴素时要物化 $[T,T]$ mask，长窗上这张表自己就炸。
2. **变长 FlashAttention。** 把真实 token 展成一维，传 `cu_seqlens = [0, n1, n1+n2, ...]`。kernel 按段算，不物化 mask，也不打 pad。这是现在的默认。Hugging Face 的 flattening collator 走的就是这条。

注意力 mask 控制能读到什么，loss mask 控制哪些 token 参与训练，两者独立。SFT 只在 assistant token 上计算交叉熵损失（CE），pad、输入提示（prompt）和文档缝上的 next-token 不计入；但如果注意力没有隔开，梯度仍会经过邻居文档。

EOS 当分隔符不够。模型可以学会「EOS 后面是新篇」，仍然在 softmax 里看见上一篇的 key。分隔符只是数据约定，隔离要靠 mask。

## 位置、吞吐和训练假设怎么对齐

Naive `position_ids = arange(T)` 会让第二篇从位置 $3000$ 起。RoPE 低频会把「篇首」当成「上下文很深」。每篇应从 $0$ 重置，和 unpacked 时每条样本从 $0$ 起一致。Llama 3 提高 `rope_theta`、长窗 CPT（`meta-yarn-ntk`）解决的是外推；packing 重置解决的是**样本内相对位置**。两件事叠：重置错了，长窗 RoPE 再正确也在学错误的段首相位。

Decode 没有 packing 问题；训练 pack 了、推理一条一条，分布要靠 mask 对齐。若训练允许跨文档 attend、推理没有，那是训练/推理不一致。

GQA 的 KV 仍按真实段长写。变长 kernel 里 $K,V$ 是 packed 一维 + `cu_seqlens`，不要先 pad 再 repeat KV（`meta-gqa-kernel`）。

预训练有些配方会有意允许跨文档注意力，把 packed 序列当成长流，以换取简单实现和更高 MFU。这是数据假设，需要明确记录。Llama 3 论文没有完整展开 packing 实现，因此这里不推断具体配置；改 mask 策略后，要重新检查短评测是否恢复、长窗 haystack 是否通过。

SFT / 直接偏好优化（DPO）：默认隔离。一条 packed 行里两个 user 串话，等于把别人的系统提示当自己的。completion-only loss 救不了注意力泄漏。

吞吐：packing 提高的是有效 token / 秒；collator 把 $N$ 条拼成 $1$ 条时 optimizer step 变少，要用 token 预算对齐实验。FlashAttention 变长路径对长度方差大的数据收益最大；大家差不多都是 $T$ 时，packing 几乎没好处。

动态 $T$ 会影响 `torch.compile`。Packing 后每步 `cu_seqlens` 不同，容易触发 recompile，可以按长度分组，或只 compile block，把变长注意力留在外面，见 `meta-pytorch-compile`。

相关：`meta-llama3-pretrain`。

## 追问

**跨文档attend一定有害吗？**
预训练不一定。SFT 上几乎一定有害。改策略要在短任务和指令跟随上看回归，不要只看 MFU。
**只重置 position、不改 mask 行不行？**
位置对了，注意力仍串。两件都要做。
**文档比 $T$ 还长？**
切块。块之间若不许跨块 attend，长依赖就学不到，长窗阶段会假过关。切块策略和 128k CPT 是同一类题。
**和序列并行冲突吗？**
先 pack 再按 $T$ 切给序列并行。切点落在文档中间可以，只要全局 mask / `cu_seqlens` 仍按文档边界建。见 `sys-seq-parallel`。

## 相关题

- [[coding-packed-lm]]：本题的白板编码版，要真写出 `cu_seqlens` 前缀和与块对角因果 mask，并带单测。
- [[coding-attn-mask]]：把文档边界、因果和 padding 合成一张加性 bias 的编码题。
- [[openai-long-ctx-train]]：OpenAI 问长上下文续训时也会问到 packing，那边重点是 RoPE 基频和续训数据。
- [[sys-eos-mask]]：后训练把多条回答拼在一起时，除了注意力，loss mask 也要按 EOS 切断。
