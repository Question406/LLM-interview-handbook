---
id: sys-spec-sys
section: systems
order: 18
level: A
title: 系统：投机解码，草稿长度、拒绝回滚 KV、测吞吐
quick: "小模型一次提 $\\gamma$ 个 token，大模型一次前向验证。加速比看接受长度，不是看草稿跑得多快。拒绝后必须把 target（和 draft）的 KV 截回接受前缀，否则后续注意力盯幽灵 token。测的是产出 token/s 和 SLO，不要把拒绝草稿算进吞吐。"
tags:
  - vLLM
  - Serving
  - Speculative Decoding
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Fast Inference from Transformers via Speculative Decoding
    url: https://arxiv.org/abs/2211.17192
    type: primary
  - title: Accelerating Large Language Model Decoding with Speculative Sampling
    url: https://arxiv.org/abs/2302.01318
    type: primary
  - title: Speculative Decoding — vLLM
    url: https://docs.vllm.ai/en/latest/features/spec_decode.html
    type: secondary
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

## 题怎么来的

vLLM / TensorRT-LLM 的投机解码、OpenAI serving 在 KV 之后的追问，都落到系统而不是证明「分布不变」。回滚为什么必须做，正确性那一层见 `openai-speculative-decoding`。本题答三件工程：$\gamma$ 怎么选、拒绝时 KV 怎么剪、墙上吞吐怎么测才不自欺。

分页 KV 上拒绝等于还页，见 `sys-paged-attn`。测吞吐时把拒绝草稿算进去，数字会虚高。

## 草稿长度是在赌接受率

草稿模型 $q$ 生成 $\gamma$ 个 token，目标 $p$ 一次平行前向（短 输入预填充（prefill，即处理输入并建立缓存））给出这 $\gamma$ 个位置的 logits，再从左到右接受。期望接受长度 $\alpha>1$ 才省 $p$ 的步数。$\gamma$ 太大：后面几个几乎必拒，白算草稿、白写一段 KV 再 rollback。$\gamma$ 太小：一次验证摊不回。现场用平均接受长度和「每产出 token 的 target 前向次数」调，别锁死 $\gamma=5$。

草稿太强或太弱都亏：太接近 $p$ 则草稿本身慢；太弱则 $\alpha\to 1$，系统退化成双模型开销。Medusa / EAGLE / n-gram 换的是草稿来源，调度不变量不变：验证步是 compute-bound 的小 prefill，草稿步仍是 逐 token 生成（decode）。和 continuous batching 叠时，各请求 $\alpha$ 不同，不能假设 batch 里每条都 append $\gamma$ 再一起 truncate，见 `sys-cont-batch`。

树状草稿一次提多条分支，验证更像一小段带 mask 的 prefill，接受率可能更高，KV 分叉要 copy-on-write 或分页，见 `sys-paged-attn`。不要把树和 $\gamma$ 说成两个算法家族；都是「先写后证，证完再剪」。

## 拒绝就是剪 KV 指针

验证前向已经把草稿位置的 $K,V$ 写进 target cache。接受 $k$ 个、在 $k+1$ 拒绝，序列里没有第 $k+1$ 个草稿 token，但它的 KV 已在末尾。必须把 cache 从 $S+\gamma$ 截回 $S+k$，再写入拒绝处新采样 token 的 KV。草稿侧同样截。文本长度和 KV 长度必须焊死。PagedAttention 上这就是还页，不是大块 `cat` 再拷。

只改输出字符串、不剪 cache，后面每一步 $q_t$ 都会点积到幽灵 key，生成会在不明显报错的情况下偏离。这是正确性，跟加速比无关。验收：greedy 投机路径和逐步 decode 逐 token 相同。对不上先查有没有漏层没截，再查 RoPE offset。

## 吞吐不要把垃圾算进去

合法指标：产出 token / 实际耗时（含拒绝浪费）、首个 token 的等待时间（TTFT）（投机几乎不帮 prefill）、TPOT / SLO 内 goodput。不要报「草稿 token/s」，也不要把 $\gamma$ 次验证 FLOPs 当成 $\gamma$ 个产出 token。对比基线必须同一并发、同一输出长度、同一采样。高并发时草稿和验证抢 SM、抢 KV 页，加速比会比单条 offline 差一截；有的负载上投机是负优化。

草稿放哪：同卡时间复用省调度、抢 decode 带宽；旁路小卡或 CPU 草稿不抢 target，但多一次同步。面试说清瓶颈在 target 前向次数还是在草稿延迟，再选放置。

一个测法：固定输出 256 token、同一输入提示 集。基线 target-only tokens/s 为 $R_0$。投机跑完看产出 token/s $R$，以及平均接受长度 $\bar{k}$。若 $\bar{k}=2.4$ 但 $R/R_0$ 只有 1.2，差额就是草稿延迟、拒绝回滚、验证 prefill 没喂饱。不要把 $\bar{k}$ 直接当加速比。

## 追问

- **$\gamma$ 越大越快吗？** 不是。超过平均可接受前缀就在增加被拒草稿的开销。跟接受率走。
- **拒绝后要不要重算整段 prefill？** 不要。接受前缀的 KV 合法，只丢拒绝点及其后。
- **和 PD 分离怎么叠？** 验证步像短 prefill，别塞进纯 decode 池的带宽假设，见 `sys-prefill-decode-disagg`。
- **怎样证明没变分布？** 论文保证拒绝采样后边际相同。工程上用 greedy 对齐查 rollback；随机采样对种子，不对逐 token 字符串。
- **高并发加速比为什么掉？** 草稿和验证抢 SM、抢 KV 页，各请求接受长度还不同。offline 单条的 $\bar{k}$ 不能外推到 serving goodput。
- **草稿和 target 必须同 tokenizer 吗？** 必须。接受规则要在同一个 $x$ 上比。词表不一致，rollback 也对不齐。

- **$\gamma=1$ 还有意义吗？** 退化成每步验证一个草稿，摊不回验证 prefill。$\gamma$ 至少要让平均接受长度明显大于 1。

## 相关题

- [[openai-speculative-decoding]]：只问拒绝时为什么要回滚 KV，和本卡「拒绝就是剪 KV 指针」一节大半重叠。
- [[apple-spec-edge]]：端侧场景：回本公式，以及草稿为什么要和目标放在同一块芯片上。
- [[google-spec-decode]]：算法侧的无损性和 Medusa / EAGLE 的区别。
- [[nvidia-spec-medusa]]：草稿换成多头之后，$\gamma$ 和吞吐的测法不变。
- [[coding-spec-accept]]：接受规则的代码实现，平均接受长度就是从这一步来的。
