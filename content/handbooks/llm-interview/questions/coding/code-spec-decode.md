---
id: code-spec-decode
section: coding
order: 54
level: S
title: 手写投机解码的接受规则：$\min(1,p/q)$，拒绝后在同一位置从残差重采样
quick: "从左到右按 $\\min(1,p/q)$ 接受草稿，第 $i$ 个被拒就在同一位置从 $\\propto\\max(0,p-q)$ 重采一个 token，后面的草稿全部丢掉。这是标准拒绝采样，所以输出分布仍是 $p$。"
tags:
  - SpeculativeDecoding
  - Sampling
  - Inference
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Fast Inference from Transformers via Speculative Decoding
    url: https://arxiv.org/abs/2211.17192
    type: primary
---

## 题目描述

实现手册简化版 speculative decoding 接受接口。草稿模型已经给出一段候选 token；目标模型和草稿模型在各位置的词表概率也已给定，请决定本轮输出哪些 token，并指出第一次拒绝发生的位置。

### 接口与规则

`spec_accept(p,q,draft,bonus_logits=None,gens=None)`：p、q 是 `[gamma,V]` 的合法概率分布，分别代表目标模型与草稿模型；draft 是长度 gamma 的 token ID，所选草稿 token 在 q 中概率为正。返回 `(tokens,rejected_index)`。

依次判断候选 token：接受概率为目标概率除以草稿概率与 1 的较小者。首次拒绝时，输出此前已接受的 token，并追加一个从目标减草稿的正残差分布中采样的替代 token，然后停止本轮；返回该拒绝位置的0-based下标。全部接受时返回 None；若提供 `bonus_logits`，本卡约定再追加它最大值对应的下标，而非另行随机采样。

gens 是可选 PyTorch Generator。这里仅验证该独立接口，不要求实现完整双模型推理调度。

### 示例

```text
p=q=[[0.25,0.75]], draft=[1], bonus_logits=[2,0]
输出tokens=[1,0]，rejected_index=None

p=[[0,1]], q=[[1,0]], draft=[0]
输出tokens=[1]，rejected_index=0
```

概率输入保证合法，不要求防御性检查全部异常分布。

## 解题思路与参考答案

投机解码的接受规则就是拒绝采样：草稿 token 按 $\min(1,p/q)$ 的概率留下，第一次被拒就在同一个位置从残差分布重采，后面的草稿全丢。面试官要看的是分布为什么还是 $p$，加速比是次要的。

举个例子，草稿模型一次猜了 4 个 token，前两个通过，第三个被拒。这时就在第三个位置，从 $\max(0,p-q)$ 归一化后的分布里抽一个 token，输出前两个草稿加这个新 token，第四个草稿直接扔掉，KV 回滚到接受长度就行。常见写错有三种：拒绝后从 $p$ 直接采样，却把 $\hat y_{i+1:\gamma}$ 留下；拒绝后从第 1 步整段重来；残差用 $p-q$，却没把负数截掉。

## 从左到右，第一次拒绝就停

$$
\alpha_i=\min\big(1,\,p_i(\hat y_i)/q_i(\hat y_i)\big).
$$

抽 $u_i\sim U(0,1)$，$u_i\le\alpha_i$ 就留下，接着看下一个。否则在同一个 $i$ 上按

$$
n(v)\propto\max\big(0,\,p_i(v)-q_i(v)\big)
$$

采样 $y_i$，输出 $\hat y_{1:i-1},y_i$。如果全部接受，再从 $p(\cdot\mid \hat y_{1:\gamma})$ 抽一个 bonus，所以每轮期望长度 $>1$。

数值上用 logprob 算，$\alpha=\min(1,\exp(\log p-\log q))$。遇到 $q_i(\hat y_i)=0$ 就直接拒绝、走残差，这时残差退回 $p$。

```python
import torch

def spec_accept(p, q, draft, bonus_logits=None, gens=None):
    # p,q: [gamma, V] 概率；draft: [gamma]
    g = gens or torch.Generator().manual_seed(0)
    accepted = []
    for i in range(draft.numel()):
        tok = int(draft[i])
        alpha = min(1.0, float(p[i, tok] / q[i, tok].clamp_min(1e-12)))
        if torch.rand((), generator=g).item() <= alpha:
            accepted.append(tok)
            continue
        resid = (p[i] - q[i]).clamp_min(0)
        if float(resid.sum()) <= 0:
            resid = p[i]
        y = int(torch.multinomial(resid, 1, generator=g))
        accepted.append(y)
        return torch.tensor(accepted), i
    if bonus_logits is not None:
        accepted.append(int(bonus_logits.argmax()))
    return torch.tensor(accepted), None
```

默写完先做个 sanity check：$p=q$ 时 $\alpha=1$，草稿原样收下，再加一个 bonus。另外，采样本身的温度 / top-p 要在 $p$ 和 $q$ 上用同一套，否则接受率对不上，见 `code-sampling`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

p=q 时接受率为 1，不需要靠重复随机采样碰运气。再构造草稿 token 在 p 中概率为零的分布，必然拒绝并从残差补出 token 1。

```python
p = torch.tensor([[0.25, 0.75]])
out, rejected = spec_accept(p, p, torch.tensor([1]), bonus_logits=torch.tensor([2., 0.]))
assert out.tolist() == [1, 0] and rejected is None
out, rejected = spec_accept(torch.tensor([[0., 1.]]), torch.tensor([[1., 0.]]),
                            torch.tensor([0]), gens=torch.Generator().manual_seed(7))
assert out.tolist() == [1] and rejected == 0
print("simple tests passed")
```

## 追问

**为什么分布还是 $p$？**
这是标准拒绝采样。接受的是 $q$ 的样本，用 $p/q$ 校正；拒绝时，残差把差的那一块补上。

**草稿多长好？**
要看草稿模型有多强。$\gamma$ 大，一次验证能处理更多 token，但接受率会掉。

**树状草稿 / Medusa 怎么接受？**
接受规则推广到树上，每个节点仍是 $p/q$。手写时先把链写对。
