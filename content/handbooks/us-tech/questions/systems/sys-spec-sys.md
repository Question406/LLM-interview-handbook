---
id: sys-spec-sys
section: systems
order: 18
level: A
title: 系统：投机解码，草稿长度、拒绝回滚 KV、测吞吐
quick: "投机解码用草稿模型提 $\\gamma$ 个 token，再由目标模型并行验证，收益取决于接受长度和额外开销。拒绝后两侧 KV 都要退回接受前缀，吞吐只统计最终产出的 token，并在相同并发、长度和采样条件下比较。"
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

投机解码是否加速，要看一次验证能留下多少 token，以及草稿、验证和回滚花了多少时间。工程上我会一起调草稿长度、核对 KV 回滚，并用实际产出 token 衡量吞吐。

草稿模型 $q$ 先生成 $\gamma$ 个 token，目标模型 $p$ 用一次类似短 prefill 的并行前向给出这些位置的 logits，再从左到右接受。期望接受长度 $\alpha>1$ 才能减少 $p$ 的步数。$\gamma$ 太大，后半段常被拒，草稿和 KV 写入都浪费；太小，又摊不薄验证开销。因此看平均接受长度与每个产出 token 的 target 前向次数来调，不固定 $\gamma=5$。$\gamma=1$ 通常也摊不回验证成本。

草稿太接近 $p$ 可能本身很慢，太弱则 $\alpha\to 1$，只剩双模型开销。Medusa、EAGLE、n-gram 改变草稿来源，仍需处理草稿 decode 与验证 prefill。树状草稿一次提多分支，验证使用带 mask 的小 prefill，可能提高接受率，KV 分叉则要 CoW 或分页。叠加 continuous batching 时，各请求的 $\alpha$ 与接受长度不同，不能让每条统一 append $\gamma$ 再统一截断，见 `sys-cont-batch`。

## 先保证 KV 回滚正确

验证前向已经把草稿位置的 $K,V$ 写入 target cache。原长为 $S$，接受 $k$ 个、在 $k+1$ 拒绝，就应从 $S+\gamma$ 截回 $S+k$，再写入拒绝位置重新采样 token 的 KV；draft 侧也要截断。接受前缀有效，不必重算整段 prefill。分页下可通过归还页面实现，避免大块 `cat` 和复制，见 `sys-paged-attn`。

只改输出文本、不剪 KV，后续 $q_t$ 会读到已经被拒绝的 key，输出悄悄偏离。先用 greedy 投机路径与逐步 decode 逐 token 对齐，出错查是否漏截某层，再查 RoPE offset。无损分布的算法解释见 `openai-speculative-decoding`。

## 再看实际吞吐

吞吐统计最终产出 token / 实际耗时，要包含被拒草稿的浪费。还要看 TTFT、TPOT 与 SLO 内 goodput，投机通常很少帮助 prefill，不能把草稿 token/s 或 $\gamma$ 个验证位置都当成产出。基线与投机使用相同并发、输出长度和采样方式，高并发下草稿与验证会抢 SM、抢 KV 页，可能比单条离线测试慢，甚至出现负收益。

例如固定同一 prompt 集、输出 256 token，target-only 吞吐记为 $R_0$，投机吞吐为 $R$，平均接受长度为 $\bar{k}$。即使 $\bar{k}=2.4$，$R/R_0$ 也可能只有 1.2，差额来自草稿延迟、拒绝回滚和验证 prefill 利用不足，接受长度不能直接当加速比。

草稿同卡时间复用能减少调度，却会争用 decode 带宽；放小卡或 CPU 不抢 target 资源，但多一次同步。应先判断瓶颈是 target 前向次数还是草稿延迟，再决定部署位置。这也是 vLLM、TensorRT-LLM 与 serving 岗在算法无损性之外关心的问题。

## 追问

**$\gamma$ 越大越快吗？**
不会。超过可接受前缀后，增加的主要是被拒草稿成本，要跟着接受率调。

**能放进 PD 分离的 decode 池吗？**
要重新估资源。验证像短 prefill，不能沿用纯 decode 的带宽假设，见 `sys-prefill-decode-disagg`。

**怎么确认分布没变？**
拒绝采样的边际一致由论文给出；工程上用 greedy 路径查回滚，随机采样按种子核对，不要求逐 token 字符串一致。

**高并发为何加速变少？**
草稿与验证争用 SM、KV，各请求接受长度也不同，单条离线 $\bar{k}$ 无法直接外推 serving goodput。

**两模型要同 tokenizer 吗？**
要。接受规则需在同一个 $x$ 上比较，否则词表与回滚位置对不上。

## 相关题

- [[openai-speculative-decoding]]：拒绝后的 KV 回滚。
- [[apple-spec-edge]]：端侧回本公式和同芯片放置。
- [[google-spec-decode]]：算法无损性与 Medusa / EAGLE 的区别。
- [[nvidia-spec-medusa]]：多头草稿下的长度和吞吐。
- [[coding-spec-accept]]：接受规则实现。
