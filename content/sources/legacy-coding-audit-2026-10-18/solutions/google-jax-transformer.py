import jax
import jax.numpy as jnp


def rms_norm(x, eps=1e-6):
    """沿最后一维的 RMSNorm，不带可学习 scale。"""
    return x * jax.lax.rsqrt(jnp.mean(x * x, axis=-1, keepdims=True) + eps)


def block(h, w):
    """一层 pre-norm decoder block。h: [B, T, D]；w: 单层参数字典。返回 (h, None) 供 scan 使用。"""
    seq_len, model_dim = h.shape[1], h.shape[-1]
    x = rms_norm(h)
    q = x @ w["q"]  # [B, T, D]
    k = x @ w["k"]
    v = x @ w["v"]
    scores = q @ jnp.swapaxes(k, -1, -2) / jnp.sqrt(model_dim)  # [B, T, T]
    keep = jnp.tril(jnp.ones((seq_len, seq_len), dtype=bool))
    attn = jax.nn.softmax(jnp.where(keep, scores, -jnp.inf), axis=-1)
    h = h + (attn @ v) @ w["o"]
    x = rms_norm(h)
    h = h + jax.nn.silu(x @ w["up"]) @ w["down"]
    return h, None


def stack(h, weights, remat=False):
    """用 lax.scan 跨层执行 block；weights 的每个叶子有前导层维 L。"""
    body = jax.checkpoint(block) if remat else block
    h, _ = jax.lax.scan(body, h, weights)
    return h


def loop_stack(h, weights):
    """Python for 循环的对照实现。"""
    num_layers = weights["q"].shape[0]
    for layer in range(num_layers):
        layer_weights = {name: value[layer] for name, value in weights.items()}
        h, _ = block(h, layer_weights)
    return h


def make_weights(key, num_layers, model_dim, ffn_dim):
    shapes = {
        "q": (model_dim, model_dim),
        "k": (model_dim, model_dim),
        "v": (model_dim, model_dim),
        "o": (model_dim, model_dim),
        "up": (model_dim, ffn_dim),
        "down": (ffn_dim, model_dim),
    }
    keys = jax.random.split(key, len(shapes))
    return {
        name: jax.random.normal(subkey, (num_layers,) + shape) * 0.1
        for (name, shape), subkey in zip(shapes.items(), keys)
    }


weights = make_weights(jax.random.PRNGKey(0), num_layers=2, model_dim=4, ffn_dim=4)
h = jax.random.normal(jax.random.PRNGKey(1), (1, 3, 4))

# scan 与 Python 层循环的前向一致
scanned = stack(h, weights)
assert scanned.shape == (1, 3, 4)
assert jnp.allclose(scanned, loop_stack(h, weights), atol=1e-6)

# jit 下结果不变
assert jnp.allclose(jax.jit(lambda x: stack(x, weights))(h), scanned, atol=1e-6)

# remat 不改变梯度
grad_plain = jax.grad(lambda x: stack(x, weights, remat=False).sum())(h)
grad_remat = jax.grad(lambda x: stack(x, weights, remat=True).sum())(h)
assert jnp.allclose(grad_plain, grad_remat, atol=1e-5)

# 因果：改最后一个 token 不影响前两个位置
perturbed = h.at[:, 2].add(10)
assert jnp.allclose(stack(perturbed, weights)[:, :2], scanned[:, :2])

# F 与 D 不同时形状也对
wide = make_weights(jax.random.PRNGKey(2), num_layers=3, model_dim=4, ffn_dim=8)
assert stack(h, wide).shape == (1, 3, 4)
assert jnp.allclose(stack(h, wide), loop_stack(h, wide), atol=1e-5)
