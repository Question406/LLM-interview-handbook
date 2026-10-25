---
id: code-mla-cache
section: coding
order: 20
level: S
title: 手写 MLA：只缓存 latent，decode 时把 $W_{UK}$ / $W_{UV}$ 吸收掉
quick: "cache 里只存每个 token 的 $d_c$ 维 latent $c_{kv}$，加上各头共享的 $D_r$ 维 RoPE key。decode 时把 $W_{UK}$ 吸收进 query、把 $W_{UV}$ 挪到输出端，直接在 latent 上做 attention，不用把 K/V 还原出来。"
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

## 题目描述

实现一个小型 Multi-head Latent Attention 模块，比较整段因果前向与带压缩 KV cache 的逐 token 解码。这是手册独立张量练习，不要求复刻完整模型或推理框架。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `MLA(d,H,Dh,Dr,dc,dq)`，所有投影无 bias；Dr 为正偶数，其余维度为正。`prefill(h)` 输入 [B,T,d]；`decode(h,cache)` 输入一个新 token [B,1,d]。

### 输出与约束

prefill 返回 `(o,(c_kv,k_r))`：o 为 [B,T,d]，两项缓存为 [B,T,dc] 与 [B,T,Dr]。decode 接收历史长S的同结构缓存，返回 [B,1,d] 输出及历史长S+1的新缓存。使用因果注意力，旋转位置按绝对位置递增；缓存保存压缩潜变量和共享旋转key，不按头展开完整KV。

### 数学契约与参数名

全部线性层都采用 PyTorch `nn.Linear` 的约定：权重为 `[out,in]`，输入右乘权重转置，均无 bias。模块必须具有以下参数名和尺寸：`w_dq: d→dq`、`w_uq: dq→H*Dh`、`w_qr: dq→H*Dr`、`w_dkv: d→dc`、`w_kr: d→Dr`、`w_uk: dc→H*Dh`、`w_uv: dc→H*Dh`、`w_o: H*Dh→d`。

对于输入 token 向量 h，先定义查询潜变量 `c_q=w_dq(h)`，内容查询 `q_c=reshape(w_uq(c_q),[H,Dh])`，位置查询 `q_r=RoPE(reshape(w_qr(c_q),[H,Dr]),位置)`。KV 潜变量 `c_kv=w_dkv(h)`，内容 key `k_c=reshape(w_uk(c_kv),[H,Dh])`，value `v=reshape(w_uv(c_kv),[H,Dh])`；共享位置 key 为 `k_r=RoPE(w_kr(h),位置)`，没有头维。

此卡 RoPE 使用前后半维配对，而非相邻偶奇维配对。令 m=Dr/2，对 r=0,…,m-1，位置p的角度为 `theta=p*10000^(-r/m)`；将第r维a和第r+m维b变为 `(a*cos(theta)-b*sin(theta), a*sin(theta)+b*cos(theta))`，结果仍按前半、后半顺序排列。所有头共享相同频率。

第i头的 query 位置t对key位置j的分数定义为 `(dot(q_c[t,i],k_c[j,i])+dot(q_r[t,i],k_r[j]))/sqrt(Dh+Dr)`。对所有可见j做softmax，再以这些概率加权对应 `v[j,i]`；按头编号拼接得到H*Dh维向量，经 `w_o` 得到最终输出。prefill只允许j≤t；decode把当前token加入缓存后允许读取全部历史及自身。prefill位置从0开始，历史长S的decode新位置为S。非零权重时，decode输出必须等于同一序列完整prefill的最后位置输出；压缩缓存约束始终成立。

### 示例

```text
取 B=1,T=2,d=4,H=2,Dh=2,Dr=2,dc=dq=2，所有投影权重设为0
prefill任意h -> o为[1,2,4]全零；cache形状分别[1,2,2]、[1,2,2]。
再decode一个token -> 输出[1,1,4]全零，缓存时间长度均为3。
```

## 解题思路与参考答案

MLA 的 cache 里只放两样东西：每个 token 的 $d_c$ 维 latent $c_{kv}$，和所有头共享的 $D_r$ 维 RoPE key。逐 token 生成（decode）时把 $W_{UK}$ 吸收进 query、把 $W_{UV}$ 挪到输出端，attention 直接在 latent 上算，每步读的 cache 就很小。原理见 `arch-mla`，普通 MHA 的写法见 `code-attention`。

