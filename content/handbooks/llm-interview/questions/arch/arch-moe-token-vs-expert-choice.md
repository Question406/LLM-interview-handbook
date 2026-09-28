---
id: arch-moe-token-vs-expert-choice
section: arch
order: 23
level: A
title: Token-choice 和 Expert-choice 路由怎么实现？各自保证什么、牺牲什么？
quick: >-
  Token-choice：每个 token 选 Top-$k$ 专家，保证每 token 都有专家，不保证负载。Expert-choice：每个专家选
  Top-$C$ 个 token，负载锁成 $C$，有的 token 会没人要或被多个专家抢走。生产 LLM 仍以 token-choice
  为主；expert-choice 更像把 capacity 写成路由本身。
tags:
  - MoE
  - Router
  - Expert Choice
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Mixture-of-Experts with Expert Choice Routing
    url: https://arxiv.org/abs/2202.09368
    type: primary
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

错法：把两种 Top-$k$ 说成同一个 `topk` 调用、只是维不一样。它们保证的不变量相反，permute、capacity 和「没被选中的 token 怎么办」都要跟着改。GShard / Switch / Mixtral / DeepSeek 都是 token-choice；Expert Choice 是另一张分配表。

## Token-choice：token 挑专家

对分数矩阵 $S\in\mathbb{R}^{T\times N}$（softmax 或 sigmoid 亲和），每个 token 沿专家维取 Top-$k$：

$$
\mathcal{E}(t)=\mathrm{TopK}(S_{t,:},k).
$$

不变量：每个 token 恰好 $k$ 个专家（忽略后来的 capacity 截断）。不变量不包含负载：热点专家可以接到 $\gg kT/N$ 个 token。所以才要 aux / bias / capacity / drop，见 `arch-moe-balance`、`sys-moe-capacity-token-drop`。Dispatch 的 key 是 `(token, expert)` 对，按 expert id 排序后 grouped GEMM，见 `code-moe-permute-combine`。

Capacity 是事后补丁：专家 $i$ 只留分数最高的 $C$ 个 token，多出来的 drop 或改派。被 drop 的 token 这一层等于没走 MoE，和「路由保证每 token 都有专家」已经冲突。

## Expert-choice：专家挑 token

同一张 $S$，每个专家沿 token 维取 Top-$C$：

$$
\mathcal{T}(i)=\mathrm{TopC}(S_{:,i},C),\qquad C\approx \frac{kT}{N}.
$$

不变量：每个专家恰好 $C$ 个 token（$T$ 不够时取 $\min(C,T)$）。负载直方图是平的，aux 不再是主均衡器，all-to-all 消息长度也可预知。代价在 token 侧：

- 热门 token 被很多专家选中，等效 $k_{\mathrm{eff}}\gt k$；
- 冷门 token $k_{\mathrm{eff}}=0$，这一层只有 residual / shared。

实现上 permute 的主键变成「每个 expert 一段固定长 $C$」，padding 少，很适合静态 shape。但要显式处理 $k_{\mathrm{eff}}=0$：输出置零、走 residual，或再做一次 token-choice 补洞。面试别说 expert-choice「没有 drop」：它 drop 的是 token 的专家覆盖，不是专家的容量。

$C$ 的取法和 token-choice 的 capacity 同源：$C=\mathrm{CF}\cdot kT/N$。$\mathrm{CF}=1$ 时平均每个 token 仍大约被 $k$ 个专家覆盖，只是覆盖不再逐 token 保证。

## 怎么选题

要每 token 表达力均匀（生成、对齐、RL 都怕个别 token 这一层空转），走 token-choice，再用均衡和 capacity 管热点。要系统 shape 固定、杜绝热点卡、能接受长尾 token 少专家，走 expert-choice。把两者拼成「先 expert-choice 再给 $k_{\mathrm{eff}}=0$ 的 token 补路由」是工程折中，不是论文默认。

生产开源 LLM（Mixtral、DeepSeek-V3）走 token-choice，因为解码质量对「这个 token 有没有专家」比「这个专家满不满」更敏感。Expert-choice 更常出现在编码器 / 检索 / 训练吞吐优先的设定里。

## 追问

- **`topk` 写在哪一维？** Token-choice：`S.topk(k, dim=-1)`。Expert-choice：`S.topk(C, dim=0)`。写反就把保证的不变量写反。
- **Expert-choice 还要不要 aux？** 负载已锁。仍可加 z-loss 压 logits，见 `arch-moe-z-loss`，但不要再惩罚 $f_i$。
- **和 shared expert？** Shared 给 $k_{\mathrm{eff}}=0$ 的 token 兜底，expert-choice 更吃这套，见 `arch-shared-expert`。
- **RL 为什么更怕 expert-choice？** 策略一变，同一位置 token 可能突然没人要，$\log\pi$ 跳变比「换了一个专家」更狠，见 `byte-moe-rollout-routing-gspo`。
