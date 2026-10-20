import numpy as np


def sigmoid(z):
    """数值稳定的 sigmoid：1 / (1 + e^{-z}) = exp(-log(1 + e^{-z}))，大 |z| 不会溢出。"""
    return np.exp(-np.logaddexp(0, -z))


def add_bias(features):
    """在 (N, D) 特征右侧拼一列 1，得到 (N, D + 1)，最后一维权重就是偏置。"""
    return np.column_stack([features, np.ones(len(features))])


def fit(x, y, steps=1000, lr=0.1, l2=0.01):
    """全批量梯度下降训练逻辑回归，返回 (mean, std, weights)。

    mean、std 只用训练集估计，predict 必须复用它们。
    """
    x = np.asarray(x, dtype=float)  # (N, D)
    y = np.asarray(y, dtype=float)  # (N,)
    if x.ndim != 2 or len(x) == 0:
        raise ValueError("x must be a non-empty 2-D array")
    if y.shape != (len(x),):
        raise ValueError("y must have shape (N,)")
    if not np.all(np.isin(y, [0, 1])):
        raise ValueError("y must contain only 0 and 1")
    if not np.all(np.isfinite(x)):
        raise ValueError("x must be finite")

    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std = np.where(std > 0, std, 1.0)  # 常数列不缩放，避免除以 0
    design = add_bias((x - mean) / std)  # (N, D + 1)
    weights = np.zeros(design.shape[1])

    for _ in range(steps):
        gradient = design.T @ (sigmoid(design @ weights) - y) / len(design)
        penalty = l2 * weights
        penalty[-1] = 0  # 偏置不加 L2
        weights -= lr * (gradient + penalty)
    return mean, std, weights


def predict(model, x):
    """用训练时的 mean/std 标准化，概率 >= 0.5 判为 1。"""
    mean, std, weights = model
    x = np.asarray(x, dtype=float)
    design = add_bias((x - mean) / std)
    return (sigmoid(design @ weights) >= 0.5).astype(int)


def safe_divide(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def metrics(y_true, y_pred):
    """返回 accuracy、precision、recall、F1；分母为 0 时记为 0。"""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_true.shape != y_pred.shape or len(y_true) == 0:
        raise ValueError("y_true and y_pred must be non-empty and the same shape")

    true_pos = int(((y_true == 1) & (y_pred == 1)).sum())
    false_pos = int(((y_true == 0) & (y_pred == 1)).sum())
    false_neg = int(((y_true == 1) & (y_pred == 0)).sum())
    precision = safe_divide(true_pos, true_pos + false_pos)
    recall = safe_divide(true_pos, true_pos + false_neg)
    return {
        "accuracy": float((y_true == y_pred).mean()),
        "precision": precision,
        "recall": recall,
        "f1": safe_divide(2 * precision * recall, precision + recall),
    }


def select_annotators(votes, trusted, min_accuracy=0.7):
    """votes 形状 (N, A)，trusted 形状 (N,)：返回在可信校准集上准确率达标的标注员下标。"""
    votes = np.asarray(votes)
    trusted = np.asarray(trusted)
    if votes.ndim != 2 or len(votes) != len(trusted) or len(votes) == 0:
        raise ValueError("calibration votes must be (N, A) and match trusted labels")
    accuracy = (votes == trusted[:, None]).mean(axis=0)  # (A,)
    return np.flatnonzero(accuracy >= min_accuracy)


def vote(votes, selected):
    """只用 selected 标注员做多数票；平票取 0。"""
    votes = np.asarray(votes)
    if len(selected) == 0:
        raise ValueError("no reliable annotators")
    return (votes[:, selected].mean(axis=1) > 0.5).astype(int)


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    # 一维可分数据：训练后全部预测正确
    x = np.array([[-2.0], [-1.0], [1.0], [2.0]])
    y = np.array([0, 0, 1, 1])
    model = fit(x, y)
    assert np.array_equal(predict(model, x), y)
    assert metrics(y, predict(model, x))["f1"] == 1
    mean, std, weights = model
    assert np.allclose(mean, [0])
    assert np.isfinite(weights).all()

    # 标注员 0 全对，标注员 1 全部反标，应被排除
    votes = np.column_stack([y, 1 - y])
    selected = select_annotators(votes, trusted=y)
    assert selected.tolist() == [0]
    assert np.array_equal(vote(votes, selected), y)

    # 平票取 0
    assert vote([[1, 0]], [0, 1]).tolist() == [0]

    # 没有预测正例时 precision 记为 0
    assert metrics([0, 0], [0, 0])["precision"] == 0

    # 常数特征不会除以 0
    assert np.isfinite(fit(np.ones((4, 2)), y)[2]).all()

    # 非法输入
    expect_value_error(fit, x, [0, 1, 2, 1])
    expect_value_error(vote, votes, [])


if __name__ == "__main__":
    test()
