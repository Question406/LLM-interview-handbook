---
id: kv-prefix-implementation-index
section: systems
order: 1
level: S
title: KV Prefix 实现专题：8 道完整题，从 Transformer 到 Radix Cache
quick: >-
  这组题从 cached / uncached 数值对齐开始，依次练 radix、pin / evict、分页 COW、块哈希和分段
  attention，最后接成少算前缀的循环。每题都有完整代码与测试，可按数值、数据结构或小项目路线练习。
tags:
  - 备考地图
  - KV Prefix 实现专题
  - KV Cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: SGLang radix cache implementation
    url: >-
      https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py
    type: primary
  - title: vLLM prefix caching design
    url: 'https://docs.vllm.ai/en/latest/design/prefix_caching/'
    type: primary
---

## 这组题要真正写出来的路径

按这张表从数值正确性练到完整推理循环：先算好并保存前缀的每层 K/V，新请求找到语义一致的公共 token 前缀后挂上 cache，只计算后缀。最后要检查 forward 的实际计算量，确认树命中确实减少了计算。

| 顺序 | 题目 | 关键验收 |
|---|---|---|
| 1 | [[kv-prefix-transformer|KV Prefix ①：多层 Transformer 的 prefill、decode 与前缀分叉]] | 实际写出每层 K/V 的复用路径，带 RoPE、GQA、残差和 gating MLP；验证整段重算、逐 token decode、分块 prefill 的 logits 一致。 |
| 2 | [[kv-prefix-radix|KV Prefix ②：手写 Radix Tree——插入、边分裂与任意前缀命中]] | 边存 token 段及对应 KV 句柄；查询即使在压缩边中途结束或分歧，也应返回已计算的公共部分，不能只匹配终止节点。 |
| 3 | [[kv-prefix-radix-leases|KV Prefix ③：Radix Cache 的 pin/unpin、活跃分裂与叶子 LRU]] | 运行中请求保护整条祖先路径；边分裂时新父节点继承引用数，旧 lease 释放时沿当前 parent 链回退，避免提前淘汰或引用泄漏。 |
| 4 | [[kv-prefix-paged-cow|KV Prefix ④：共享 KV 页的引用计数与 Copy-on-Write]] | 多个请求共享同一物理前缀页；写共享的未满尾页才复制，写满页后的新 token 直接分配新页。OOM 前先保留原页表与引用数。 |
| 5 | [[kv-prefix-block-hash|KV Prefix ⑤：链式块哈希、缓存上下文与碰撞防护]] | 块身份包含祖先哈希、当前 token 和完整上下文；同一个后缀块处在不同前缀下不能互相命中，模型、adapter、租户或位置语义改变也必须 miss。 |
| 6 | [[kv-prefix-segmented-attention|KV Prefix ⑥：共享 Prefix + 私有 Suffix 的分段 Attention]] | 不先 concat 公共前缀，不物化重复 KV heads：分别读共享 prefix 和各请求 suffix，用在线 max、指数和及输出累计量合并为同一个 softmax。 |
| 7 | [[kv-prefix-reuse-plan|KV Prefix ⑦：页对齐命中、完整命中与 Chunked Prefill 计划]] | 逻辑命中长度还要按完整页取整；如果只缓存 KV、没有末 token logits，完整命中时也要重放末 token，页级复用可能需要重放整尾页。 |
| 8 | [[kv-prefix-engine|KV Prefix ⑧：把 Radix Tree 接进 Transformer——可运行 Prefix Engine]] | 真正执行“查前缀 → 恢复每层 KV → 只算后缀 → greedy decode → 把新 KV 插回树”，对比 cold run 的 token、每层 KV 与少算的 prefill token 数。 |

## 三条练习路线

- 想先验证 Transformer 数值，可以走 ① → ⑦ → ⑥ → ⑧，重点核对 RoPE offset、矩形因果 mask、完整命中时的末 logits 和 chunk boundaries。
- 想先练缓存数据结构，可以走 ② → ③ → ④ → ⑤，重点核对边中途命中、活跃节点分裂、重复句柄，以及 COW 失败时是否保留原状态。
- 想做完整小项目，先跑⑧的 cold/warm 对照，再把连续 cache 恢复换成④的页池，并接上⑥的分段读取。最后的零拷贝集成是扩展作业，当前⑧仍会显式复制数组。

## 先分清几个不同的“引用”

树的 lease 保护索引祖先，防止活跃路径被淘汰；物理页 refcount 保护页不被回收或原位写坏，两者需要分别计数。缓存自己持有的页也占一份引用，因此请求结束只释放请求那一份，页不一定立刻 free。

Token 粒度 radix 树可命中压缩边内部，完整页哈希通常只复用整页。拿到逻辑命中长度后，仍要按所用物理格式对齐。

这组题都标为手册原创练习，不将它们算作新增真实面经。

## 相关题

- [[sys-prefix-cache]]：前缀缓存的口述系统题，适合先建立命中条件的概念再来写代码。
- [[sys-radix-tree]]：SGLang radix tree 的口述版，对应这里的第②③题。
- [[p3a-xai-radix-cache]]：xAI 面经里的 radix tree 编程题，查询只认终结节点，契约和第②题不同。
