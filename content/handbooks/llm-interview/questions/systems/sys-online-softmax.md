---
id: sys-online-softmax
section: systems
order: 18
level: S
title: FlashAttention 的 Online Softmax 怎么在分块后仍保持精确？
quick: >-
  每一行维护当前最大值 $m$ 和归一化和 $\ell$。读到新 block 后更新 $m'=\max(m,m_{\mathrm{block}})$，并把旧分子/分母按
  $\exp(m-m')$ 重标定，再累加新 block；因此无需 materialize 全部 attention matrix。
tags:
  - FlashAttention
  - Softmax
  - 真实面经
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: 2025 美团大模型面经
    url: 'https://www.nowcoder.com/feed/main/detail/b87b9794a2114f7c818b40a3be51c4f0'
    type: legacy-reference
  - title: FlashAttention
    url: 'https://arxiv.org/abs/2205.14135'
    type: legacy-reference
---

陷阱是把 FlashAttention 说成「近似 attention」或「丢精度换速度」。目标仍是

$$
\mathrm{softmax}(QK^\top/\sqrt{d})\,V,
$$

只是不把 $N\times N$ 的 score / 概率写回 HBM。普通实现的瓶颈经常是这次往返，不是 FLOPs。分块后若各自做完 softmax 再平均，**数学上就错了**，因为 softmax 的分母是整行 $\sum_j e^{s_j}$。Online softmax 用一组递推，让分块结果与整行一次算完代数等价。

## 1. 每行维护三个量

对 $Q$ 的一行，扫过已处理的 K/V 块后保存：

- $m$：目前见过的 score 最大值（含 scale 后的 $s=qk^\top/\sqrt{d}$）
- $\ell$：$\sum e^{s-m}$，即按当前 $m$ 标定后的归一化和
- $O$：尚未除 $\ell$ 的加权值，也就是 $\sum e^{s-m}v$

初始化：$m=-\infty$，$\ell=0$，$O=0$。

## 2. 读入新 block 时的更新

设新块 scores 为 $S$，该块行最大为 $m_b=\mathrm{rowmax}(S)$，对应 $V$ 块为 $V_b$。先对齐最大值，再同时改分母和分子：

$$
\begin{aligned}
m' &= \max(m,\, m_b),\\
\ell' &= e^{m-m'}\,\ell + \mathrm{rowsum}\big(e^{S-m'}\big),\\
O' &= e^{m-m'}\,O + e^{S-m'}\,V_b.
\end{aligned}
$$

$e^{m-m'}$ 是旧统计量的重标定：若新块没有更大的 max，它为 $1$；若新块更大，旧的 $\ell$ 与 $O$ 一起缩小，避免溢出，并与新的 $\exp(\cdot-m')$ 处在同一标度。全部块结束后

$$
\mathrm{output} = O \oslash \ell,
$$

按行除。这与先拼出整行 $S$ 再 softmax 再乘 $V$ 相同，只是从未物化整张 $N\times N$ 矩阵。

数值上，先减 max 再 $\exp$ 与标准稳定 softmax 同一技巧；$m$ 单调不减，递推不引入额外近似（忽略浮点舍入）。FlashAttention-2 把 $O$ 的 rescale 和最后一次除法的次序略作重排，方便 SRAM 里向量化，**代数目标不变**。

两块数值：$s=(1,2)$ 与 $s=(3,0)$。第一块后 $m=2$，$\ell=e^{-1}+1$，$O$ 按 $e^{s-2}v$ 累加。第二块 $m_b=3$，$m'=3$，旧 $\ell,O$ 乘 $e^{2-3}=e^{-1}$，再加入 $e^{s-3}$。最终 $\ell$ 等于 $e^{1-3}+e^{2-3}+e^{0}+e^{-3}$，与整行一次减 $3$ 相同。

## 3. 和「为什么快」的关系

SRAM 里完成 $Q$ 块 $\times$ $K$ 块、$P$ 块 $\times$ $V$ 块，HBM 只进 $Q,K,V$ 和出 $O$。复杂度从写 $O(N^2)$ score 降到 $O(N)$ 输出加分块往返。Causal mask 在块内做；padding 用 $m$ 的初值吃掉。面试若被追「和 xformers memory-efficient attention 什么关系」：都是 online softmax + tiling，FlashAttention 把 IO 分析和反向也写进同一套 kernel。

## 追问

- **为什么不能对每个 block 先 softmax 再加权平均？** 各块自己的分母不同；平均概率不是整行 softmax。必须按全局 $m$ 重标定后再加 $\ell$ 与 $O$。
- **$m$ 为什么必须是 running max 而不能随便固定？** 固定过小会 $\exp$ 溢出；固定过大则全下溢成 $0$。Running max 既稳定又与最终 softmax 等价。
- **反向要存什么？** 不必存 $N\times N$ 的 $P$。用输出 $O$、行统计和再读一遍 $K,V$ 重算块内 softmax，用重算换 HBM。这是 FlashAttention 省显存的另一半。
