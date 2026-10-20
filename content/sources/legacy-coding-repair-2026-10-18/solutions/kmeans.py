import numpy as np

def kmeans(x, k, initial, max_iter=100, tol=1e-8):
    x, centers = np.asarray(x, float), np.array(initial, dtype=float, copy=True)
    if (x.ndim != 2 or not x.shape[1] or not 1 <= k <= len(x)
            or centers.shape != (k, x.shape[1]) or max_iter < 1
            or tol < 0 or not np.isfinite(tol)
            or not np.isfinite(x).all() or not np.isfinite(centers).all()):
        raise ValueError("invalid inputs")
    def assign(c):
        distances = ((x[:, None, :] - c[None, :, :]) ** 2).sum(axis=-1)
        return distances.argmin(axis=1)
    for _ in range(max_iter):
        labels = assign(centers)
        updated = centers.copy()
        for j in range(k):
            points = x[labels == j]
            if len(points):
                updated[j] = points.mean(axis=0)
        shift = np.linalg.norm(updated-centers, axis=1).max()
        centers = updated
        if shift <= tol:
            break
    labels = assign(centers)
    sse = ((x-centers[labels]) ** 2).sum()
    return centers, labels, float(sse)

x = np.array([[0.], [2.], [10.], [12.]])
c, labels, loss = kmeans(x, 2, [[0.], [10.]])
assert np.allclose(c, [[1.],[11.]]) and labels.tolist() == [0,0,1,1] and loss == 4
initial = np.array([[0.], [100.]])
c, labels, loss = kmeans([[0.],[0.]], 2, initial)
assert np.array_equal(c, initial) and labels.tolist() == [0,0] and loss == 0
assert np.array_equal(initial, [[0.], [100.]])  # input not mutated
c, labels, _ = kmeans(x, 2, [[0.],[1.]], max_iter=1)
expected = ((x[:,None,:]-c[None,:,:])**2).sum(-1).argmin(1)
assert np.array_equal(labels, expected)
_, _, previous = kmeans(x, 2, [[0.],[1.]], max_iter=1)
for n in range(2, 6):
    _, _, current = kmeans(x, 2, [[0.],[1.]], max_iter=n)
    assert current <= previous + 1e-12
    previous = current
