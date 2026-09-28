---
id: coding-spec-accept
section: coding
order: 31
level: S
title: 白板：投机解码接受规则，拒绝后从哪一步重采样
quick: >-
  草稿 $\hat y_{1:\gamma}$ 从 $q$ 来。从左到右以 $\min(1,p/q)$ 接受。第一次拒绝发生在步 $i$：保留
  $\hat y_{1:i-1}$，从残差 $\propto\max(0,p-q)$ 在 **第 $i$ 步** 抽一个真 token，丢掉 $i$ 之后的草稿。全接受再从
  $p$ 多抽一个。
tags:
  - Coding
  - Speculative Decoding
  - Sampling
  - Google
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Fast Inference from Transformers via Speculative Decoding
    url: https://arxiv.org/abs/2211.17192
    type: primary
  - title: Accelerating Large Language Model Decoding with Speculative Sampling
    url: https://arxiv.org/abs/2302.01318
    type: primary
  - title: Speculative Decoding — vLLM
    url: https://docs.vllm.ai/en/latest/features/spec_decode.html
    type: secondary
---

## 题怎么来的

Leviathan et al. / DeepMind speculative sampling：小模型一次提 $\gamma$ 个
token，大模型一次前向给出这些位置的 logits，再用拒绝采样保证边际分布仍是 $p$。Google / OpenAI
推理白板要写接受不等式和「拒绝后从哪一步重采样」，不是加速比。KV 回滚见
`openai-speculative-decoding`、`sys-spec-sys`。本题把规则写成代码。前缀记
$x_{1:t-1}$，不要写成带比较符的下标。

## 从左到右，第一次拒绝就停

草稿模型 $q$ 顺序采样 $\hat y_1,\ldots,\hat y_\gamma$。目标 $p$ 在一次平行前向里给出每个位置的条件分布 $p(\cdot\mid x_{1:t-1},\hat y_{1:i-1})$，以及若全部接受时下一步的 $p(\cdot\mid x_{1:t-1},\hat y_{1:\gamma})$。对 $i=1,\ldots,\gamma$：

$$
\alpha_i=\min\bigl(1,\,p(\hat y_i)/q(\hat y_i)\bigr).
$$

抽 $u_i\sim\mathrm{Unif}(0,1)$。若 $u_i\le\alpha_i$，接受 $\hat y_i$，继续。若拒绝：在
同一个位置 $i$ 从残差

$$
n(v)\propto\max\bigl(0,\,p(v)-q(v)\bigr)
$$

采样 $y_i$，输出 $\hat y_{1:i-1},y_i$，丢掉 $\hat y_{i+1:\gamma}$。若全部接受，再从 $p(\cdot\mid x_{1:t-1},\hat y_{1:\gamma})$ 多抽一个 bonus token。这一点保证期望产出长度大于 $1$。

残差必须在拒绝的那一步求，条件是已接受前缀，不是草稿的第 $i+1$ 步。常见错法：拒绝后从 $p$ 直接采样却还把后面的草稿留下；或从第 $1$
步重来。数值上用 logprob：$\alpha=\min(1,\exp(\log p-\log q))$，在 log 域减，避免先 $\exp$ 再除。

```python
import torch
import torch.nn.functional as F

def residual_probs(p_logits, q_logits):
    p = F.softmax(p_logits.float(), dim=-1)
    q = F.softmax(q_logits.float(), dim=-1)
    n = (p - q).clamp(min=0)
    return n / n.sum().clamp_min(1e-12)

def spec_accept(draft_ids, log_p, log_q, p_logits, q_logits, bonus_logits):
    # draft_ids, log_p, log_q: [gamma]
    # p_logits, q_logits: [gamma, V]；bonus_logits: [V]
    accepted = []
    for i in range(draft_ids.numel()):
        ratio = torch.exp(log_p[i] - log_q[i]).clamp(max=1.0)
        if torch.rand(()) < ratio:
            accepted.append(int(draft_ids[i]))
            continue
        tok = int(torch.multinomial(residual_probs(p_logits[i], q_logits[i]), 1))
        accepted.append(tok)
        return accepted, i
    extra = int(torch.multinomial(F.softmax(bonus_logits.float(), dim=-1), 1))
    accepted.append(extra)
    return accepted, None
```

返回的下标 $i$ 就是拒绝步：KV 从 $S+\gamma$ 截回 $S+i$（再写入重采样的那个 token）。`None` 表示全接受，cache
合法长度是 $S+\gamma+1$（含 bonus）。greedy 对照：令 $p=q$ 则应全接受；令草稿总是错 token 且 $p$ 很尖，应在
$i=0$ 就残差采样。

## 和系统、采样栈的接口

$p$ 与 $q$ 必须同一 tokenizer、同一词表约束。非法 token 在两边都打 $-\infty$ 再比 $\log p-\log q$，不要只 mask 一边。温度、top-k、nucleus 若存在，要规定清是只改 $p$、只改 $q$、还是两边同一套；混用会破坏「边际仍是 $p$」的证明，见 `coding-topk-nucleus`。树状草稿只是把这条规则沿多条前缀做，接受的仍是从根出发的一条链。

不要把 $\gamma$ 个草稿的 logprob 求和再做一次接受：那是整段接受/拒绝，不是论文算法，期望长度和方差都变了。残差在理论上 $p=q$ 时全 $0$，不会拒绝；若数值把 $p-q$ 全打成负，clamp 后要有 fallback：直接从 $p$ 采样，并查是不是两套 softmax 温度不一致。

## 追问

- **拒绝后为什么不从 $i+1$ 抽？** $i$ 这个位置还没有合法 token。$i+1$ 的草稿以被拒 token 为条件，分布作废。
- **残差全 $0$ 怎么办？** $p=q$ 时不会拒绝。若数值把 $p-q$ 全打成负，clamp 后要有 fallback：直接从 $p$ 采样，并查 logprob 是否同一套
  softmax。
- **bonus token 算不算投机？** 算产出。全接受时 target 已经付过这一次前向，顺手再抽一个，论文原算法就有。
- **和 greedy 逐 token 何时逐字相同？** $p$ 取 $\arg\max$、$q$ 也 greedy 且总被接受时。随机采样只对分布，不对字符串；查 KV 回滚用 greedy。
