---
id: code-beam-search
section: coding
order: 55
level: A
title: 手写 Beam Search 一步：累计 logprob、flatten top-k、回指父 beam
quick: "每步把 $K$ 条 beam 的累计 logprob 加到 $[B,K,V]$ 的 log-softmax 上，展平成 $[B,KV]$ 取 top-$K$。下标整除 $V$ 得到父 beam，模 $V$ 得到新 token，再用父 beam 去 gather 前缀和 KV cache。"
tags:
  - BeamSearch
  - Decoding
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Generation strategies (Hugging Face)
    url: https://huggingface.co/docs/transformers/en/generation_strategies
    type: primary
---

## 题目描述

实现批量 beam search 的一步选择：对每个 batch，把所有已有 beam 与词表词组合的累计分数放在一起，选出最高的若干个。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `beam_step(logp, beam_logp, beam_size)`。logp 为 [B,K,V]，`beam_logp` 为 [B,K]，`beam_size` 在 1 到 K*V 之间。输入是 log 分数，可以直接相加。

### 输出与约束

返回 `(scores,prev,tok)`，均为 [B,`beam_size`]；scores 降序排列，prev 指出父 beam 编号，tok 指出接上的词编号。本函数不包含 EOS 冻结、长度惩罚或序列拼接；并列时允许采用后端 topk 的顺序。

### 示例

```text
logp=[[[0,-3],[-4,0]]], beam_logp=[[0,-1]], beam_size=2
返回 scores=[[0,-1]], prev=[[0,1]], tok=[[0,1]]
```

## 解题思路与参考答案

Beam search 一步的向量化写法是：把每条 beam 的累计 logprob 加到本步 $[B,K,V]$ 的 log-softmax 上，展平成 $[B,KV]$ 取 top-$K$，下标整除 $V$ 是父 beam，模 $V$ 是新 token。这样 $K$ 条 beam 的候选放在一起竞争，好的前缀可以同时占好几个名额。

常见的写错有两种。一是每条 beam 各自 argmax，那其实是 $K$ 路独立的贪心，beam 之间不会交叉。二是在 fp32 里连乘概率，序列一长就下溢。和 greedy、sampling 对比着看，greedy 就是 $K=1$ 的 beam。蚂蚁的原题是用树来讲的，见 `ant-beam-search-pytorch-tree`；这张卡写向量化的一步。

## 一步

已有 `beam_logp`，形状 `[B,K]`，和本步的 `logp`，形状 `[B,K,V]`：

$$
\mathrm{cand}_{b,k,v}=\mathrm{beam}_{b,k}+\log p_k(v),\qquad
\text{对 } KV \text{ 个候选取 top }K.
$$

```python
import torch

def beam_step(logp, beam_logp, beam_size):
    # logp: [B, K, V]；beam_logp: [B, K]
    cand = beam_logp.unsqueeze(-1) + logp
    B, K, V = cand.shape
    scores, idx = cand.reshape(B, K * V).topk(beam_size, dim=-1)
    prev, tok = idx // V, idx % V
    return scores, prev, tok
```

`prev` 用来给每条新 beam gather 它的 KV cache 和前缀 token。出现 EOS 的 beam 冻结分数，继续扩还没结束的；最后在结束的 beam 里取分数最高的。长度惩罚常用 GNMT 的写法：

$$
\mathrm{score}=\frac{\sum_t\log p_t}{(5+T)^\alpha/(6)^\alpha}.
$$

$\alpha=0.6$ 比较常见。不除长度的话，结果会偏向短句。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

构造一个 batch、两个 beam、每个两个 token，手算累计分数后检查 top-2 的父 beam 与 token。分数无平票，避免依赖 topk 的平票顺序。

```python
logp = torch.tensor([[[0., -3.], [-4., 0.]]])
scores, parent, token = beam_step(logp, torch.tensor([[0., -1.]]), 2)
torch.testing.assert_close(scores, torch.tensor([[0., -1.]]))
assert parent.tolist() == [[0, 1]] and token.tolist() == [[0, 1]]
print("simple tests passed")
```

## 追问

**beam 和 sampling 怎么选？**
beam 是 MAP 近似，多样性差；sampling 更贴近训练分布。现在对话生成多用 sampling。

**diverse beam 是什么？**
把 $K$ 条 beam 分成几个小组，组之间加相异惩罚。手写时先把普通 beam 写对。

**和 KV cache 怎么配合？**
$K$ 条序列各有一份 cache。一个父 beam 被两个子节点共用时要做 CoW，见 `code-paged-kv-cow`。