面试官主要看三件事：cache 里到底存什么，decoupled RoPE 为什么要单独拆出来，吸收之后的 decode 和输入预填充（prefill，即处理输入并建立缓存）是否逐位相等。最常见的两种错法正好对着前两件。一种是把 RoPE 直接加在上投影出来的 $k_c=W_{UK}c_{kv}$ 上，这样 $W_{UK}$ 就再也吸收不进 query，decode 时每步还得把整段 latent 还原成 K，低维 cache 省读取量的收益也就没了。另一种是 cache 里存了还原后的 K/V，那只是换了个参数化的 MHA。

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

吸收靠的是结合律。第 $i$ 头有 $q_c^{(i)\top}(W_{UK}^{(i)}c_j)=(W_{UK}^{(i)\top}q_c^{(i)})^\top c_j$，也就是先把 query 投到 $d_c$ 维，再和 latent 点积。输出同理，$\sum_j a_j W_{UV}^{(i)}c_j=W_{UV}^{(i)}\sum_j a_j c_j$，先在 latent 上加权求和，最后再上投影。RoPE 的旋转矩阵 $R_t$ 跟位置有关，夹在 $q$ 和 $W_{UK}$ 中间就没法提前合并，所以位置信息只放在单独的 $D_r$ 维上。

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

`nn.Linear` 的 weight 是 `[out, in]`，所以 `view(H, Dh, dc)` 正好把第 $i$ 头的 $W_{UK}^{(i)}$ 切出来。验证的办法是拿同一段序列，整段 `prefill` 的输出应该等于先 prefill 前半段、再逐 token `decode` 的输出，float64 下 `allclose`。

## Cache 大小

每 token 每层存的元素数：

| 方案 | 每 token 每层 |
| --- | --- |
| MHA | $2HD_h$ |
| GQA | $2H_{kv}D_h$ |
| MLA | $d_c+D_r$ |

DeepSeek-V2 取 $H=128$、$D_h=128$、$d_c=4D_h=512$、$D_r=D_h/2=64$。MHA 每 token 每层要存 32768 个数，MLA 只有 576 个，相当于 $4.5D_h$。论文说这大约等于只有 2.25 组的 GQA，效果却比 MHA 还好。GQA 的对齐写法见 `code-gqa`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

固定权重随机种子，对同一段输入比较整段 prefill 与先 prefill 两个 token 再 decode 一个 token。末位输出一致，且压缩 cache 长度从 2 变成 3。

```python
torch.manual_seed(7)
model = MLA(d=4, H=2, Dh=2, Dr=2, dc=2, dq=2).eval()
x = torch.randn(1, 3, 4)
with torch.no_grad():
    full, _ = model.prefill(x)
    _, cache = model.prefill(x[:, :2])
    last, cache = model.decode(x[:, 2:], cache)
torch.testing.assert_close(last, full[:, -1:], atol=1e-6, rtol=1e-5)
assert cache[0].shape == (1, 3, 2) and cache[1].shape == (1, 3, 2)
print("simple tests passed")
```

## 追问

**prefill 为什么不也走吸收？**
吸收以后每头的 query 和打分都在 $d_c$ 维上做，$d_c=512$ 比 $D_h=128$ 大，FLOPs 更多。Prefill 是算力瓶颈，还原 K/V 再算更划算；decode 是带宽瓶颈，少读 cache 比多几倍 FLOPs 值钱。

**$W_{UV}$ 还能再往后吸收吗？**
能。$W_{UV}^{(i)}$ 和 $W_O$ 里对应第 $i$ 头的那一块可以预先乘成一个 $d_c\times d$ 的矩阵，推理时 `o_lat` 直接乘它，每头的 $v$ 完全不用物化。

**$k_r$ 为什么所有头共享？**
它只负责位置信息。每头一份的话 cache 要多 $HD_r$，直接把 MLA 省下的空间吃掉一大块；共享以后只多 $D_r$ 个数。

**query 为什么也做低秩压缩？**
这和 cache 没关系，只是训练时省激活显存。手写时直接 $q=hW_Q$ 也行，面试官一般不卡这个。

**吸收以后还能用 FlashAttention 吗？**
能。打分可以看成 $d_c+D_r$ 维的 query 对 $d_c+D_r$ 维的 key（把 $c_{kv}$ 和 $k_r$ 拼起来），value 就是 $c_{kv}$ 本身，相当于一个 $H$ 个 query 头、1 个 KV 头的 MQA，kernel 按 MQA 写就行。
