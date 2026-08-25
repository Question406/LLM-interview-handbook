---
id: sys-radix-tree
section: systems
order: 25
level: A
title: 系统：radix / prefix tree 共享 KV（SGLang）
quick: >-
  树在 CPU，KV 页在 GPU。边存的是一段 token，不是单字符。新请求沿树找最长前缀，命中的物理页直接挂上
  block table。分叉之后才写新页。淘汰从叶子 LRU，根上的系统提示尽量留下。
tags:
  - SGLang
  - vLLM
  - KV Cache
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Fast and Expressive LLM Inference with RadixAttention and SGLang
    url: https://lmsys.org/blog/2024-01-17-sglang/
    type: primary
  - title: SGLang — Efficient Execution of Structured Language Model Programs
    url: https://arxiv.org/abs/2312.07104
    type: primary
  - title: Automatic Prefix Caching — vLLM
    url: https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html
    type: secondary
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

## 题怎么来的

多轮对话、few-shot、同一条系统提示、agent 工具模板，请求之间有长公共前缀。vLLM automatic prefix caching 用块哈希；SGLang 公开的 RadixAttention 用 radix tree（压缩前缀树）做最长前缀匹配。LMSYS 2024 博客和 SGLang 论文都把树画出来了，这不是内部黑话。NVIDIA 岗追页怎么共享；应用岗追错命中。块表原语见 `sys-paged-attn`，命中条件见 `sys-prefix-cache`。本题讲树比扁平哈希多了什么、淘汰怎么走。

## 树在 CPU，页在 GPU

我会先把两层拆开。Radix 树的边可以标一段 token，比逐 token 的 trie 浅。节点存引用计数和指向 GPU 物理页的下标。博客写明：树维护在 CPU，开销相对 GEMM 可忽略；GPU 上仍是 paged KV。$page_size \gt 1$ 时匹配对齐到页边界，余下不足一页的 token 只能当 miss 重算。

新请求带着完整 prompt 进来（前端不负责切前缀）。运行时从根走下去，找到最长已经驻留的前缀，把那些物理页填进这条请求的 block table，只对后缀做 prefill。多条请求共享同一段系统提示时，那一段 KV 只有一份，靠引用计数，不是 memcpy。某条开始生成、要写已经共享的页，必须 copy-on-write 拆页，否则会改到别人的前缀。

和 vLLM 块哈希的差别：扁平哈希擅长「整块 token 完全一致」；树天然表达部分共享和分叉——同一模板头、第三轮才分叉、工具 schema 相同后面参数不同。Agent 多轮、并行采样、beam 都是树更顺的形状。哈希也能做前缀，但大量部分命中时表项和比较次数更难看。

```python
def match_prefix(root, ids, page_size=16):
    node, i = root, 0
    n = (len(ids) // page_size) * page_size
    while i != n:
        child = node.children.get(ids[i])
        if child is None:
            break
        seg = child.edge  # 一段 token，不是单点
        L = len(seg)
        if ids[i : i + L] != list(seg):
            break
        i += L
        node = child
    return i, node.pages  # 命中长度、已有物理页
```

Cache key 不能只有 token。SGLang 源码里 `extra_key` 把 LoRA、adapter、故意不共享的命名空间拆开：token 相同但 `extra_key` 不同，不得走同一条边。这和 `sys-prefix-cache` 的错命中纪律一致。

## 淘汰、调度、和分页的关系

HBM 有限，树不能无限长。公开策略是 LRU，并且先踢叶子：踢叶子不拆掉还被很多人引用的主干。系统提示在根附近，命中频繁，会留下；一小时前某条对话的尾巴先走。这和「按页 LRU、不管树结构」不同：乱踢中间节点会把整棵子树变孤儿，命中率假高、实际全 miss。

Cache-aware 调度：尽量把共享同一前缀的请求排在一起，提高本步树命中，也让 FlashInfer cascade 那种「公共 KV + 私有 KV」更值钱，见 `sys-flashinfer`。只追瞬时 tokens/s、乱序插请求，会把主干的引用计数抖动打乱。

没有分页，树只能指向连续 buffer，分叉就要拷整段前缀。Radix 是索引；PagedAttention 是物理页。两层一起才有零拷贝共享。结束的请求不要立刻把 KV 丢掉：生成结果也可以插回树，下一轮用户消息才能命中「系统提示 + 上一轮问答」。这正是 agent 流量的形状，见 `sys-agent-sched`。

风险：热点主干占满 KV 池，挤掉在飞 decode，hit rate 很好、P99 TPOT 很差。要限制单前缀占比，并和在飞页分池或设水位。跨机 replica 没有同一棵树，要亲和，或接受 miss。多租户：用户文档默认不要跨租户命中；公共系统提示可以共享。

错误说法：RadixAttention 改了注意力公式（数值应与按页 gather 的精确注意力一致）；树存在 GPU 上每步被核遍历；和 PagedAttention 二选一。树是 CPU 索引，核仍然按 block table 读页。

## 追问

- **和 vLLM prefix cache 怎么选？** 大量部分共享、多轮、分叉，树更合适。几乎总是整段系统提示完全相同、分叉少，块哈希够用。
- **改一个空格？** 从第一个不同 token 断开。若整段仍命中，key 没含 token ID 或 template 版本。
- **为什么淘汰叶子？** 叶子是私有后缀；中间节点是共享主干。先踢叶子保留系统提示。
- **page_size 和匹配粒度？** 匹配按页对齐。页太大，短分叉也要重算一截；页太小，树更深、核间接访问更多。
- **生成结果为什么也要插入？** 下一轮 prompt 是旧上下文加新用户句。不插生成段，多轮第一次就会从分叉处全量 prefill。
- **LoRA 能共享主干吗？** 一般不能。`extra_key` 必须分开，否则 silent 错命中。
