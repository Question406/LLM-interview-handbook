import numpy as np


def _shift_by_row_max(x, axis):
    """检查输入，返回沿 axis 减去最大值后的 float64 副本（不修改输入）。"""
    x = np.asarray(x, dtype=np.float64)
    if x.shape[axis] == 0:
        raise ValueError(f"cannot normalize over empty axis {axis}")
    if np.isnan(x).any() or np.isposinf(x).any():
        raise ValueError("input contains NaN or +inf")
    row_max = x.max(axis=axis, keepdims=True)
    if np.isneginf(row_max).any():
        raise ValueError("a row is fully masked (all -inf)")
    return x - row_max


def softmax(x, axis=-1):
    """沿 axis 的数值稳定 softmax；-inf 表示屏蔽，输出形状与输入相同。"""
    shifted = _shift_by_row_max(x, axis)
    exps = np.exp(shifted)  # 每行最大的一项是 e^0 = 1，不会溢出
    return exps / exps.sum(axis=axis, keepdims=True)


def log_softmax(x, axis=-1):
    """沿 axis 的数值稳定 log-softmax：shifted - log(sum(exp(shifted)))。"""
    shifted = _shift_by_row_max(x, axis)
    return shifted - np.log(np.exp(shifted).sum(axis=axis, keepdims=True))


def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} accepted invalid input {args}")


logits = np.array([[1000.0, 1001.0], [-1000.0, -999.0]])

# 大正数、大负数都不溢出；两行差值相同，所以分布相同
probs = softmax(logits)
assert np.allclose(probs[0], probs[1])

# 每行各自加一个常数，分布不变
assert np.allclose(softmax(logits + np.array([[500.0], [-700.0]])), probs)

# 示例：[1000, 1000] -> [0.5, 0.5]
assert np.allclose(softmax([1000.0, 1000.0]), [0.5, 0.5])

# axis=0 时沿列归一化
assert np.allclose(softmax(logits, axis=0).sum(axis=0), 1)

# log_softmax 和 softmax 一致
assert np.allclose(np.exp(log_softmax(logits)), probs)

# -inf 表示屏蔽，对应概率精确为 0
assert np.array_equal(softmax([0.0, -np.inf]), [1.0, 0.0])

# 不修改输入
original = logits.copy()
softmax(logits)
log_softmax(logits)
assert np.array_equal(logits, original)

# 非法输入：全屏蔽行、NaN、+inf、空轴，两个函数都报错
for bad in ([-np.inf, -np.inf], [np.nan, 1.0], [np.inf, 0.0], np.zeros((2, 0))):
    expect_value_error(softmax, bad)
    expect_value_error(log_softmax, bad)
