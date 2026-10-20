import numpy as np

def rope(x, start):
    d = x.shape[-1]
    if d % 2:
        raise ValueError("RoPE requires an even head dimension")
    angles = (np.arange(start, start+x.shape[2])[:, None]
              * 10000.0 ** (-np.arange(0, d, 2) / d))
    c, s = np.cos(angles), np.sin(angles)
    even, odd = x[..., 0::2], x[..., 1::2]
    out = np.empty_like(x)
    out[..., 0::2] = even*c - odd*s
    out[..., 1::2] = even*s + odd*c
    return out

def mha(x, wq, wk, wv, wo, heads, kv_heads=None, cache=None,
        key_valid=None, use_rope=False):
    x = np.asarray(x, dtype=float)
    wq, wk, wv, wo = [np.asarray(w, dtype=float) for w in (wq, wk, wv, wo)]
    kv_heads = heads if kv_heads is None else kv_heads
    if x.ndim != 3 or heads <= 0 or kv_heads <= 0 or heads % kv_heads:
        raise ValueError("invalid input or heads")
    b, t, model = x.shape
    if not b or not t or model % heads:
        raise ValueError("empty input or head dimension")
    d = model // heads
    if (wq.shape != (model, model) or wo.shape != (model, model)
            or wk.shape != (model, kv_heads*d) or wv.shape != wk.shape):
        raise ValueError("projection shapes")
    q = (x @ wq).reshape(b, t, heads, d).transpose(0, 2, 1, 3)
    k = (x @ wk).reshape(b, t, kv_heads, d).transpose(0, 2, 1, 3)
    v = (x @ wv).reshape(b, t, kv_heads, d).transpose(0, 2, 1, 3)
    old = 0
    if cache is not None:
        old_k, old_v = [np.asarray(a, dtype=float) for a in cache]
        if (old_k.ndim != 4 or old_k.shape != old_v.shape
                or old_k.shape[:2] != (b, kv_heads) or old_k.shape[-1] != d):
            raise ValueError("cache shape")
        old = old_k.shape[2]
    if use_rope:
        q, k = rope(q, old), rope(k, old)
    if cache is not None:
        k = np.concatenate((old_k, k), axis=2)
        v = np.concatenate((old_v, v), axis=2)
    total = k.shape[2]
    # Cache only the compact KV heads. Repetition is a reference implementation.
    kr = np.repeat(k, heads//kv_heads, axis=1)
    vr = np.repeat(v, heads//kv_heads, axis=1)
    scores = (q @ kr.swapaxes(-1, -2)) / np.sqrt(d)
    allowed = np.broadcast_to(
        np.arange(total)[None, :] <= old+np.arange(t)[:, None],
        (b, heads, t, total)).copy()
    if key_valid is not None:
        valid = np.asarray(key_valid, dtype=bool)
        if valid.shape != (b, total):
            raise ValueError("key_valid shape")
        allowed &= valid[:, None, None, :]
    scores = np.where(allowed, scores, -np.inf)
    maximum = scores.max(axis=-1, keepdims=True)
    maximum = np.where(np.isfinite(maximum), maximum, 0.0)
    weights = np.exp(scores-maximum)
    denom = weights.sum(axis=-1, keepdims=True)
    weights = np.divide(weights, denom, out=np.zeros_like(weights), where=denom > 0)
    output = (weights @ vr).transpose(0, 2, 1, 3).reshape(b, t, model) @ wo
    return output, (k, v)

rng = np.random.default_rng(7)
x = rng.normal(size=(2, 5, 8))
for kv_heads in (1, 2, 4):
    weights = [rng.normal(size=(8, n)) for n in (8, kv_heads*2, kv_heads*2, 8)]
    for rotating in (False, True):
        full, _ = mha(x, *weights, heads=4, kv_heads=kv_heads, use_rope=rotating)
        pieces, cache = [], None
        for step in range(5):
            out, cache = mha(x[:, step:step+1], *weights, heads=4,
                             kv_heads=kv_heads, cache=cache, use_rope=rotating)
            pieces.append(out)
        assert np.allclose(full, np.concatenate(pieces, axis=1))
        assert cache[0].shape == (2, kv_heads, 5, 2)
        changed = x.copy(); changed[:, 4] += 100
        other, _ = mha(changed, *weights, heads=4, kv_heads=kv_heads, use_rope=rotating)
        assert np.allclose(full[:, :4], other[:, :4])  # no future-token leakage
    zero, _ = mha(x, *weights, heads=4, kv_heads=kv_heads, key_valid=np.zeros((2,5), bool))
    assert np.isfinite(zero).all() and np.allclose(zero, 0)
# Independent numerical oracle: scalar-head loop, uniform Q/K, known V.
z = np.array([[[2., 4.], [6., 8.]]]); ident = np.eye(2); zeros = np.zeros((2,2))
out, _ = mha(z, zeros, zeros, ident, ident, heads=1)
assert np.allclose(out, [[[2.,4.], [4.,6.]]])
# Cached chunk (not only one-token decode) uses the prefix offset in its causal mask.
weights = [np.eye(8)] * 4
full, _ = mha(x, *weights, heads=4, use_rope=True)
_, cache = mha(x[:, :2], *weights, heads=4, use_rope=True)
tail, _ = mha(x[:, 2:], *weights, heads=4, cache=cache, use_rope=True)
assert np.allclose(full[:, 2:], tail)
