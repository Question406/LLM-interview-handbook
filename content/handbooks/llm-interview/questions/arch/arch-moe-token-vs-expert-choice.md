---
id: arch-moe-token-vs-expert-choice
section: arch
order: 23
level: A
title: Token-choice 和 Expert-choice 路由怎么实现？各自保证什么、牺牲什么？
quick: >-
  Token-choice 是每个 token 沿专家维取 Top-$k$，保证每个 token 都有 $k$
  个专家，负载却可能不均；Expert-choice 是每个专家沿 token 维取 Top-$C$，负载固定，但冷门 token 可能没人选。生产 LLM
  多用 token-choice，再靠均衡和 capacity 管热点。
tags:
  - MoE
  - Router
  - Expert Choice
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Mixture-of-Experts with Expert Choice Routing
    url: 'https://arxiv.org/abs/2202.09368'
    type: primary
  - title: Switch Transformers
    url: 'https://arxiv.org/abs/2101.03961'
    type: primary
---

两种路由用的是同一张分数矩阵，区别在 `topk` 沿哪一维取：token-choice 是每个 token 挑 Top-$k$ 个专家，保证每个 token 都有专家，负载不保证；expert-choice 是每个专家挑 Top-$C$ 个 token，保证负载是平的，但有的 token 可能一个专家都分不到。它们保证的不变量正好相反，所以 permute、capacity 和「没被选中的 token 怎么办」都要跟着改。

GShard、Switch、Mixtral、DeepSeek 都是 token-choice，Expert Choice 是另一张分配表。光说「同一个 `topk` 换了个维度」就漏掉了这些后果。

## Token-choice：token 挑专家

对分数矩阵 $S\in\mathbb{R}^{T\times N}$（softmax 或 sigmoid 亲和），每个 token 沿专家维取 Top-$k$：

$$
\mathcal{E}(t)=\mathrm{TopK}(S_{t,:},k).
$$

它保证每个 token 恰好有 $k$ 个专家（先不算后面的 capacity 截断），负载却不在保证范围里：热点专家可以接到 $\gg kT/N$ 个 token。所以才需要 aux、bias、capacity、drop 这些手段，见 `arch-moe-balance`、`sys-moe-capacity-token-drop`。Dispatch 的 key 是 `(token, expert)` 对，按 expert id 排序后做 grouped GEMM，见 `code-moe-permute-combine`。

Capacity 是事后补丁：专家 $i$ 只留分数最高的 $C$ 个 token，多出来的 drop 或改派。被 drop 的 token 这一层等于没走 MoE，和「每个 token 都有专家」这个保证已经冲突了。

## Expert-choice：专家挑 token

同一张 $S$，每个专家沿 token 维取 Top-$C$：

$$
\mathcal{T}(i)=\mathrm{TopC}(S_{:,i},C),\qquad C\approx \frac{kT}{N}.
$$

它保证每个专家恰好 $C$ 个 token（$T$ 不够时取 $\min(C,T)$）。负载直方图是平的，aux 就不再是主要的均衡手段，all-to-all 的消息长度也能提前知道。代价落在 token 这一侧：热门 token 被很多专家选中，等效 $k_{\mathrm{eff}}\gt k$；冷门 token 的 $k_{\mathrm{eff}}=0$，这一层只剩 residual / shared。

实现上，permute 的主键变成「每个 expert 一段固定长度 $C$」，padding 少，很适合静态 shape。但 $k_{\mathrm{eff}}=0$ 要显式处理：输出置零、走 residual，或者再做一次 token-choice，补上模型容易失败的那些任务。所以别说 expert-choice「没有 drop」，它丢的是 token 的专家覆盖，专家容量这一侧不会溢出。

$C$ 的取法和 token-choice 的 capacity 同源，$C=\mathrm{CF}\cdot kT/N$。$\mathrm{CF}=1$ 时平均每个 token 仍被大约 $k$ 个专家覆盖，只是不再逐个 token 保证。

## 怎么选

要每个 token 的表达力都均匀，比如生成、对齐、RL 都怕个别 token 在这一层空转，就用 token-choice，再拿均衡和 capacity 管热点。要系统 shape 固定、杜绝热点卡，又能接受长尾 token 分到的专家少，就用 expert-choice。先 expert-choice、再给 $k_{\mathrm{eff}}=0$ 的 token 补一次路由，是一种工程折中，论文里并不默认这么做。

开源的生产 LLM（Mixtral、DeepSeek-V3）走 token-choice，因为 decoding 质量对「这个 token 有没有专家」比对「这个专家满不满」更敏感。Expert-choice 更常出现在编码器、检索、训练 throughput 优先的设定里。

## 追问

**`topk` 写在哪一维？**
Token-choice 是 `S.topk(k, dim=-1)`，Expert-choice 是 `S.topk(C, dim=0)`。写反了，保证的不变量也就反了。

**Expert-choice 还要不要 aux？**
负载已经锁住了，不用再惩罚 $f_i$。仍可以加 z-loss 压 logits，见 `arch-moe-z-loss`。

**和 shared expert 怎么配合？**
Shared expert 给 $k_{\mathrm{eff}}=0$ 的 token fallback，expert-choice 更依赖这一套，见 `arch-shared-expert`。

**RL 为什么更怕 expert-choice？**
策略一变，同一位置的 token 可能突然没人要，$\log\pi$ 的跳变比「换了一个专家」更大，见 `byte-moe-rollout-routing-gspo`。
