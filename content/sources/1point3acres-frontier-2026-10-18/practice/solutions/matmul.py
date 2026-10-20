from concurrent.futures import ThreadPoolExecutor
from queue import Queue

import numpy as np


def _check_inputs(a, b, world_size):
    a = np.asarray(a, dtype=float)  # [M, K]
    b = np.asarray(b, dtype=float)  # [K, N]
    if type(world_size) is not int or world_size < 1:
        raise ValueError(f"world_size must be a positive int, got {world_size!r}")
    if a.ndim != 2 or b.ndim != 2:
        raise ValueError("a and b must be 2-D")
    if a.shape[1] != b.shape[0]:
        raise ValueError(f"inner dims differ: {a.shape} @ {b.shape}")
    return a, b


def dp_matmul(a, b, world_size):
    """数据并行：每个 rank 拿 a 的一段行和完整的 b，结果按 rank 顺序拼回去。"""
    a, b = _check_inputs(a, b, world_size)
    row_shards = np.array_split(a, world_size, axis=0)  # 允许不整除和空分片
    with ThreadPoolExecutor(world_size) as pool:
        # pool.map 按输入顺序返回，所以拼接顺序就是 rank 顺序
        outputs = list(pool.map(lambda rows: rows @ b, row_shards))
    return np.concatenate(outputs, axis=0)  # [M, N]


def fsdp_matmul(a, b, world_size):
    """FSDP 模拟：a 按行切、b 按列切，b 的列分片沿环传递 world_size - 1 轮。"""
    a, b = _check_inputs(a, b, world_size)
    row_shards = np.array_split(a, world_size, axis=0)
    col_shards = np.array_split(b, world_size, axis=1)
    # 第 r 个列分片对应输出的 [col_offsets[r], col_offsets[r + 1]) 列
    col_offsets = np.cumsum([0] + [shard.shape[1] for shard in col_shards])
    inboxes = [Queue() for _ in range(world_size)]  # 无界队列，put 不会阻塞

    def worker(rank):
        rows = row_shards[rank]
        out = np.zeros((rows.shape[0], b.shape[1]))
        owner, shard = rank, col_shards[rank]
        for step in range(world_size):
            # 消息里带着 owner，才知道这块结果该写到哪几列
            out[:, col_offsets[owner]:col_offsets[owner + 1]] = rows @ shard
            if step + 1 < world_size:
                # 所有 rank 都先发后收，环上每一轮都有消息可取，不会互相等死
                inboxes[(rank + 1) % world_size].put((owner, shard))
                owner, shard = inboxes[rank].get(timeout=10)
        return out

    with ThreadPoolExecutor(world_size) as pool:
        parts = list(pool.map(worker, range(world_size)))
    return np.concatenate(parts, axis=0)  # [M, N]


def backward(a, b, grad_out):
    """Y = A @ B 的反向：给定 dL/dY，返回 (dL/dA, dL/dB) = (G B^T, A^T G)。"""
    a = np.asarray(a, dtype=float)  # [M, K]
    b = np.asarray(b, dtype=float)  # [K, N]
    grad_out = np.asarray(grad_out, dtype=float)  # [M, N]
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[0]:
        raise ValueError(f"bad matmul shapes: {a.shape} @ {b.shape}")
    if grad_out.shape != (a.shape[0], b.shape[1]):
        raise ValueError(f"grad_out shape {grad_out.shape} != {(a.shape[0], b.shape[1])}")
    return grad_out @ b.T, a.T @ grad_out


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    def numeric_grad(loss, x, index, h=1e-5):
        plus = x.copy()
        minus = x.copy()
        plus[index] += h
        minus[index] -= h
        return (loss(plus) - loss(minus)) / (2 * h)

    # 手算的小例子
    a = [[1, 2], [3, 4]]
    b = [[5], [6]]
    assert np.allclose(dp_matmul(a, b, 2), [[17], [39]])
    assert np.allclose(fsdp_matmul(a, b, 2), [[17], [39]])

    # 随机形状：整除、不整除、world_size 大于 N（有空列分片）、单卡
    rng = np.random.default_rng(6)
    for m, k, n, world_size in ((8, 6, 4, 2), (3, 2, 5, 4), (2, 3, 1, 1), (5, 3, 2, 3)):
        a = rng.normal(size=(m, k))
        b = rng.normal(size=(k, n))
        grad_out = rng.normal(size=(m, n))
        assert np.allclose(dp_matmul(a, b, world_size), a @ b)
        assert np.allclose(fsdp_matmul(a, b, world_size), a @ b)

        # 用有限差分核对解析梯度，损失取 sum(Y * G)
        grad_a, grad_b = backward(a, b, grad_out)

        def loss_of_a(x):
            return ((x @ b) * grad_out).sum()

        def loss_of_b(x):
            return ((a @ x) * grad_out).sum()

        for index in ((0, 0), (m - 1, k - 1)):
            assert np.isclose(numeric_grad(loss_of_a, a, index), grad_a[index])
        for index in ((0, 0), (k - 1, n - 1)):
            assert np.isclose(numeric_grad(loss_of_b, b, index), grad_b[index])

    # 非法输入
    expect_value_error(dp_matmul, [[1, 2]], [[1, 2]], 1)
    expect_value_error(fsdp_matmul, [[1]], [[1]], 0)
    expect_value_error(backward, [[1]], [[1]], [[1, 2]])


if __name__ == "__main__":
    test()
