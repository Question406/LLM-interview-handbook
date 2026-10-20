import torch

INT32_MAX = 2**31 - 1


def cu_seqlens_from_lens(lens):
    """[B] 长度 -> [B+1] int32 前缀和，cu[0] = 0。"""
    total = int(lens.sum()) if lens.numel() else 0
    if total > INT32_MAX:
        raise ValueError(f"total tokens {total} does not fit in int32")
    cu = torch.zeros(lens.numel() + 1, dtype=torch.int32, device=lens.device)
    cu[1:] = torch.cumsum(lens, 0).to(torch.int32)
    return cu


def pack_tokens(tokens, lens):
    """tokens: [B, T] 右 pad；返回 packed [total] 和 cu [B+1]。"""
    batch_size, max_len = tokens.shape
    if lens.shape != (batch_size,):
        raise ValueError(f"lens shape {tuple(lens.shape)} does not match batch size {batch_size}")
    if lens.numel() and (int(lens.min()) < 0 or int(lens.max()) > max_len):
        raise ValueError(f"lens must lie in [0, {max_len}], got {lens.tolist()}")

    parts = [tokens[b, :int(lens[b])] for b in range(batch_size)]
    packed = torch.cat(parts, dim=0) if parts else tokens.new_empty((0,))
    cu = cu_seqlens_from_lens(lens)
    if int(cu[-1]) != packed.size(0):
        raise ValueError("cu_seqlens does not match the packed length")
    return packed, cu


def doc_causal_keep(doc_ids):
    """doc_ids: [T]，同一文档连续出现。返回 [T, T]，True 表示 i 可以看 j（同文档且 j <= i）。"""
    seq_len = doc_ids.numel()
    if seq_len:
        starts = 1 + int((doc_ids[1:] != doc_ids[:-1]).sum())
        if starts != doc_ids.unique().numel():
            raise ValueError("each doc id must appear in one contiguous run")
    causal = torch.tril(torch.ones(seq_len, seq_len, dtype=torch.bool))
    same_doc = doc_ids[:, None] == doc_ids[None, :]
    return causal & same_doc


torch.set_num_threads(1)


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError from {fn.__name__}")


# 中间夹一条空样本
tokens = torch.tensor([[1, 2, 0], [0, 0, 0], [3, 0, 0]])
packed, cu = pack_tokens(tokens, torch.tensor([2, 0, 1]))
assert packed.tolist() == [1, 2, 3]
assert cu.tolist() == [0, 2, 2, 3]
assert cu.dtype == torch.int32

# B = 0
packed, cu = pack_tokens(torch.empty((0, 3), dtype=torch.long), torch.empty(0, dtype=torch.long))
assert packed.numel() == 0
assert cu.tolist() == [0]

# 长度全为 0
packed, cu = pack_tokens(torch.zeros(2, 3, dtype=torch.long), torch.tensor([0, 0]))
assert packed.numel() == 0
assert cu.tolist() == [0, 0, 0]

# 长度越界或个数不对
expect_value_error(pack_tokens, tokens, torch.tensor([4, 0, 1]))
expect_value_error(pack_tokens, tokens, torch.tensor([-1, 0, 1]))
expect_value_error(pack_tokens, tokens, torch.tensor([1, 1]))

# 块对角因果：第二篇文档看不到第一篇
keep = doc_causal_keep(torch.tensor([0, 0, 1]))
assert keep.tolist() == [[True, False, False], [True, True, False], [False, False, True]]

# 同一个 id 不连续出现时拒绝
expect_value_error(doc_causal_keep, torch.tensor([0, 1, 0]))
