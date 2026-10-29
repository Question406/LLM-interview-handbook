---
id: tencent-moe-vs-dense
section: arch
order: 202
level: A
title: 腾讯混元一面：MoE 相对 Dense 赚在哪、亏在哪？
quick: >-
  假设一层有 8 个 experts，每个 token 只使用其中 2 个。总参数包含全部 experts，但当前 token
  只计算被选中的部分，所以参数量增加时，每个 token 的计算不必同比增加。
tags:
  - Tencent
  - Hunyuan
  - MoE
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 日常实习 腾讯混元大模型一面 好难
    url: 'https://www.nowcoder.com/feed/main/detail/8066dff3170547c98738ed3b1ba1b496'
    type: candidate-first-hand
---

## 回答思路

> **问题与场景：** 假设一层有 8 个 experts，每个 token 只使用其中 2 个。
>
> **做法与原因：** 代价在于 routing 和执行组织。
>
> **检查与取舍：** 所以我不会只比较参数量。

## 可以这样回答

假设一层有 8 个 experts，每个 token 只使用其中 2 个。总参数包含全部 experts，但当前 token 只计算被选中的部分，所以参数量增加时，每个 token 的计算不必同比增加。

代价在于 routing 和执行组织。Tokens 要被分到不同 experts，再把结果放回原来的位置；有的 expert 太忙时，其他设备会等待。总参数也仍需要存储和管理。

所以我不会只比较参数量。我会在相同任务和部署预算下，同时看质量、实际计算、memory、通信与 latency，判断稀疏激活的收益有没有被额外成本抵消。

## 技术备查

MoE 相对 Dense 赚的是容量：激活参数差不多，总参数大得多；亏的是路由不均、专家之间的通信，还有训练和推理两套并行要对齐。MoE 的总参数往往更大，它省的只是每个 token 激活的那部分 FFN，所以光说「稀疏省算力」不够。

## 赚在哪：容量和激活分开了

拿一个 token 走一层来说。Dense 要把整层 FFN 全跑一遍；MoE 把 FFN 换成 $E$ 个专家，token 先过 router，挑出 top-$k$ 个专家来跑（也可以再加共享专家），再把结果加权合起来：

$$
y=\sum_{i\in\mathrm{Top}k} g_i(x)\,E_i(x).
$$

这样总参数可以做到百 B 甚至万亿，单个 token 却只跑 $k$ 个专家，激活 FLOPs 接近一个「小 Dense」。同样的激活量下装得下更多东西，长尾知识、多领域内容更好塞进去。Router 本身只是一个 $d\times E$ 的矩阵，和专家矩阵比可以忽略。白板上我会画这条线：token → gating logits → softmax/sigmoid → 取 top-$k$ → 分发到专家 → 加权合回。

## 亏在哪：不均、通信、训推两套

最先碰到的是负载不均。少数专家接走大部分 token，剩下的专家训练不足，严重时路由塌缩。常用 aux loss、sequence-level balance 和 capacity factor 来防，见 `arch-moe-balance`、`ant-moe-aux-load-balance`、`code-moe-router-aux-loss`；capacity 设得太紧又会 drop token，见 `sys-moe-capacity-token-drop`。

然后是通信。expert parallel 要把 token 按专家做 all-to-all，EP size 直接决定通信量。小 batch、或者 decode 每次只处理一个 token 的时候，MoE 并不更快。

还有训推不一致。训练时有 drop、用某个 capacity，serving 换了另一套 top-$k$ 或 EP，两边的路由统计就对不上，见 `sys-moe-train-infer-routing-mismatch`。做 RL 时路由还会跟着策略一起漂，见 `stepfun-rl-moe-gspo`。所以评测时要关掉训练专用的随机 drop，用和线上一致的路由。

## 什么时候 Dense 更稳

数据少的时候，专家学不热，路由容易塌；延迟有硬约束的时候，小 batch 下 all-to-all 会把稀疏省下来的那点吃掉；团队还不会做负载均衡的时候，也先别上。像 7B 量级的数据、单机推理这种场景，硬上 MoE 不划算。混元面试官如果追问「和 Dense 比训练稳定性」，直接承认 MoE 要调的超参更多：lr、aux 系数、$k$、capacity 得一起拧。

## 追问

**稀疏一定省钱吗？**
不一定。训练算力按激活参数算，存储和通信却按总参数和 EP 算，小 batch 推理常常更慢。报算力时报激活 FLOPs，别拿总参数充数。

**$k=1$ 和 $k=2$ 怎么选？**
$k=1$ 更省，也更脆；$k=2$ 是常见的折中。共享专家相当于再加一份固定激活，DeepSeek 的细粒度 MoE 就是这么做的。

**加了 aux loss 还是塌缩，可能是什么原因？**
系数太小、数据偏科，或者 RL 之后分布变了。这时去看专家利用率的直方图，平均 loss 看不出来。

**为什么数据少的时候 Dense 更好？**
专家要吃到足够多的 token 才能训热。样本不够，大量专家 underfitting，效果还不如一份 Dense FFN。

**MoE 和 GQA/MLA 是一回事吗？**
不是一回事。GQA/MLA 压的是 KV cache，MoE 压的是 FFN 的激活。同一场面试连着问时分开讲，见 `arch-mla`。

## 真题记录

这题来自腾讯混元大模型日常实习一面的牛客候选人原帖，可信度 A，原话是 **“MoE 和 Dense 比，优势和代价是什么？”**。同一场还接着问了 Qwen 和 DeepSeek 的区别，那边要讲到共享专家和 MLA。

相关：`tencent-qwen-vs-deepseek`、`arch-moe`、`minimax-param-breakdown`
