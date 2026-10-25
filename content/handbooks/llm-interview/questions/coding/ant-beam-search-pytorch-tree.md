---
id: ant-beam-search-pytorch-tree
section: coding
order: 101
level: A
title: 蚂蚁 26 秋招：如何用 PyTorch 构建 LLM token 预测的 Beam Search 树？
quick: "Beam 树的每个节点是一整条前缀，保存 token 序列、累计 log-prob、是否结束和 cache。每步把 k 条 beam 扩成 k×V 个候选，按累计分数取 top-k，拆出父 beam 和新 token，写出 EOS 的进 finished。最后在 finished 里按长度惩罚后的整句分数选，最后一步的概率说明不了整句好坏。"
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

## 题目描述

实现 beam search 的单步候选扩展：已有 k 条候选序列，每条序列再接一个词，从全部扩展中保留累计得分最高的 k 个。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `beam_expand(logp, scores, k, eos_id)`。logp 为 [k,V] 的浮点张量，表示各候选的下一词 log-probability；scores 为 [k] 的累计分数；1≤k≤kV，`eos_id` 是合法词表编号。

### 输出与约束

返回 `(parent, token, topv, done)`，各为长度 k 的张量，按得分降序排列；parent 是原候选下标，token 是接上的词编号，topv 是新累计分数，done 表示 token 是否等于 `eos_id`。本步只选择和标记，不维护历史 token，也不自动屏蔽已经结束的候选；示例不含边界并列得分。

### 示例

```text
logp=[[0,-3],[-4,0]], scores=[0,-1], k=2, eos_id=1
返回 parent=[0,1], token=[0,1], topv=[0,-1], done=[False,True]
```

## 解题思路与参考答案

Beam 树的每个节点是一整条前缀：每条 beam 存着 token 前缀、累计 log-prob、是否已结束，以及它的 cache。每一步把 $k$ 条 beam 扩展成 $k\times V$ 个候选，按累计分数取 top-$k$，再拆出「父 beam 是谁、新 token 是谁」，写出 EOS 的候选移进 `finished`。最终答案从 `finished` 里按整句分数挑，没有完成的序列才回退到活跃 beam。

举个例子，$k=2$ 时两条 beam 分别是「今天天气」和「今天心情」。下一步要把两条 beam 的 $2\times V$ 个续写放在一起比累计分数，很可能两个名额都给了「今天天气」的两种续写，「今天心情」这条就被剪掉了。每步只看当前条件概率取 $k$ 个 token、丢掉累计 log-prob 和父节点回溯，就是最常见的写错法。另外这题是搜索，和采样是两回事，采样分布见 `code-sampling`。

## 树怎么长：扩展、扁平 top-$k$、拆父索引

活跃集合是 `[(tokens, score, cache)]`，大小为 $k$。一次 forward 得到每条 beam 的 `log_softmax`，形状 $[k,V]$，加上累计分数：

$$
s' = s + \log\pi(\cdot\mid\text{prefix}),
$$

然后展平成 $k\times V$ 取 `topk`，用整除和取模拆出父 beam 和新 token：

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

`parent` 用来复制前缀、reorder KV cache。`done` 为真的候选进 `finished`，其余留在活跃集合，一直跑到最大长度或者没有活跃 beam 为止。分数一定在 log 域累加，概率直接相乘会下溢。每步扩展的成本是 $O(kV)$，所以 $k$ 通常很小（4 到 8）；大词表也只是在 $k\times V$ 上取 top，不用对全词表做完整排序。

## 长度惩罚，以及最后怎么选

不同长度的句子不能直接比 $\sum\log\pi$，短句的 log-prob 和往往更大。常用的做法是按长度归一：

$$
\mathrm{score}(y)=\frac{1}{|y|^\lambda}\sum_t\log\pi(y_t\mid y_{\lt t}),
$$

$\lambda\in[0.6,1]$。写出 EOS 的 beam 不再扩展。重复 n-gram 屏蔽、坏 token mask 要在加分之前做。最后先比 `finished` 里惩罚后的分数；全部顶到 `max_len` 还没有 EOS，才从活跃 beam 里选。把每一步 logit 最大的 token 串起来当答案，是错的。

真实实现还要处理几件事：batch 里每条样本的 beam 互相独立，pad 不扩展，cache 按 `parent` 做 gather。面试时把「累计 logp → 扁平 top-k → 拆 parent → EOS 分流」讲完就够了，代码比调 `generate` 还短。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

给出没有平票的累计分数，手算 top-2：第一个 beam 的 token 0 为 0，第二个 beam 的 token 1 为 -1。后者设为 EOS，检查 parent、token 和 done 都对应同一个展平下标。

```python
logp = torch.tensor([[0., -3.], [-4., 0.]])
parent, token, score, done = beam_expand(logp, torch.tensor([0., -1.]), 2, eos_id=1)
assert parent.tolist() == [0, 1] and token.tolist() == [0, 1]
assert done.tolist() == [False, True]
torch.testing.assert_close(score, torch.tensor([0., -1.]))
print("simple tests passed")
```

## 追问

**为什么不用概率相乘？**
长序列会下溢成 0。log 域做加法是稳定的，也和交叉熵损失（CE）里的 log-softmax 一致，见 `pdd-ce-handwrite`。

**$k=1$ 是什么？**
就是贪心。没有树，也不需要 parent。

**能和 top-p 一起用吗？**
能。做法是每步先截出 nucleus，再在 nucleus 上扩 beam，分布就变了。蚂蚁这题先写标准 beam。

**cache 不 reorder 会怎样？**
子节点会用错历史 KV，分数全错。`parent` 必须对每一层的 cache 做 gather。

**为什么最后不看活跃集合？**
没写出 EOS 的前缀和完成的句子没法比，产品上通常也只要完整句子。只有一条都没结束时才回退。

## 真题记录

这题来自牛客候选人原帖：蚂蚁集团大模型算法岗，26 届秋招一面，原帖没写面试时间，帖子发布于 2025-11-05，可信度 A（公司、届别、岗位和轮次都明确）。原话是 **“核心代码模式，写一下大模型预测token时，beam树如何构建，如何得到最终的结果(pytorch简单实现了一下，主要是还是讲明白)”**。
