import torch
import torch.nn.functional as F


def _check_inputs(logits, input_ids, temperature):
    if temperature <= 0:
        raise ValueError(f"temperature must be positive, got {temperature}")
    if logits.dim() != 3 or logits.shape[:2] != input_ids.shape:
        raise ValueError(
            f"expected logits [B, L, V] and input_ids [B, L], "
            f"got {tuple(logits.shape)} and {tuple(input_ids.shape)}"
        )


def token_logprobs(logits, input_ids, temperature=1.0):
    """logits [B, L, V]、input_ids [B, L] -> [B, L-1]；第 t 列是 input_ids[:, t+1] 的 logprob。"""
    _check_inputs(logits, input_ids, temperature)
    scaled = logits[:, :-1].float() / temperature  # [B, L-1, V]，位置 t 预测 t+1
    targets = input_ids[:, 1:]                       # [B, L-1]
    picked = scaled.gather(-1, targets.unsqueeze(-1)).squeeze(-1)
    return picked - torch.logsumexp(scaled, dim=-1)


def token_logprobs_chunked(logits, input_ids, temperature=1.0, chunk=1024):
    """和 token_logprobs 相同，但每次只把 chunk 个位置转成 float32。"""
    _check_inputs(logits, input_ids, temperature)
    if chunk < 1:
        raise ValueError(f"chunk must be >= 1, got {chunk}")
    batch, length = input_ids.shape
    n_predictions = length - 1
    if n_predictions <= 0:
        return logits.new_zeros((batch, 0), dtype=torch.float32)

    targets = input_ids[:, 1:]  # [B, L-1]
    pieces = []
    for start in range(0, n_predictions, chunk):
        end = min(start + chunk, n_predictions)
        scaled = logits[:, start:end].float() / temperature  # [B, end-start, V]
        picked = scaled.gather(-1, targets[:, start:end].unsqueeze(-1)).squeeze(-1)
        pieces.append(picked - torch.logsumexp(scaled, dim=-1))
    return torch.cat(pieces, dim=1)


torch.set_num_threads(1)


def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


torch.manual_seed(2)
logits = torch.randn(2, 6, 7)
ids = torch.randint(0, 7, (2, 6))
reference = F.log_softmax(logits[:, :-1] / 0.7, -1).gather(-1, ids[:, 1:, None]).squeeze(-1)

# 和 log_softmax + gather 的参考结果一致（含 shift 和温度）
assert torch.allclose(token_logprobs(logits, ids, 0.7), reference, atol=1e-6)

# 分块大小不整除、等于 1、大于长度时都和不分块一致
for chunk in (1, 2, 4, 20):
    assert torch.allclose(token_logprobs_chunked(logits, ids, 0.7, chunk), reference, atol=1e-6)

# L = 1：没有可预测的 token，返回 [B, 0]
assert token_logprobs_chunked(logits[:, :1], ids[:, :1]).shape == (2, 0)
assert token_logprobs(logits[:, :1], ids[:, :1]).shape == (2, 0)

# 均匀 logits：每个位置都是 -ln V
uniform = token_logprobs(torch.zeros(1, 3, 4), torch.tensor([[0, 1, 2]]))
assert torch.allclose(uniform, torch.full((1, 2), -torch.log(torch.tensor(4.0)).item()))

# bf16 logits 在 float32 里计算，结果是 float32
assert token_logprobs(logits.to(torch.bfloat16), ids).dtype == torch.float32

# 非法参数
expect_value_error(lambda: token_logprobs(logits, ids, 0.0))
expect_value_error(lambda: token_logprobs_chunked(logits, ids, 1.0, 0))
expect_value_error(lambda: token_logprobs(logits, ids[:, :5]))
