import numpy as np


def _as_matrices(train, query):
    """转成 float 矩阵并检查形状：train 是 (N, D)，query 是 (M, D)，N >= 1。"""
    train = np.asarray(train, dtype=float)
    query = np.asarray(query, dtype=float)
    if train.ndim != 2 or query.ndim != 2:
        raise ValueError("train and query must be 2-D arrays")
    if train.shape[1] != query.shape[1]:
        raise ValueError(f"feature dims differ: {train.shape[1]} vs {query.shape[1]}")
    if len(train) == 0:
        raise ValueError("train must be non-empty")
    return train, query


def network_scores(train, query):
    """把 1-NN（平方欧氏距离）写成 Wx + b：每个训练样本是一个输出单元。

    W = 2 * train，b = -||train_i||²，分数越大距离越近。返回 (M, N)。
    """
    train, query = _as_matrices(train, query)
    weights = 2 * train  # (N, D)
    bias = -np.sum(train * train, axis=1)  # (N,)
    return query @ weights.T + bias  # (M, N)


def nearest(train, labels, query, metric="l2"):
    """对每个查询返回最近训练样本的 label；并列时取训练下标最小的。"""
    train, query = _as_matrices(train, query)
    labels = np.asarray(labels)
    if len(labels) != len(train):
        raise ValueError(f"expected {len(train)} labels, got {len(labels)}")

    if metric == "l2":
        index = np.argmax(network_scores(train, query), axis=1)
    elif metric == "l1":
        # L1 没有点积展开，只能广播出 (M, N, D) 的差再求和
        distances = np.abs(query[:, None, :] - train[None, :, :]).sum(axis=-1)  # (M, N)
        index = np.argmin(distances, axis=1)
    else:
        raise ValueError(f"unknown metric: {metric!r}")
    return labels[index]


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 第二个查询到两个训练点距离相同，取下标小的 a
    train = np.array([[0, 0], [2, 0]])
    query = np.array([[1.9, 0], [1, 0]])
    assert nearest(train, ["a", "b"], query).tolist() == ["b", "a"]

    # 和逐个计算距离的暴力解对照
    rng = np.random.default_rng(4)
    train = rng.normal(size=(7, 3))
    query = rng.normal(size=(5, 3))
    distance_fns = {
        "l1": lambda u, v: np.abs(u - v).sum(),
        "l2": lambda u, v: ((u - v) ** 2).sum(),
    }
    for metric, distance in distance_fns.items():
        expected = [
            min(range(len(train)), key=lambda i: distance(point, train[i]))
            for point in query
        ]
        assert np.array_equal(nearest(train, np.arange(len(train)), query, metric), expected)

    # 形状、label 数量和 metric 校验
    expect_value_error(nearest, [[0, 0]], ["a"], [[0, 0, 0]])
    expect_value_error(nearest, [[0, 0]], ["a", "b"], [[0, 0]])
    expect_value_error(nearest, [[0, 0]], ["a"], [[0, 0]], "cosine")
    expect_value_error(network_scores, np.zeros((0, 2)), [[0, 0]])


if __name__ == "__main__":
    test()
