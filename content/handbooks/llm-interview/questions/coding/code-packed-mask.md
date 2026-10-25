---
id: code-packed-mask
section: coding
order: 46
level: A
title: 手写 packed sequence 的文档边界 mask：`cu_seqlens` 怎么变成 keep 矩阵
quick: "用前缀和 `cu_seqlens` 给每个位置算出所属的 doc id，keep 的条件是同一文档且 $j\\le i$。跨文档的位置要设成 $-\\infty$，否则后一条样本能看到前一条。"
tags:
  - Packing
  - Attention
  - Mask
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: FlashAttention-2
    url: https://arxiv.org/abs/2307.08691
    type: primary
---

## 题目描述

多个独立文档被直接拼接成一个 token 序列。请生成可见性 mask，使每个 token 只能看到同一文档内自己及之前的 token，既不能跨文档读取，也不能读取未来。

### 接口与输入输出

输入 cu 为一维整数张量，是各文档边界的累计 token 数：首项为 0，后一项减前一项得到对应文档长度，末项为总长 T。保证边界非递减且合法。

- `cu_seqlens_to_doc(cu)` 返回 `[T]` 的文档编号，文档编号从 0 开始，按拼接顺序递增。
- `packed_keep(cu)` 返回 `[T,T]` 的布尔张量，行是 query、列是 key，True 表示可见。输出与 cu 位于同一设备。

### 示例

```text
cu=[0,2,3]，表示两个文档，长度分别为2和1
文档编号 -> [0,0,1]
可见性矩阵 ->
[[True, False,False],
 [True, True, False],
 [False,False,True]]
```

第三个 token 不能看到前两个，即使它们在整个拼接序列中出现得更早。

## 解题思路与参考答案

packed sequence 的 mask 就是在因果 mask 上再加一个「同一文档」的条件：先用 `cu_seqlens` 给每个位置算出 doc id，只有 doc id 相同、而且 $j\le i$ 的位置才保留。packing 把多条样本拼在一起，是为了少放 padding；如果只加因果 mask、不管文档边界，后一条样本的输入提示（prompt）就能看到前一条样本，信息就泄漏了。计算损失时也一样要按文档划分，padding 和文档衔接处的 label 设成 `ignore_index`。

举个例子，`cu = [0, 3, 7]` 表示两段，长度分别是 3 和 4。用 `repeat_interleave` 展开，得到每个位置的 doc id `[0,0,0,1,1,1,1]`。第 4 个位置（下标 3）属于第二段，它不能看下标 0 到 2。写成公式是

$$
\mathrm{keep}(i,j)=\big[\mathrm{doc}(i)=\mathrm{doc}(j)\big]\land[j\le i].
$$

```python
import torch

def cu_seqlens_to_doc(cu):
    lens = cu[1:] - cu[:-1]
    return torch.repeat_interleave(torch.arange(len(lens), device=cu.device), lens)

def packed_keep(cu):
    doc = cu_seqlens_to_doc(cu)
    T = doc.numel()
    q = torch.arange(T, device=cu.device)
    return (doc[:, None] == doc[None, :]) & (q[:, None] >= q[None, :])
```

生产实现不会真的建一个完整的 $[T,T]$ 矩阵，FlashAttention 的 varlen kernel 会根据 `cu_seqlens` 分段计算。白板上可以先写 dense mask，再说明实际 kernel 怎么避开它。RoPE 的 position 也要按段内从 0 重新数，或者用每条样本自己的 position id，不能用拼接后的列下标。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

两个文档长度分别为 2 和 1，最后一个 token 不能看到前一文档。手写块对角因果矩阵，同时检查文档编号的展开。

```python
cu = torch.tensor([0, 2, 3])
assert cu_seqlens_to_doc(cu).tolist() == [0, 0, 1]
expected = torch.tensor([[1, 0, 0], [1, 1, 0], [0, 0, 1]], dtype=torch.bool)
assert torch.equal(packed_keep(cu), expected)
print("simple tests passed")
```

## 追问

**loss 怎么 shift？**
每段自己做 `logits[:-1]` 对 `idx[1:]`。段尾不能去预测下一段的第一个 token，这个 label 要屏蔽掉。

**和 left padding 的 batch 有什么区别？**
padding 是按 batch 维对齐，packing 是沿时间维拼接。两种都能去掉多余的 pad，packing 的有效 token 比例更高。

**逐 token 生成（decode）还用 packing 吗？**
一般不用。推理走 continuous batching 加 paged KV，见 `code-paged-kv-cow`。
