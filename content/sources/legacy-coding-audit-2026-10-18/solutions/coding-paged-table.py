import torch


class PagedKV:
    """分页 KV cache：物理页池 [n_blocks, H, block_size, D] + 每条序列一张逻辑页 -> 物理块的表。"""

    def __init__(self, n_blocks, n_heads, block_size, dim):
        if min(n_blocks, n_heads, block_size, dim) < 1:
            raise ValueError(
                f"all sizes must be >= 1, got n_blocks={n_blocks}, n_heads={n_heads}, "
                f"block_size={block_size}, dim={dim}"
            )
        self.block_size = block_size
        self.k = torch.zeros(n_blocks, n_heads, block_size, dim)
        self.v = torch.zeros_like(self.k)
        self.free = list(range(n_blocks))

    def append_token(self, table, seq_lens, k_t, v_t):
        """给每条序列追加一个 token。table: [B, max_pages]，seq_lens: [B]，k_t/v_t: [B, H, 1, D]。

        先检查完所有序列再提交，出错时 table、seq_lens 和空闲列表都不变。
        """
        batch = len(seq_lens)
        n_heads, dim = self.k.shape[1], self.k.shape[-1]
        expected = (batch, n_heads, 1, dim)
        if k_t.shape != expected or v_t.shape != expected:
            raise ValueError(f"k_t/v_t must have shape {expected}, got {tuple(k_t.shape)}, {tuple(v_t.shape)}")

        # 第一阶段：只读，规划每条序列写到哪一页、哪个偏移
        plan = []
        blocks_needed = 0
        for row in range(batch):
            pos = int(seq_lens[row])
            page, offset = divmod(pos, self.block_size)
            if pos < 0 or page >= table.shape[1]:
                raise ValueError(f"sequence {row} exceeds max_pages={table.shape[1]}")
            if offset == 0:
                blocks_needed += 1  # 当前页写满（或还没有页），需要一个新块
            else:
                block = int(table[row, page])
                if not 0 <= block < len(self.k):
                    raise ValueError(f"sequence {row} has no valid block for page {page}")
            plan.append((row, page, offset))
        if blocks_needed > len(self.free):
            raise MemoryError(f"need {blocks_needed} free KV blocks, only {len(self.free)} left")

        # 第二阶段：提交
        for row, page, offset in plan:
            if offset == 0:
                table[row, page] = self.free.pop()
            block = int(table[row, page])
            self.k[block, :, offset] = k_t[row, :, 0]
            self.v[block, :, offset] = v_t[row, :, 0]
            seq_lens[row] += 1

    def gather_seq(self, table_row, seq_len):
        """按逻辑页顺序拼出一条序列的 (k, v)，形状 [H, seq_len, D]。"""
        if seq_len < 0:
            raise ValueError(f"seq_len must be non-negative, got {seq_len}")
        n_heads, dim = self.k.shape[1], self.k.shape[-1]
        n_pages = (seq_len + self.block_size - 1) // self.block_size
        if n_pages > len(table_row):
            raise ValueError(f"seq_len={seq_len} needs {n_pages} pages, table has {len(table_row)}")
        blocks = table_row[:n_pages].long()
        if bool(((blocks < 0) | (blocks >= len(self.k))).any()):
            raise ValueError(f"page table has invalid block ids: {blocks.tolist()}")
        if seq_len == 0:
            return self.k.new_empty((n_heads, 0, dim)), self.v.new_empty((n_heads, 0, dim))
        # [pages, H, block_size, D] -> [H, pages, block_size, D] -> [H, pages * block_size, D]
        k = self.k[blocks].transpose(0, 1).reshape(n_heads, -1, dim)[:, :seq_len]
        v = self.v[blocks].transpose(0, 1).reshape(n_heads, -1, dim)[:, :seq_len]
        return k, v


torch.set_num_threads(1)


def expect_error(error_type, action):
    try:
        action()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def token(value, batch=1):
    return torch.full((batch, 1, 1, 1), float(value))


# 一条序列追加 3 个 token：用 2 个物理块，gather 按顺序取回
cache = PagedKV(4, 1, 2, 1)
table = torch.full((1, 3), -1)
lens = torch.zeros(1, dtype=torch.long)
for value in (1.0, 2.0, 3.0):
    cache.append_token(table, lens, token(value), token(value * 10))
k, v = cache.gather_seq(table[0], 3)
assert k.flatten().tolist() == [1, 2, 3]
assert v.flatten().tolist() == [10, 20, 30]
assert len(cache.free) == 2
assert table[0, 2] == -1

# 长度 0 合法，返回空张量
assert cache.gather_seq(table[0], 0)[0].shape == (1, 0, 1)

# 空闲块不够：MemoryError，所有状态不变
cache = PagedKV(1, 1, 2, 1)
table = torch.full((2, 1), -1)
lens = torch.zeros(2, dtype=torch.long)
expect_error(MemoryError, lambda: cache.append_token(table, lens, torch.ones(2, 1, 1, 1), torch.ones(2, 1, 1, 1)))
assert lens.tolist() == [0, 0]
assert torch.all(table == -1)
assert len(cache.free) == 1

# 两条序列交替追加：物理块号不连续，gather 仍按逻辑顺序拼接
cache = PagedKV(4, 1, 1, 1)
table = torch.full((2, 2), -1)
lens = torch.zeros(2, dtype=torch.long)
cache.append_token(table, lens, torch.tensor([1.0, 5.0]).view(2, 1, 1, 1), torch.zeros(2, 1, 1, 1))
cache.append_token(table, lens, torch.tensor([2.0, 6.0]).view(2, 1, 1, 1), torch.zeros(2, 1, 1, 1))
assert cache.gather_seq(table[0], 2)[0].flatten().tolist() == [1, 2]
assert cache.gather_seq(table[1], 2)[0].flatten().tolist() == [5, 6]
assert table.tolist() == [[3, 1], [2, 0]]  # 空闲列表从末尾弹出，每条序列拿到的块号不相邻

# 第二条序列超出 max_pages：ValueError，第一条序列也不会被写入
cache = PagedKV(2, 1, 2, 1)
table = torch.full((2, 1), -1)
lens = torch.tensor([0, 2])
expect_error(ValueError, lambda: cache.append_token(table, lens, token(9, 2), token(9, 2)))
assert lens.tolist() == [0, 2]
assert torch.all(table == -1)
assert len(cache.free) == 2

# token 形状不对、gather 越界、构造参数非法
cache = PagedKV(2, 2, 2, 3)
table = torch.full((1, 1), -1)
lens = torch.zeros(1, dtype=torch.long)
expect_error(ValueError, lambda: cache.append_token(table, lens, torch.ones(1, 1, 1, 3), torch.ones(1, 1, 1, 3)))
expect_error(ValueError, lambda: cache.gather_seq(table[0], 3))
expect_error(ValueError, lambda: cache.gather_seq(table[0], 1))
expect_error(ValueError, lambda: cache.gather_seq(table[0], -1))
expect_error(ValueError, lambda: PagedKV(0, 1, 1, 1))
