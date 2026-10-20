import numpy as np


def log_softmax(logits):
    """按行计算 log-softmax。先减去每行最大值，exp 就不会溢出。"""
    shifted = logits - logits.max(axis=1, keepdims=True)
    return shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))


def check_inputs(logits, labels, smoothing):
    if logits.ndim != 2 or logits.shape[1] < 2:
        raise ValueError(f"logits must have shape [N, C] with C >= 2, got {logits.shape}")
    num_rows, num_classes = logits.shape
    if labels.shape != (num_rows,) or not np.issubdtype(labels.dtype, np.integer):
        raise ValueError(f"labels must be integers of shape ({num_rows},), got {labels.dtype} {labels.shape}")
    if np.any(labels < 0) or np.any(labels >= num_classes):
        raise ValueError(f"labels must be in [0, {num_classes})")
    if not 0 <= smoothing < 1:
        raise ValueError(f"smoothing must be in [0, 1), got {smoothing}")


def cross_entropy(logits, labels, mask=None, smoothing=0):
    """带 mask 和标签平滑的交叉熵，返回 (loss, dlogits)。

    logits: [N, C]，labels: [N] 整数，mask: [N] bool（None 表示全部有效）。
    目标分布是 (1 - smoothing) * one_hot + smoothing / C，loss 只在有效行上平均。
    没有有效行时返回 loss = 0 和全零梯度。
    """
    logits = np.asarray(logits, dtype=float)
    labels = np.asarray(labels)
    check_inputs(logits, labels, smoothing)
    num_rows, num_classes = logits.shape

    valid = np.ones(num_rows, dtype=bool) if mask is None else np.asarray(mask, dtype=bool)
    if valid.shape != (num_rows,):
        raise ValueError(f"mask must have shape ({num_rows},), got {valid.shape}")
    num_valid = int(valid.sum())
    if num_valid == 0:
        return 0.0, np.zeros_like(logits)

    log_probs = log_softmax(logits)                             # [N, C]
    target = np.full_like(logits, smoothing / num_classes)      # [N, C]
    target[np.arange(num_rows), labels] += 1 - smoothing

    row_loss = -(target * log_probs).sum(axis=1)                # [N]
    loss = float((row_loss * valid).sum() / num_valid)
    # 每行目标分布的和为 1，所以 d(loss)/d(logits) = softmax - target
    grad = (np.exp(log_probs) - target) * valid[:, None] / num_valid
    return loss, grad


def test():
    def numeric_grad(fn, x, eps=1e-4):
        """中心差分，逐个元素估计 fn 对 x 的梯度。"""
        grad = np.zeros_like(x)
        for index in np.ndindex(x.shape):
            plus = x.copy()
            minus = x.copy()
            plus[index] += eps
            minus[index] -= eps
            grad[index] = (fn(plus) - fn(minus)) / (2 * eps)
        return grad

    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 两类等概率：loss = log 2，梯度是 softmax - one_hot
    loss, grad = cross_entropy([[0, 0]], np.array([1]))
    assert np.isclose(loss, np.log(2))
    assert np.allclose(grad, [[0.5, -0.5]])

    # 极端 logits 不溢出；被 mask 掉的行梯度为 0
    logits = np.array([[1000.0, -1000.0, 0.0], [1.0, 2.0, 3.0]])
    labels = np.array([0, 2])
    mask = [True, False]
    loss, grad = cross_entropy(logits, labels, mask, 0.1)
    assert np.isfinite(loss)
    assert np.all(grad[1] == 0)

    # 解析梯度与数值梯度一致
    def masked_loss(x):
        return cross_entropy(x, labels, mask, 0.1)[0]

    assert np.allclose(numeric_grad(masked_loss, logits), grad, atol=1e-6)

    # 全部被 mask 时 loss 有定义，等于 0
    assert cross_entropy(logits, labels, [False, False])[0] == 0

    expect_value_error(cross_entropy, [[0.0]], [0])               # C 必须 >= 2
    expect_value_error(cross_entropy, [[0.0, 1.0]], [2])          # 标签越界
    expect_value_error(cross_entropy, [[0.0, 1.0]], [0], None, 1)  # smoothing 必须 < 1


if __name__ == "__main__":
    test()
