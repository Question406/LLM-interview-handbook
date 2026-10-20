import numpy as np

TEST_SIZE = 2000


def fit_linear(x, y, ridge):
    """ridge == 0 时用 lstsq 求最小范数最小二乘解；否则解 (XᵀX + λI) w = Xᵀy。"""
    if ridge == 0:
        return np.linalg.lstsq(x, y, rcond=None)[0]
    features = x.shape[1]
    return np.linalg.solve(x.T @ x + ridge * np.eye(features), x.T @ y)


def sample_data(rng, truth, n, noise):
    """生成 y = x · truth + 高斯噪声，x 形状 (n, D)。"""
    x = rng.normal(size=(n, len(truth)))
    y = x @ truth + rng.normal(scale=noise, size=n)
    return x, y


def experiment(sample_sizes, features=20, noise=0.2, seeds=(0, 1, 2), ridge=0.0):
    """对每个训练样本量，在多个 seed 上拟合线性模型，返回平均 train/test MSE。

    每个 seed 固定一组真实权重和一份独立的测试集。
    """
    if features < 1:
        raise ValueError("features must be >= 1")
    if noise < 0 or ridge < 0:
        raise ValueError("noise and ridge must be non-negative")
    if not seeds:
        raise ValueError("need at least one seed")
    if any(n < 1 for n in sample_sizes):
        raise ValueError("sample sizes must be >= 1")

    errors = {n: [] for n in sample_sizes}  # n -> [(train_mse, test_mse), ...]
    for seed in seeds:
        rng = np.random.default_rng(seed)
        truth = rng.normal(size=features) / np.sqrt(features)
        x_test, y_test = sample_data(rng, truth, TEST_SIZE, noise)
        for n in sample_sizes:
            x_train, y_train = sample_data(rng, truth, n, noise)
            weights = fit_linear(x_train, y_train, ridge)
            train_mse = np.mean((x_train @ weights - y_train) ** 2)
            test_mse = np.mean((x_test @ weights - y_test) ** 2)
            errors[n].append((train_mse, test_mse))

    rows = []
    for n in sample_sizes:
        train_mse, test_mse = np.mean(errors[n], axis=0)
        rows.append({"n": n, "train_mse": float(train_mse), "test_mse": float(test_mse)})
    return rows


def test():
    # 同样的 seed 结果完全相同
    first = experiment([3, 5, 10], features=5, seeds=(0, 1))
    second = experiment([3, 5, 10], features=5, seeds=(0, 1))
    assert first == second
    assert len(first) == 3

    # 所有误差有限且非负
    assert all(np.isfinite(row["test_mse"]) for row in first)
    assert all(row["train_mse"] >= 0 for row in first)

    # n = 3 < D = 5：最小范数解能完全插值训练集
    assert first[0]["train_mse"] < 1e-20

    # ridge > 0 时也能正常运行
    ridge_rows = experiment([3, 5], 5, seeds=(0,), ridge=1)
    assert all(np.isfinite(row["test_mse"]) for row in ridge_rows)

    # 这组固定 seed 下，n = D = 20 处测试误差出现峰值，ridge 能把峰压下去
    plain = [row["test_mse"] for row in experiment([15, 20, 40], features=20)]
    ridged = [row["test_mse"] for row in experiment([15, 20, 40], features=20, ridge=1)]
    assert plain[1] > plain[0]
    assert plain[1] > plain[2]
    assert ridged[1] < plain[1]


if __name__ == "__main__":
    test()
