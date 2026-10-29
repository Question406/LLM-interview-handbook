---
id: ant-moe-dense-routing
section: arch
order: 140
level: A
title: 蚂蚁实习：Dense 和 MoE 有何区别，路由怎么做？
quick: >-
  Dense 模型里每个 token 都走同一套 FFN 参数，容量和计算一起涨；MoE 把 FFN 换成一组专家，由路由器给每个 token 选
  top-$k$ 个专家，只算这几个。路由通常是线性投影加 softmax 得到 gating weights，再配合负载均衡，避免 token
  都挤到少数专家。
tags:
  - Ant Group
  - MoE
  - Routing
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 蚂蚁 实习大模型算法一面 1h
    url: 'https://www.nowcoder.com/feed/main/detail/46dc3bfc070a4128bb63cfc91003f509'
    type: candidate-first-hand
---

Dense 和 MoE 的区别在 FFN 这一层：Dense Transformer 对每个 token 用同一套 FFN 权重，参数和计算一起涨；MoE 把 FFN 换成一组专家，路由器只激活其中 top-$k$ 个，总参数可以很大，每个 token 实际用到的参数却只占一小部分。路由的做法是对 token 的隐状态做线性投影、softmax 成 gating，取 top-$k$ 后按 gating 加权专家输出。

常见的错是把 MoE 说成「就是更大的 Dense」，或者把路由讲成随便 argmax 一个专家。

## 路由怎么算

对 token 隐状态 $x\in\mathbb{R}^{d}$，线性投影得到专家 logits，再 softmax 成 gating：

$$
g(x)=\mathrm{softmax}(xW_g),\qquad y=\sum_{i\in\mathrm{top}k(g)} g_i(x)\,E_i(x).
$$

$E_i$ 通常仍是 SwiGLU 一类的 FFN：$\mathrm{SwiGLU}(u)=(\mathrm{SiLU}(uW_1)\odot uW_2)W_3$。训练时还要处理 capacity factor、token drop / overflow 和专家并行的 all-to-all。推理时同一个 batch 的专家分布不均会造成气泡，比如有的卡在等热点专家，有的专家在空转。

位置编码（RoPE）在 attention 那一侧，和 MoE 路由互不相干：$\langle R_m q, R_n k\rangle$ 只依赖相对位移 $n-m$，不参与选专家。被问「MoE 怎么外推」时，别答成改 RoPE。

## Dense 和 MoE 要对比哪几项

光说「MoE 更大」不够，我会对比五项：激活参数（每 token 算力）、总参数（容量）、通信（all-to-all）、负载不均、训推路由是否一致。Dense 没有路由塌缩的问题，但也没有「加专家不加倍 FLOPs」这根杠杆。

蚂蚁后续面试常追问负载均衡损失，准备时把这张卡和 `ant-moe-aux-load-balance` 连起来讲。

## 追问

**为什么 $k$ 常取 1 或 2？**
$k$ 越大越接近 Dense，省算力的理由就弱了。$k=1$ 最省，但路由一旦选错，没有后备专家。

**共享专家是什么？**
一部分专家对所有 token 常开，其余专家仍走 top-$k$。常开的那部分 fallback 通用变换，减轻路由的压力。

**专家并行挂了是什么表现？**
某个专家所在的 rank 超时，整层 all-to-all 卡住，看起来像训练 hang。要和数据 loader 卡住区分开。

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-03-27
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“分别讲一下 Dense 模型和 MoE 模型以及二者的区别”**；**“讲一下 MoE 的 路由机制是如何做的”**
