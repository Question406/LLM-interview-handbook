---
id: ant-beam-search-pytorch-tree
section: coding
order: 101
level: A
title: 蚂蚁 26 秋招：如何用 PyTorch 构建 LLM token 预测的 Beam Search 树？
quick: >-
  每个 beam 保存 token 前缀、累计 log-prob、结束标记和 cache；每步把 k 条 beam 扩展为 k×V 个候选，
  加上累计分数和长度惩罚后做 top-k，EOS 候选移入 finished 集合。最终比较完成序列，不能只拿最后一步概率最大的 token。
tags:
  - Ant Group
  - 2026 Campus Recruiting
  - Coding
  - Beam Search
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 26秋招蚂蚁金服大模型算法一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/e2585943c7874b3081b0878b646b6f01
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型算法
- 届别 / 流程：26 届秋招；一面
- 面试时间：原帖未披露；帖子发布于 2025-11-05
- 来源类型与可信度：牛客候选人原帖，A（公司、届别、岗位与轮次明确）
- 原始措辞：**“核心代码模式，写一下大模型预测token时，beam树如何构建，如何得到最终的结果(pytorch简单实现了一下，主要是还是讲明白)”**

这块容易把 beam search 写成「每步取当前条件概率最大的 $k$ 个 token」，丢掉累计 log-prob 和父节点回溯。树的节点是整条前缀，不是孤立 token。最终从 `finished`（已写 EOS）里选，没有完成序列才回退活跃 beam。采样分布见 `code-sampling`；本题是搜索不是采样。

## 树怎么长：扩展、扁平 top-$k$、拆父索引

活跃集合 `[(tokens, score, cache)]`，大小为 $k$。一步 forward 得到每条 beam 的 `log_softmax`，形状 $[k,V]$。累计

$$
s' = s + \log\pi(\cdot\mid\text{prefix}),
$$

展成 $k\times V$ 再 `topk`。父 beam 与新 token：

```python
import torch

def beam_expand(logp, scores, k, eos_id):
    # logp: [k, V], scores: [k]
    cand = scores[:, None] + logp
    topv, topi = torch.topk(cand.reshape(-1), k)
    vsz = logp.size(1)
    parent = torch.div(topi, vsz, rounding_mode="floor")
    token = topi % vsz
    done = token == eos_id
    return parent, token, topv, done
```

`parent` 用来复制前缀和 reorder KV cache。`done` 为真的候选进 `finished`，其余留在活跃集合。直到最大长度或没有活跃 beam。禁止用概率相乘（下溢）；必须累计 log 域。扩展成本 $O(kV)$，所以 $k$ 通常很小（4 到 8），大词表靠 `topk` 不要真物化排序全词表以外的逻辑，实现上仍是对 $k\times V$ 取 top。

## 长度惩罚与最终怎么选

不同长度不能直接比 $\sum\log\pi$：短句 log-prob 和往往更大。常用

$$
\mathrm{score}(y)=\frac{1}{|y|^\lambda}\sum_t\log\pi(y_t\mid y_{\lt t}),
$$

$\lambda\in[0.6,1]$。也可在 EOS 后不再扩展。重复 n-gram 屏蔽、坏 token mask 在加分之前做。最终：先比 `finished` 里惩罚后分数；全部顶到 `max_len` 仍无 EOS，才从活跃 beam 里选。不要返回「最后一步 logit 最大的那个 token 串起来」。

真实实现还要：batch 内各条样本 beam 独立；pad 不扩展；cache 按 `parent` gather。面试把「累计 logp → 扁平 top-k → 拆 parent → EOS 分流」讲完，代码短于调 `generate`。

## 追问

- **为什么不用概率相乘？** 长序列下溢成 0。log 域加法稳定，和 CE 的 log-softmax 一致，见 `pdd-ce-handwrite`。
- **$k=1$ 是什么？** 贪心。没有树，也不需要 parent。
- **和 top-p 能一起用吗？** 能，但那是每步先截核再在核上扩 beam，分布变了。蚂蚁这题先写标准 beam。
- **cache 不 reorder 会怎样？** 子节点用错历史 KV，分数全错。`parent` 必须 gather 每一层 cache。
- **为何结束不看活跃集合？** 未写 EOS 的前缀不可比完成句；产品上通常只要完整句子。无 EOS 才回退。
