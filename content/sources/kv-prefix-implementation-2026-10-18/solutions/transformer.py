import hashlib
import numpy as np


class TinyTransformer:
    """Two-or-more-layer CPU reference: RMSNorm, RoPE, GQA and gated MLP."""
    def __init__(self, seed=0, layers=2, vocab=19, width=8, heads=2, kv_heads=1):
        if layers < 1 or width % heads or heads % kv_heads or (width//heads) % 2:
            raise ValueError('head geometry')
        self.layers, self.heads, self.kv_heads = layers, heads, kv_heads
        self.width, self.d = width, width//heads
        rng = np.random.default_rng(seed)
        def weight(a, b):
            return rng.normal(scale=.2, size=(a, b))
        self.embed = weight(vocab, width)
        self.output = weight(width, vocab)
        self.weights = []
        for _ in range(layers):
            self.weights.append(dict(q=weight(width, width),
                                     k=weight(width, kv_heads*self.d),
                                     v=weight(width, kv_heads*self.d),
                                     o=weight(width, width),
                                     gate=weight(width, 2*width),
                                     up=weight(width, 2*width),
                                     down=weight(2*width, width)))
        # Frozen weights/config define the cache namespace in this exercise.
        arrays = [self.embed, self.output]
        arrays += [w[k] for w in self.weights for k in sorted(w)]
        digest = hashlib.sha256(str((layers, width, heads, kv_heads)).encode())
        for a in arrays:
            a.flags.writeable = False
            digest.update(a.tobytes())
        self.fingerprint = digest.hexdigest()
        self.computed_tokens = 0

    @staticmethod
    def norm(x):
        return x / np.sqrt(np.mean(x*x, axis=-1, keepdims=True)+1e-6)

    @staticmethod
    def rotate(x, start):
        d = x.shape[-1]
        angle = np.arange(start, start+x.shape[1])[:, None] * 10000.**(-np.arange(0, d, 2)/d)
        even, odd = x[..., 0::2], x[..., 1::2]
        out = np.empty_like(x)
        out[..., 0::2] = even*np.cos(angle)-odd*np.sin(angle)
        out[..., 1::2] = even*np.sin(angle)+odd*np.cos(angle)
        return out

    def forward(self, token_ids, cache=None):
        ids = np.asarray(token_ids)
        if ids.ndim != 1 or ids.dtype.kind not in 'iu' or not len(ids):
            raise ValueError('nonempty integer token sequence required')
        if (ids < 0).any() or (ids >= len(self.embed)).any():
            raise ValueError('token range')
        old = 0
        if cache is not None:
            if len(cache) != self.layers:
                raise ValueError('one KV pair per layer required')
            lengths = set()
            for k, v in cache:
                if k.ndim != 3 or k.shape != v.shape or k.shape[0] != self.kv_heads or k.shape[-1] != self.d:
                    raise ValueError('cache shape')
                lengths.add(k.shape[1])
            if len(lengths) != 1:
                raise ValueError('layer cache lengths disagree')
            old = lengths.pop()
        x = self.embed[ids].copy()
        new_cache = []
        t = len(ids)
        for layer, w in enumerate(self.weights):
            z = self.norm(x)
            q = self.rotate((z@w['q']).reshape(t, self.heads, self.d).transpose(1, 0, 2), old)
            k = self.rotate((z@w['k']).reshape(t, self.kv_heads, self.d).transpose(1, 0, 2), old)
            v = (z@w['v']).reshape(t, self.kv_heads, self.d).transpose(1, 0, 2)
            if cache is not None:
                k = np.concatenate((cache[layer][0], k), axis=1)
                v = np.concatenate((cache[layer][1], v), axis=1)
            new_cache.append((k, v))
            kr, vr = (np.repeat(a, self.heads//self.kv_heads, axis=0) for a in (k, v))
            scores = (q@kr.swapaxes(-1, -2))/np.sqrt(self.d)
            allowed = np.arange(old+t)[None, :] <= (old+np.arange(t))[:, None]
            scores = np.where(allowed[None], scores, -np.inf)
            p = np.exp(scores-scores.max(axis=-1, keepdims=True))
            p /= p.sum(axis=-1, keepdims=True)
            attended = (p@vr).transpose(1, 0, 2).reshape(t, self.width)
            x += attended@w['o']
            z = self.norm(x)
            gate = z@w['gate']
            # Stable sigmoid, used only in the SiLU gate.
            e = np.exp(-np.abs(gate))
            sigmoid = np.where(gate < 0, e/(1+e), 1/(1+e))
            x += (gate*sigmoid*(z@w['up']))@w['down']
        self.computed_tokens += t
        return self.norm(x)@self.output, tuple(new_cache)


def slice_cache(cache, length):
    if length < 0 or any(length > k.shape[1] for k, _ in cache):
        raise ValueError('cache slice length')
    return tuple((k[:, :length].copy(), v[:, :length].copy()) for k, v in cache)


# === TESTS ===
def test():
    ids = [1, 4, 2, 7, 3, 8]
    model = TinyTransformer(seed=7, layers=3)
    full, _ = model.forward(ids)
    cache = None
    parts = []
    for token in ids:
        logits, cache = model.forward([token], cache)
        parts.append(logits)
    assert np.allclose(full, np.concatenate(parts), atol=1e-12)
    prefix, cache = model.forward(ids[:3])
    suffix, extended = model.forward(ids[3:], cache)
    assert np.allclose(prefix, full[:3], atol=1e-12)
    assert np.allclose(suffix, full[3:], atol=1e-12)
    assert all(k.shape == (1, 6, 4) for k, _ in extended)
    snapshot = tuple((k.copy(), v.copy()) for k, v in cache)
    branch_a, _ = model.forward([5, 9], cache)
    branch_b, _ = model.forward([6, 10], cache)
    assert np.allclose(branch_a, model.forward(ids[:3]+[5, 9])[0][3:])
    assert np.allclose(branch_b, model.forward(ids[:3]+[6, 10])[0][3:])
    assert all(np.array_equal(a, b) for pair, saved in zip(cache, snapshot) for a, b in zip(pair, saved))
    # A future token must not change prefix hidden states at any layer.
    altered, _ = model.forward(ids[:-1]+[12])
    assert np.allclose(altered[:-1], full[:-1])
    assert all(k.shape[1] == 2 for k, _ in slice_cache(cache, 2))

if __name__ == '__main__':
    test()
