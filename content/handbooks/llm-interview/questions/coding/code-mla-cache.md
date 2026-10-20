---
id: code-mla-cache
section: coding
order: 20
level: S
title: 手写 MLA：只缓存 latent，decode 时把 $W_{UK}$ / $W_{UV}$ 吸收掉
quick: "cache 只存每个 token 的 $d_c$ 维 latent $c_{kv}$ 和各头共享的 $D_r$ 维 RoPE key。decode 时把 $W_{UK}$ 吸收进 query、$W_{UV}$ 移到输出端，直接在 latent 上做 attention。"
tags:
  - MLA
  - KV Cache
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
    url: https://arxiv.org/abs/2405.04434
    type: primary
---

常见错法有两种。一是把 RoPE 直接加在上投影出来的 $k_c=W_{UK}c_{kv}$ 上，这样 $W_{UK}$ 就再也吸收不进 query，逐 token 生成（decode） 时每步还得把整段 latent 还原成 K，也就失去了通过低维 cache 减少读取量的收益。二是 cache 里存了还原后的 K/V，那就只是换了个参数化的 MHA。面试官看三件事：cache 里到底存什么，decoupled RoPE 为什么要单独拆出来，吸收之后的 decode 和 输入预填充（prefill，即处理输入并建立缓存） 是否逐位相等。原理见 `arch-mla`，普通 MHA 写法见 `code-attention`。

## 形状

记 $H$ 个头、head dim $D_h$、RoPE 维度 $D_r$、KV latent 维度 $d_c$：

- $c_{kv}=h W_{DKV}$：`[B, T, d_c]`，进 cache
- $k_r=\mathrm{RoPE}(h W_{KR})$：`[B, T, D_r]`，所有头共享，进 cache
- $k_c=c_{kv}W_{UK}$、$v=c_{kv}W_{UV}$：`[B, T, H, D_h]`，只在 prefill 临时算
- query 也走低秩：$c_q=hW_{DQ}$，$q_c=c_qW_{UQ}$，$q_r=\mathrm{RoPE}(c_qW_{QR})$ 每头一份

打分是内容项加位置项，缩放用 $\sqrt{D_h+D_r}$：

$$
s_{t,j}^{(i)}=\frac{q_{c,t}^{(i)\top}k_{c,j}^{(i)}+q_{r,t}^{(i)\top}k_{r,j}}{\sqrt{D_h+D_r}}.
$$

吸收靠的是结合律。第 $i$ 头 $q_c^{(i)\top}(W_{UK}^{(i)}c_j)=(W_{UK}^{(i)\top}q_c^{(i)})^\top c_j$，先把 query 投到 $d_c$ 维，再和 latent 点积。输出同理，$\sum_j a_j W_{UV}^{(i)}c_j=W_{UV}^{(i)}\sum_j a_j c_j$，先在 latent 上加权求和，最后再上投影。RoPE 的旋转矩阵 $R_t$ 跟位置有关，夹在 $q$ 和 $W_{UK}$ 中间就没法提前合并，所以位置信息只放在单独的 $D_r$ 维上。

