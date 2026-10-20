import numpy as np

def linear_entropy(x, w, b):
    x, w, b = [np.asarray(a, float) for a in (x, w, b)]
    if (x.ndim != 2 or w.ndim != 2 or b.ndim != 1
            or not len(x) or x.shape[1] != w.shape[0]
            or w.shape[1] != len(b) or not len(b)):
        raise ValueError("shape")
    z = x @ w + b
    if not np.isfinite(z).all():
        raise ValueError("nonfinite logits")
    shifted = z-z.max(axis=-1, keepdims=True)
    logp = shifted-np.log(np.exp(shifted).sum(axis=-1, keepdims=True))
    p = np.exp(logp)
    return p, -(p*logp).sum(axis=-1)

def l1_loss_grad_logits(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    if p.ndim != 2 or p.shape != q.shape or not len(p) or not p.shape[1]:
        raise ValueError("shape")
    for a in (p, q):
        if not np.isfinite(a).all() or (a < 0).any() or not np.allclose(a.sum(-1), 1):
            raise ValueError("distribution")
    g = np.sign(p-q)
    grad = p*(g-(p*g).sum(axis=-1, keepdims=True))/len(p)
    return np.abs(p-q).sum(axis=-1).mean(), grad

p, h = linear_entropy([[0.]], [[0.,0.]], [0.,0.])
assert np.allclose(h, np.log(2))
loss, grad = l1_loss_grad_logits(p, [[1.,0.]])
assert np.isclose(loss, 1) and np.allclose(grad, [[-.5,.5]])
p, h = linear_entropy([[1.]], [[1000.,-1000.]], [0.,0.])
assert np.isfinite(h).all() and np.allclose(h, 0)
assert l1_loss_grad_logits(p, p)[0] == 0
assert np.all(l1_loss_grad_logits(p, p)[1] == 0)
z = np.array([[.3,-.7,1.1], [.1,.9,-.5]])
q = np.array([[.2,.3,.5], [.5,.2,.3]])
def objective(logits):
    p, _ = linear_entropy(logits, np.eye(3), np.zeros(3))
    return l1_loss_grad_logits(p, q)[0]
p, _ = linear_entropy(z, np.eye(3), np.zeros(3))
_, analytical = l1_loss_grad_logits(p, q)
for idx in np.ndindex(z.shape):
    plus, minus = z.copy(), z.copy(); plus[idx] += 1e-6; minus[idx] -= 1e-6
    numerical = (objective(plus)-objective(minus))/2e-6
    assert np.isclose(analytical[idx], numerical, atol=1e-7)
