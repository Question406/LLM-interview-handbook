---
id: baichuan-mha-handwrite
section: coding
order: 184
level: A
title: 百川智能二面：手写多头注意力时和 DeepSeek 练习卡差在哪？
quick: >-
  同一套 $QKV$ + 拆头 + 缩放点积 + mask + 拼头。二面常紧接着要你对比 GQA/MHA，并口头写出
  DPO/PPO 公式，不能把 Attention 写成调用库的一行。
tags:
  - Baichuan
  - Attention
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川大模型算法二面-日常实习
    url: https://www.nowcoder.com/feed/main/detail/326e80fe4eb14fd58e9712ca2852ec1a
    type: candidate-first-hand
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：二面
- 面试时间：原帖未披露；帖子发布于 2026-02-13
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“手写多头注意力机制”**；同面还有 **“手写一下 dpo和ppo”**、**“手写梯度下降法的二分”**

这块容易写成 `nn.MultiheadAttention` 一行，或 reshape 时把 $[B,T,H,d_h]$ 和 $[B,H,T,d_h]$ 搞反。骨架与 `deepseek-mha-handwrite`、`pdd-attention-handwrite` 相同；百川二面差在紧接着 GQA、DPO/PPO、二分求根（见 `baichuan-sqrt-binary-search`、`baichuan-grpo-ppo-dpo`）。先画形状再写公式，避免卡在 `view`。

## 形状清单：拆头、缩放、mask、拼回

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d_h}}+M\Big)V
$$

$d_{\mathrm{model}}$ 整除 $H$，$d_h=d_{\mathrm{model}}/H$。$Q,K,V: [B,H,T,d_h]$，scores $[B,H,T,T]$。因果 mask 下三角为可见；padding 的 True/False 与 `masked_fill(-inf)` 不要反。fp16 下 softmax 升 fp32。`view` 前 `contiguous`。

```python
import torch

def mha(x, wq, wk, wv, wo, n_heads, mask=None):
    b, t, c = x.shape
    dh = c // n_heads
    q = (x @ wq).view(b, t, n_heads, dh).transpose(1, 2)
    k = (x @ wk).view(b, t, n_heads, dh).transpose(1, 2)
    v = (x @ wv).view(b, t, n_heads, dh).transpose(1, 2)
    scores = (q @ k.transpose(-2, -1)) * dh**-0.5
    if mask is not None:
        scores = scores.masked_fill(mask, float("-inf"))
    out = torch.softmax(scores.float(), dim=-1).to(x.dtype) @ v
    out = out.transpose(1, 2).contiguous().view(b, t, c)
    return out @ wo
```

GQA：把 $K,V$ 头数降到 $H_{\mathrm{kv}}$，对 $Q$ 做 `repeat_interleave`，softmax 公式不变。不要改缩放或拆两次 `d_h`。

## 同面连问：先形状，再 DPO/PPO

DPO：token logp 聚成 sequence logp，再

$$
L=-\log\sigma\bigl(\beta(\log\pi_\theta(y_w)-\log\pi_\theta(y_l)-\log\pi_{\mathrm{ref}}(y_w)+\log\pi_{\mathrm{ref}}(y_l))\bigr).
$$

PPO：$\min(\rho A,\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)A)$，见 `code-ppo-clip`。三题连问时 Attention 十分钟内写完主干，公式口头写，二分另开卡。不要在 attention 里写 dropout 细节耗掉白板。

## 追问

- **缩放为什么除 $\sqrt{d_h}$？** 点积方差随 $d_h$ 涨，softmax 否则变 one-hot。
- **GQA 改公式了吗？** 没有。只改 K/V 头的组织与 cache 体积。
- **cross-attn？** $T_q\neq T_k$，scores $[B,H,T_q,T_k]$，mask 按 key 侧 padding。
- **和 MLA？** MLA 压表示维，不是少头。见 `arch-mla`。百川若只问 MHA/GQA，不要主动展开吸收。
- **DPO 的 logp 在哪一层加？** 序列级求和（或平均，需与实现一致），不是对每个 token 各算一个 DPO。
