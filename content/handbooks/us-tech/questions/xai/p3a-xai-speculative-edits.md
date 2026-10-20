---
id: p3a-xai-speculative-edits
section: xai
order: 750
level: S
title: "xAI：代码编辑 Speculative Edits：复用原代码草稿"
quick: "把原代码当作草稿，每次让模型批量验证一段，接受和模型预测一致的前缀；第一次分歧时取模型的预测并丢掉后面的结果，这样输出和逐 token 贪心完全相同。"
companies:
  - xai
tags:
  - xAI
  - Coding
  - Frontier-2026-10
  - 完整编程练习
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: 1Point3Acres xAI source
    url: https://www.1point3acres.com/interview/thread/1193219
    type: candidate-first-hand
---

## 题目

代码编辑场景下，模型要输出的新代码大部分和原代码相同。题目要求实现普通的 greedy 解码和 speculative edits：把原代码当作草稿，让模型一次验证多个 token，从而减少调用次数，同时输出必须和 greedy 完全一致。要处理草稿全部匹配、中途分歧和输出长度上限这几种情况。

> 来源：一亩三分地 xAI 候选人原帖（thread 1193219）。原帖明确要求 greedy 与 speculative edits 输出相同、复用原代码作为草稿、处理全匹配、分歧与长度上限，并以加速为目标；`verify` 的模拟接口、函数签名和测试是手册补的练习约定，原帖没写的条件不当作已确认的面试事实。

## 思路

核心观察是：模型在位置 $i$ 的预测只依赖它前面的上下文。把 `prefix + draft[pos:pos+block]` 一次送进模型，第 $i$ 个输出就是「假设前 $i$ 个草稿 token 都对」时的下一个 token。只要前面的草稿 token 都和预测一致，这个上下文就和 greedy 当时看到的一模一样，预测也就一样。

所以每一轮验证时：

- 从左到右比较草稿 token 和模型预测，相同就接受；
- 第一次不同时，把模型的预测（而不是草稿 token）追加进输出，然后停止，后面的预测都基于错误上下文，必须丢掉；
- 遇到 EOS 或达到 `limit` 就结束。

这份练习在第一次分歧后就永久退回 greedy，不尝试把草稿重新对齐。面试中可以把重新对齐（比如在草稿里找到和当前输出后缀匹配的位置继续用）作为改进方向提出来。

还有一点要和面试官说清：这里的模型是确定性 argmax，接受条件是「完全相等」。采样版 speculative decoding 用 $p/q$ 概率比做接受判断，那套规则不适用于这道题。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `verify(prefix, candidates) -> list`：模拟模型。返回长度与 `candidates` 相同的列表，第 $i$ 项是以 `prefix + candidates[:i]` 为上下文时的 argmax。模型固定、确定性，平局按统一规则打破。
- `greedy(verify, limit, eos=-1)`：逐 token 解码，返回 `(tokens, calls)`。
- `edits(verify, draft, block, limit, eos=-1)`：每次最多验证 `block` 个草稿 token，只接受与预测一致的连续前缀；第一次不一致时输出该位置的模型预测，之后永久切回 greedy。返回 `(tokens, calls)`。
- EOS 不放进输出；`limit = 0` 时不调用模型；`block >= 1`，`limit >= 0`，否则抛 `ValueError`。

### 输入输出示例

```text
模型目标输出 [1, 2, 3]，草稿 [1, 9, 3]，block = 2
greedy(verify, 10)[0]               -> [1, 2, 3]
edits(verify, [1, 9, 3], 2, 10)[0]  -> [1, 2, 3]
```

第一轮验证 `[1, 9]`：1 被接受，9 处模型预测 2，于是输出 2 并切回 greedy，接着生成 3 和 EOS。草稿完全正确时，6 个 token 用 block = 3 两次批量调用就能全部确认，再加一次调用得到 EOS；greedy 需要 7 次。

### 解题思路与正确性

用归纳法证明：每轮开始时 `out` 都等于 greedy 输出的一个前缀。验证位置 $i$ 的上下文是 `out + candidates[:i]`；如果前 $i$ 个草稿 token 都已被接受，这个上下文就是 greedy 在同一步的上下文，所以预测相同，追加它保持不变量。分歧位置的预测同样基于正确的上下文，也可以追加；但它之后的预测用的是错误的草稿 token，必须丢弃。

退回 greedy 后每一步就是普通贪心，不变量显然成立。因此两种算法在 EOS 或 `limit` 处同时停下，输出完全相同。

