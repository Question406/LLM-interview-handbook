import numpy as np


def as_matrix_stack(matrices):
    """转成 float 数组并检查形状是 [n, D, D]。"""
    stack = np.asarray(matrices, dtype=float)
    if stack.ndim != 3 or stack.shape[1] != stack.shape[2]:
        raise ValueError(f"expected shape [n, D, D], got {stack.shape}")
    return stack


def prefix(matrices):
    """顺序计算有序前缀积：P_i = A_0 @ A_1 @ ... @ A_i。matrices: [n, D, D]。"""
    stack = as_matrix_stack(matrices)
    products = np.empty_like(stack)
    running = np.eye(stack.shape[1])
    for i, matrix in enumerate(stack):
        running = running @ matrix
        products[i] = running
    return products


def scan(matrices):
    """Hillis–Steele 扫描：第 k 层让 out[i] = old[i - 2^k] @ old[i]，共 ceil(log2 n) 层。

    每层都从上一层的副本 old 读，避免同一层里读到刚写入的新值。
    矩阵乘法不满足交换律，左边的块必须放在左边。
    """
    out = as_matrix_stack(matrices).copy()
    step = 1
    while step < len(out):
        old = out.copy()
        for i in range(step, len(out)):
            out[i] = old[i - step] @ old[i]
        step *= 2
    return out


def backward(matrices, upstream):
    """标量 L = sum_i <G_i, P_i> 对每个 A_i 的梯度。matrices 和 upstream 都是 [n, D, D]。

    P_i = P_{i-1} @ A_i，所以 dL/dA_i = P_{i-1}^T @ dL/dP_i，
    并且 dL/dP_{i-1} = G_{i-1} + dL/dP_i @ A_i^T，从后往前累积即可。
    """
    stack = as_matrix_stack(matrices)
    upstream = np.asarray(upstream, dtype=float)
    if upstream.shape != stack.shape:
        raise ValueError(f"upstream shape {upstream.shape} != matrices shape {stack.shape}")
    products = prefix(stack)
    identity = np.eye(stack.shape[1])

    grads = np.zeros_like(stack)
    from_later = np.zeros(stack.shape[1:])  # 后面所有输出经由 P_i 传回来的梯度
    for i in range(len(stack) - 1, -1, -1):
        grad_prefix = from_later + upstream[i]  # dL/dP_i
        left = identity if i == 0 else products[i - 1]
        grads[i] = left.T @ grad_prefix
        from_later = grad_prefix @ stack[i].T
    return grads


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    # 1x1 矩阵就是标量连乘：前缀 [2, 6]，dL/dA0 = 1 + 3 = 4，dL/dA1 = 2
    small = np.array([[[2.0]], [[3.0]]])
    assert np.allclose(prefix(small), [[[2]], [[6]]])
    assert np.allclose(backward(small, np.ones_like(small)), [[[4]], [[2]]])

    # 随机 2x2 矩阵：scan 与顺序前缀积一致
    rng = np.random.default_rng(2)
    matrices = rng.normal(size=(5, 2, 2))
    upstream = rng.normal(size=matrices.shape)
    assert np.allclose(prefix(matrices), scan(matrices))

    # 解析梯度与中心差分一致
    grads = backward(matrices, upstream)
    eps = 1e-6
    for index in np.ndindex(matrices.shape):
        plus = matrices.copy()
        minus = matrices.copy()
        plus[index] += eps
        minus[index] -= eps
        numeric = ((prefix(plus) - prefix(minus)) * upstream).sum() / (2 * eps)
        assert np.isclose(numeric, grads[index], atol=1e-6)

    # n = 0 返回空结果
    empty = np.zeros((0, 3, 3))
    assert prefix(empty).shape == (0, 3, 3)
    assert scan(empty).shape == (0, 3, 3)
    assert backward(empty, empty).shape == (0, 3, 3)

    expect_value_error(prefix, np.zeros((2, 2, 3)))              # 不是方阵
    expect_value_error(backward, small, np.ones((1, 1, 1)))      # 上游梯度形状不符


if __name__ == "__main__":
    test()