```python
import torch
import torch.nn.functional as F

def rope(x, pos, base=10000.0):
    # x: [B,T,...,D], pos: [T]
    half = x.shape[-1] // 2
    freq = base ** (-torch.arange(half, dtype=x.dtype) / half)
    ang = pos[:, None].to(x.dtype) * freq                     # [T,half]
    shape = (1, x.shape[1]) + (1,) * (x.dim() - 3) + (half,)
    cos, sin = ang.cos().view(shape), ang.sin().view(shape)
    x1, x2 = x[..., :half], x[..., half:]
    return torch.cat([x1 * cos - x2 * sin, x1 * sin + x2 * cos], -1)

class MLA(torch.nn.Module):
    def __init__(self, d, H, Dh, Dr, dc, dq):
        super().__init__()
        self.H, self.Dh, self.Dr = H, Dh, Dr
        L = lambda i, o: torch.nn.Linear(i, o, bias=False)
        self.w_dq, self.w_uq, self.w_qr = L(d, dq), L(dq, H * Dh), L(dq, H * Dr)
        self.w_dkv, self.w_kr = L(d, dc), L(d, Dr)
        self.w_uk, self.w_uv = L(dc, H * Dh), L(dc, H * Dh)
        self.w_o = L(H * Dh, d)
        self.scale = (Dh + Dr) ** -0.5

    def _q(self, h, pos):
        B, T, _ = h.shape
        cq = self.w_dq(h)
        q_c = self.w_uq(cq).view(B, T, self.H, self.Dh)
        q_r = rope(self.w_qr(cq).view(B, T, self.H, self.Dr), pos)
        return q_c, q_r                                        # [B,T,H,Dh], [B,T,H,Dr]

    def prefill(self, h):
        B, T, _ = h.shape
        pos = torch.arange(T)
        q_c, q_r = self._q(h, pos)
        c_kv = self.w_dkv(h)                                   # [B,T,dc]
        k_r = rope(self.w_kr(h), pos)                          # [B,T,Dr]
        k_c = self.w_uk(c_kv).view(B, T, self.H, self.Dh)
        v = self.w_uv(c_kv).view(B, T, self.H, self.Dh)
        s = torch.einsum('bthd,bshd->bhts', q_c, k_c) + torch.einsum('bthd,bsd->bhts', q_r, k_r)
        mask = torch.ones(T, T, dtype=torch.bool).triu(1)
        a = F.softmax((s * self.scale).masked_fill(mask, float('-inf')), -1)
        o = torch.einsum('bhts,bshd->bthd', a, v).reshape(B, T, -1)
        return self.w_o(o), (c_kv, k_r)

    def decode(self, h, cache):
        # h: [B,1,d]; cache: c_kv [B,S,dc], k_r [B,S,Dr]
        c_kv, k_r = cache
        B, S = h.shape[0], c_kv.shape[1]
        pos = torch.tensor([S])
        c_kv = torch.cat([c_kv, self.w_dkv(h)], 1)
        k_r = torch.cat([k_r, rope(self.w_kr(h), pos)], 1)
        q_c, q_r = self._q(h, pos)
        W_uk = self.w_uk.weight.view(self.H, self.Dh, -1)      # [H,Dh,dc]
        W_uv = self.w_uv.weight.view(self.H, self.Dh, -1)      # [H,Dh,dc]
        q_lat = torch.einsum('bhd,hdc->bhc', q_c[:, 0], W_uk)  # [B,H,dc]
        s = torch.einsum('bhc,bsc->bhs', q_lat, c_kv) + torch.einsum('bhd,bsd->bhs', q_r[:, 0], k_r)
        a = F.softmax(s * self.scale, -1)                      # [B,H,S+1]
        o_lat = torch.einsum('bhs,bsc->bhc', a, c_kv)          # [B,H,dc]
        o = torch.einsum('bhc,hdc->bhd', o_lat, W_uv).reshape(B, 1, -1)
        return self.w_o(o), (c_kv, k_r)
```

`nn.Linear` 的 weight 是 `[out, in]`，所以 `view(H, Dh, dc)` 正好把第 $i$ 头的 $W_{UK}^{(i)}$ 切出来。验证方法：同一段序列整段 `prefill` 的输出，应该等于先 prefill 前半段、再逐 token `decode` 的输出，float64 下 `allclose`。

## Cache 大小

每 token 每层存的元素数：

| 方案 | 每 token 每层 |
| --- | --- |
| MHA | $2HD_h$ |
| GQA | $2H_{kv}D_h$ |
| MLA | $d_c+D_r$ |

DeepSeek-V2 取 $H=128$、$D_h=128$、$d_c=4D_h=512$、$D_r=D_h/2=64$。MHA 每 token 每层 32768 个数，MLA 只有 576 个，相当于 $4.5D_h$，论文说这大约等于只有 2.25 组的 GQA，但效果比 MHA 还好。GQA 的对齐写法见 `code-gqa`。

## 追问

- **prefill 为什么不也走吸收？** 吸收后每头 query 和打分都在 $d_c$ 维上做，$d_c=512$ 比 $D_h=128$ 大，FLOPs 更多。Prefill 是算力瓶颈，还原 K/V 再算更划算；decode 是带宽瓶颈，少读 cache 比多几倍 FLOPs 值钱。
- **$W_{UV}$ 还能再往后吸收吗？** 可以，$W_{UV}^{(i)}$ 和 $W_O$ 里对应第 $i$ 头的那一块可以预先乘成一个 $d_c\times d$ 的矩阵，推理时 `o_lat` 直接乘它，完全不用物化每头的 $v$。
- **$k_r$ 为什么所有头共享？** 它只负责位置信息，每头一份的话 cache 要多 $HD_r$，直接把 MLA 省下的空间吃掉一大块。共享后只多 $D_r$ 个数。
- **query 为什么也做低秩压缩？** 不影响 cache，只是训练时省激活显存。手写时可以直接 $q=hW_Q$，面试官一般不卡这个。
- **吸收以后还能用 FlashAttention 吗？** 打分可以看成 $d_c+D_r$ 维的 query 对 $d_c+D_r$ 维的 key（把 $c_{kv}$ 和 $k_r$ 拼起来），value 就是 $c_{kv}$ 本身，相当于一个 $H$ 个 query 头、1 个 KV 头的 MQA，kernel 按 MQA 写就行。