### 完整参考实现（Python 3）

```python
def greedy(verify, limit, eos=-1):
    """逐 token 贪心解码，返回 (输出 token 列表, 模型调用次数)。EOS 不放进输出。"""
    if limit < 0:
        raise ValueError(f"limit must be non-negative, got {limit}")
    out = []
    calls = 0
    while len(out) < limit:
        token = verify(out, [0])[0]  # 只要下一个 token，candidates 内容不影响第 0 个预测
        calls += 1
        if token == eos:
            break
        out.append(token)
    return out, calls


def edits(verify, draft, block, limit, eos=-1):
    """speculative edits：拿原代码 draft 当草稿，每次批量验证最多 block 个 token。

    verify(prefix, candidates)[i] 是以 prefix + candidates[:i] 为上下文时模型的 argmax。
    输出保证和 greedy 完全相同。返回 (输出 token 列表, 模型调用次数)。
    """
    if block < 1:
        raise ValueError(f"block must be >= 1, got {block}")
    if limit < 0:
        raise ValueError(f"limit must be non-negative, got {limit}")
    out = []
    pos = 0  # 下一个待验证的草稿位置
    calls = 0
    use_draft = True
    while len(out) < limit:
        if use_draft and pos < len(draft):
            candidates = list(draft[pos:pos + min(block, limit - len(out))])
            predictions = verify(out, candidates)
            calls += 1
            if len(predictions) != len(candidates):
                raise ValueError("verify must return one prediction per candidate")
            for candidate, prediction in zip(candidates, predictions):
                if prediction == eos:
                    return out, calls
                out.append(prediction)  # 无论是否匹配，模型的预测都是正确的下一个 token
                if prediction != candidate:
                    # 后面的预测建立在错误的草稿 token 上，全部作废；之后退回 greedy
                    use_draft = False
                    break
                pos += 1
        else:
            token = verify(out, [0])[0]
            calls += 1
            if token == eos:
                break
            out.append(token)
    return out, calls
```

### 可执行测试

```python
def make_verify(target):
    """依赖前缀的确定性模型：只有上下文是 target 的前缀时才继续预测 target，否则输出 EOS。"""

    def verify(prefix, candidates):
        predictions = []
        context = list(prefix)
        for candidate in candidates:
            n = len(context)
            if n < len(target) and context == target[:n]:
                predictions.append(target[n])
            else:
                predictions.append(-1)
            context.append(candidate)  # 错误的草稿 token 会改变后面的预测
        return predictions

    return verify

# 各种草稿（空、全错、中间分歧、完全匹配）和长度上限下，输出都必须和 greedy 一致
for target in ([], [1], [1, 2, 3, 4]):
    verify = make_verify(target)
    for draft in ([], [9], [1, 9, 3], target):
        for limit in range(7):
            assert edits(verify, draft, 2, limit)[0] == greedy(verify, limit)[0]

# 草稿中途分歧：输出模型的修正 token，然后继续贪心
verify = make_verify([1, 2, 3])
assert edits(verify, [1, 9, 3], 2, 10)[0] == [1, 2, 3]

# 草稿完全正确时，批量验证的调用次数少于逐 token 贪心
verify = make_verify(list(range(6)))
assert edits(verify, list(range(6)), 3, 10)[1] < greedy(verify, 10)[1]

# limit = 0 不调用模型
assert edits(verify, list(range(6)), 3, 0) == ([], 0)
```

### 复杂度与追问

设草稿长度为 $L$。草稿全部正确时，调用次数约为 $\lceil L / \text{block} \rceil$ 加上之后的贪心步数；最坏情况（第一个 token 就分歧）退化成和 greedy 一样逐 token 调用。参考实现里列表切片和拼接有复制开销，但和模型调用比可以忽略。

- 调用次数少了，GPU 上一定更快吗？不一定。一次验证 `block` 个 token 的计算量更大，分歧时还要把 KV cache 回滚到分歧位置。真实收益取决于草稿命中率和批量验证的开销，要用墙钟时间衡量。
- `block` 怎么选？命中率高时 block 大更省调用，命中率低时大 block 浪费的计算多。可以根据最近几轮的接受长度动态调整。

## 相关题

- [[coding-spec-accept]]：采样版的接受规则，用 $\min(1,p/q)$ 和残差分布；本卡的 greedy 前缀匹配是它的特例。
- [[p3a-cursor-speculative-decoding-acceptance]]：同样是编程题，草稿来自小模型，要求输出分布和 target 一致，而不是逐字相同。
