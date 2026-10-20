import math


class Entropy:
    """流式计算 softmax(logits) 的自然对数熵，只保存三个数，支持分块合并。

    设 m = max(x)，z = Σ exp(x - m)，r = Σ exp(x - m) · (x - m)，
    则熵 H = log z - r / z。
    """

    def __init__(self):
        self.max_logit = -math.inf
        self.z = 0.0
        self.r = 0.0

    def _absorb(self, max_logit, z, r):
        """把另一份 (m, z, r) 合并进来；两边先换算到共同的最大值上。"""
        if z == 0:
            return self
        if self.z == 0:
            self.max_logit, self.z, self.r = max_logit, z, r
            return self
        new_max = max(self.max_logit, max_logit)
        own_r = self._rescaled_r(self.max_logit, self.z, self.r, new_max)
        incoming_r = self._rescaled_r(max_logit, z, r, new_max)
        self.r = own_r + incoming_r
        self.z = self.z * math.exp(self.max_logit - new_max) + z * math.exp(max_logit - new_max)
        self.max_logit = new_max
        return self

    @staticmethod
    def _rescaled_r(old_max, z, r, new_max):
        # 每项权重乘 scale，同时 (x - old_max) 变成 (x - new_max)，多出 (old_max - new_max)。
        # 只缩放 r 而漏掉 z · (old_max - new_max) 这一项，结果会错。
        scale = math.exp(old_max - new_max)
        return scale * (r + z * (old_max - new_max))

    def add(self, logit):
        if not math.isfinite(logit):
            raise ValueError(f"logit must be finite: {logit!r}")
        # 单个 logit 的状态：m = x，z = 1，r = 0
        return self._absorb(logit, 1.0, 0.0)

    def merge(self, other):
        return self._absorb(other.max_logit, other.z, other.r)

    def value(self):
        if self.z == 0:
            raise ValueError("entropy of an empty stream is undefined")
        return math.log(self.z) - self.r / self.z


def test():
    import numpy as np

    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    def reference_entropy(logits):
        probs = np.exp(np.array(logits) - max(logits))
        probs /= probs.sum()
        return -sum(p * math.log(p) for p in probs if p > 0)

    logits = [1000.0, 999.0, -1000.0, 1001.0]
    expected = reference_entropy(logits)

    # 逐项累积，与整批计算一致（logit 很大也不溢出）
    whole = Entropy()
    for logit in logits:
        whole.add(logit)
    assert np.isclose(whole.value(), expected)

    # 拆成两块再合并，结果相同
    left = Entropy()
    right = Entropy()
    for logit in logits[:2]:
        left.add(logit)
    for logit in logits[2:]:
        right.add(logit)
    assert np.isclose(left.merge(right).value(), expected)

    # 两个相同 logit 的熵是 log 2；单个 logit 的熵是 0
    assert np.isclose(Entropy().add(1000).add(1000).value(), math.log(2))
    assert Entropy().add(5).value() == 0

    # 和空流合并不改变结果
    assert np.isclose(Entropy().merge(whole).value(), expected)

    # 空流和非有限 logit
    expect_value_error(Entropy().value)
    expect_value_error(Entropy().add, math.inf)


if __name__ == "__main__":
    test()
