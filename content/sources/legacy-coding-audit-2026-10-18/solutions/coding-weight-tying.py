import torch
import torch.nn.functional as F
from torch import nn


class TiedLM(nn.Module):
    """embedding 和无 bias 的 lm_head 共享同一个 [V, D] Parameter 的最小语言模型。"""

    def __init__(self, vocab, dim, pad=0):
        super().__init__()
        self.pad = pad
        self.embed = nn.Embedding(vocab, dim, padding_idx=pad)
        self.ln = nn.LayerNorm(dim)
        self.lm_head = nn.Linear(dim, vocab, bias=False)
        self.lm_head.weight = self.embed.weight  # 共享同一个 Parameter，不是复制数值

    def forward(self, ids, targets=None):
        """ids: [B, T]。不给 targets 时返回 logits [B, T, V]；
        给 targets 时把位置 t 的 logits 和 targets[:, t + 1] 对齐，返回忽略 pad 的平均 CE。
        """
        hidden = self.ln(self.embed(ids))  # [B, T, D]
        logits = self.lm_head(hidden)      # [B, T, V]，即 hidden @ E^T
        if targets is None:
            return logits
        if targets.shape != ids.shape or ids.shape[1] < 2:
            raise ValueError("targets must match ids with T >= 2, got "
                             f"{tuple(targets.shape)} vs {tuple(ids.shape)}")
        shifted_targets = targets[:, 1:]
        if not (shifted_targets != self.pad).any():
            raise ValueError("no non-pad target after shifting")
        return F.cross_entropy(
            logits[:, :-1].reshape(-1, logits.size(-1)),
            shifted_targets.reshape(-1),
            ignore_index=self.pad,
        )


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("invalid input should raise ValueError")


torch.manual_seed(0)
torch.set_num_threads(1)
model = TiedLM(7, 4, pad=0)
ids = torch.tensor([[1, 2, 3], [2, 4, 0]])

# 两个模块拿的是同一个 Parameter，parameters() 里只出现一次
assert model.embed.weight is model.lm_head.weight
assert sum(p is model.embed.weight for p in model.parameters()) == 1

# 反向后两边看到的是同一份梯度
loss = model(ids, ids)
assert torch.isfinite(loss)
loss.backward()
assert model.embed.weight.grad is model.lm_head.weight.grad

# 共享梯度 = 查表路径梯度 + 输出投影路径梯度：用两份数值相同的独立参数对照
untied = TiedLM(7, 4, pad=0)
untied.load_state_dict(model.state_dict())
untied.lm_head.weight = nn.Parameter(model.embed.weight.detach().clone())
untied(ids, ids).backward()
path_sum = untied.embed.weight.grad + untied.lm_head.weight.grad
assert torch.allclose(model.embed.weight.grad, path_sum, atol=1e-6)

# padding_idx 只挡住查表那一路；输出那一路仍会给 pad 行梯度
assert torch.all(untied.embed.weight.grad[0] == 0)
assert untied.lm_head.weight.grad[0].abs().sum() > 0

# 改 embedding 的一行，lm_head 同一行跟着变：两者是同一块内存
with torch.no_grad():
    model.embed.weight[1].fill_(3)
assert torch.all(model.lm_head.weight[1] == 3)

# pad 不是 0 时也按 pad 忽略：只有 1 个有效目标，loss 等于这一项的 CE
model5 = TiedLM(7, 4, pad=5)
ids5 = torch.tensor([[1, 2, 5]])
logits = model5(ids5)
expected = F.cross_entropy(logits[0, :1], ids5[0, 1:2])
assert torch.allclose(model5(ids5, ids5), expected)

# 非法输入：T < 2；shift 之后全是 pad
expect_value_error(model, torch.tensor([[1]]), torch.tensor([[1]]))
expect_value_error(model, torch.tensor([[1, 0]]), torch.tensor([[1, 0]]))
