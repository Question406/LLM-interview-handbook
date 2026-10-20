import torch
from torch import nn


def embed_forward(embed, ids, pad_id=0):
    """查表并标出 pad 位置。

    ids: [B, T] 合法词表下标 -> (x: [B, T, D], pad: [B, T] bool，True 表示 pad)。
    """
    x = embed(ids)
    pad = ids.eq(pad_id)
    return x, pad


def attn_pad_mask(pad):
    """把 pad: [B, S] 变成可广播到 scores [B, H, T, S] 的 key mask [B, 1, 1, S]。

    True 表示屏蔽这个 key（和 keep-mask 的约定相反），用法：scores.masked_fill(mask, -inf)。
    """
    return pad[:, None, None, :]


class SmallLM(nn.Module):
    """只有 embedding 的最小模型：padding_idx 那一行保持 0，梯度也为 0。"""

    def __init__(self, vocab, dim, pad=0):
        super().__init__()
        self.pad = pad
        self.embed = nn.Embedding(vocab, dim, padding_idx=pad)

    def forward(self, ids):
        x, pad = embed_forward(self.embed, ids, self.pad)
        # 后续 attention 里：scores = scores.masked_fill(attn_pad_mask(pad), float("-inf"))
        return x, pad


torch.set_num_threads(1)
model = SmallLM(5, 3, pad=0)
ids = torch.tensor([[1, 0], [2, 0]])

# 输出形状 [B, T, D]，pad 位置的向量是 0
x, pad = model(ids)
assert x.shape == (2, 2, 3)
assert torch.all(x[:, 1] == 0)
assert pad.tolist() == [[False, True], [False, True]]

# key mask 能广播到 [B, H, T, S]
mask = attn_pad_mask(pad)
assert mask.shape == (2, 1, 1, 2)

# 零向量 key 不加 mask 仍会分到正的注意力权重；加 mask 后为 0
scores = torch.zeros(2, 1, 2, 2)
assert torch.all(scores.softmax(-1)[..., 1] > 0)
masked = scores.masked_fill(mask, float("-inf")).softmax(-1)
assert torch.all(masked[..., 1] == 0)

# padding_idx 那一行梯度为 0；其他被查到一次的行梯度为 1
x.sum().backward()
assert torch.all(model.embed.weight.grad[0] == 0)
assert torch.all(model.embed.weight.grad[1] == 1)

# 没被查到的行梯度为 0（反向只累加出现过的行）
assert torch.all(model.embed.weight.grad[3:] == 0)
