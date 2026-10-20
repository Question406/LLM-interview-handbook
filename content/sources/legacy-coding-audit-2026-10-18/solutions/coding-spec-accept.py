import math

import torch
import torch.nn.functional as F


def residual_probs(p_logits, q_logits):
    """拒绝后重采样用的残差分布 normalize(max(p - q, 0))。[V] -> [V]。

    p == q 时残差全为 0，按规则此时不可能发生拒绝，所以直接报错，不返回假分布。
    """
    p = F.softmax(p_logits.float(), dim=-1)
    q = F.softmax(q_logits.float(), dim=-1)
    residual = (p - q).clamp(min=0)
    total = residual.sum()
    if total <= 0:
        raise ValueError("no residual mass: rejection is impossible when p == q")
    return residual / total


def spec_accept(draft_ids, log_p, log_q, p_logits, q_logits, bonus_logits):
    """投机解码的验证步：从左到右按 min(1, p/q) 接受草稿 token。

    draft_ids, log_p, log_q: [gamma]，草稿 token 及其在目标 / 草稿模型下的 logprob。
    p_logits, q_logits: [gamma, V]，每个草稿位置的条件分布；bonus_logits: [V]，全部接受后的下一步。
    返回 (输出 token 列表, 拒绝位置 i 或 None)。第一次拒绝时在位置 i 从残差抽一个 token 并停止；
    全部接受（包括 gamma == 0）时再从 bonus 分布多抽一个。
    """
    output = []
    for i in range(draft_ids.numel()):
        accept_prob = torch.exp(log_p[i] - log_q[i]).clamp(max=1.0)   # 在 log 域相减
        if torch.rand(()) < accept_prob:
            output.append(int(draft_ids[i]))
            continue
        corrected = int(torch.multinomial(residual_probs(p_logits[i], q_logits[i]), 1))
        output.append(corrected)
        return output, i
    bonus = int(torch.multinomial(F.softmax(bonus_logits.float(), dim=-1), 1))
    output.append(bonus)
    return output, None


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)
torch.manual_seed(2)
uniform = torch.tensor([[0.0, 0.0], [0.0, 0.0]])
half = torch.tensor([-math.log(2)] * 2)
only_token_0 = torch.tensor([0.0, -float("inf")])

# p == q：草稿全部接受，再追加 bonus（bonus 分布只能抽到 0）
tokens, reject_at = spec_accept(torch.tensor([0, 1]), half, half, uniform, uniform, only_token_0)
assert tokens == [0, 1, 0]
assert reject_at is None

# gamma = 0：没有草稿，仍从 bonus 分布抽一个
tokens, reject_at = spec_accept(torch.tensor([], dtype=torch.long), torch.zeros(0), torch.zeros(0),
                                torch.zeros(0, 2), torch.zeros(0, 2), only_token_0)
assert tokens == [0]
assert reject_at is None

# p 对草稿 token 的概率为 0：第 0 步必拒绝，从残差抽到 token 0，后面的草稿丢弃
p_row = torch.tensor([0.0, -float("inf")])
q_row = torch.tensor([0.0, 0.0])
tokens, reject_at = spec_accept(torch.tensor([1, 1]), torch.tensor([-float("inf"), 0.0]), half,
                                torch.stack([p_row, p_row]), torch.stack([q_row, q_row]), only_token_0)
assert tokens == [0]
assert reject_at == 0

# 单步采样的输出分布服从 p，而不是 q
p = torch.tensor([0.8, 0.2])
q = torch.tensor([0.2, 0.8])
samples = []
for _ in range(5000):
    draft = torch.multinomial(q, 1)
    token = int(draft[0])
    out, _ = spec_accept(draft, p[token].log()[None], q[token].log()[None], p.log()[None], q.log()[None], p.log())
    samples.append(out[0])
assert abs(samples.count(0) / len(samples) - 0.8) < 0.025

# p == q 时残差全 0，不能当成合法分布
expect_value_error(residual_probs, torch.zeros(2), torch.zeros(2))
