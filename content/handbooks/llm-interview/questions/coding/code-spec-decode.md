---
id: code-spec-decode
section: coding
order: 54
level: S
title: 手写投机解码的接受规则：$\min(1,p/q)$，拒绝后在同一位置从残差重采样
quick: "从左到右以 $\\min(1,p/q)$ 接受草稿；第 $i$ 个被拒时，在第 $i$ 步从 $\\propto\\max(0,p-q)$ 重采一个 token，丢掉后面的草稿。这样输出分布仍是 $p$。"
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

面试要的是拒绝采样保证分布，不是加速比。常见误区是：拒绝后从 $p$ 直接采样却把 $\hat y_{i+1:\gamma}$ 留下；或从第 1 步整段重来；或残差用 $p-q$ 却没把负数截掉。KV 回滚到接受长度即可。

## 从左到右，第一次拒绝就停

$$
\alpha_i=\min\big(1,\,p_i(\hat y_i)/q_i(\hat y_i)\big).
$$

抽 $u_i\sim U(0,1)$。$u_i\le\alpha_i$ 就留下，继续。否则在同一个 $i$ 上

$$
n(v)\propto\max\big(0,\,p_i(v)-q_i(v)\big)
$$

采样 $y_i$，输出 $\hat y_{1:i-1},y_i$。全接受时再从 $p(\cdot\mid \hat y_{1:\gamma})$ 抽一个 bonus，期望长度 $>1$。

数值用 logprob：$\alpha=\min(1,\exp(\log p-\log q))$。$q_i(\hat y_i)=0$ 直接拒绝并走残差（残差退回 $p$）。

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

$p=q$ 时 $\alpha=1$，草稿原样收下，再加 bonus。这是默写完的 sanity check。采样本身的温度 / top-p 要在 $p$ 和 $q$ 上用同一套，否则接受率对不上，见 `code-sampling`。

## 追问

- **为什么分布还是 $p$？** 标准拒绝采样。接受的是 $q$ 的样本，用 $p/q$ 校正；拒绝时残差补上差的那一块。
- **草稿多长好？** $\gamma$ 大则一次验证处理更多 token，但接受率掉。和草稿模型强度有关。
- **树状草稿 / Medusa？** 接受规则推广到树上，每个节点仍是 $p/q$。手写先把链写对。
