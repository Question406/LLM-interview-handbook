from collections import OrderedDict
import json
import os
import tempfile


def _freeze(value):
    """把参数编码成带类型标签的 JSON 结构，使 True 和 1、tuple 和 list 得到不同的键。"""
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("dict keys in cache key must be str")
        return ["dict", sorted((key, _freeze(item)) for key, item in value.items())]
    if isinstance(value, (tuple, list)):
        return [type(value).__name__, [_freeze(item) for item in value]]
    if value is None or type(value) in (bool, int, float, str):
        return [type(value).__name__, value]
    raise ValueError(f"unsupported cache key type: {type(value).__name__}")


def call_key(args, kwargs):
    """根据一次函数调用的 args 和 kwargs 生成缓存键；kwargs 的传入顺序不影响结果。"""
    return json.dumps([_freeze(args), _freeze(kwargs)], sort_keys=True, allow_nan=False)


class Cache:
    """按总权重限容的 LRU。data 里从最久未用到最近使用排列，值为 (value, weight)。"""

    def __init__(self, capacity):
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        self.capacity = capacity
        self.data = OrderedDict()
        self.used = 0

    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)
        return self.data[key][0]

    def put(self, key, value, weight=1):
        """插入或更新；单项权重超过容量时拒绝并返回 False，旧值保留。"""
        if weight <= 0:
            raise ValueError("weight must be positive")
        if weight > self.capacity:
            return False
        if key in self.data:
            _, old_weight = self.data.pop(key)
            self.used -= old_weight
        # 一次插入可能要连续淘汰好几个最久未用的条目
        while self.used + weight > self.capacity:
            _, (_, evicted_weight) = self.data.popitem(last=False)
            self.used -= evicted_weight
        self.data[key] = (value, weight)
        self.used += weight
        return True

    def save(self, path):
        """写临时文件并 fsync，再原子替换目标文件，读者不会看到写了一半的快照。"""
        directory = os.path.dirname(os.path.abspath(path))
        fd, tmp_path = tempfile.mkstemp(dir=directory)
        try:
            with os.fdopen(fd, "w") as file:
                json.dump([self.capacity, list(self.data.items())], file)
                file.flush()
                os.fsync(file.fileno())
            os.replace(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @classmethod
    def load(cls, path):
        """按保存时的顺序逐个 put，恢复 LRU 顺序和总权重。"""
        with open(path) as file:
            capacity, items = json.load(file)
        cache = cls(capacity)
        for key, (value, weight) in items:
            cache.put(key, value, weight)
        return cache


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 访问 a 之后插入 c，最久未用的 b 被淘汰
    cache = Cache(5)
    cache.put("a", "A", 3)
    cache.put("b", "B", 2)
    assert cache.get("a") == "A"
    cache.put("c", "C", 2)
    assert cache.get("b") is None
    assert cache.get("c") == "C"

    # 超过容量的单项被拒绝，旧值保留
    assert not cache.put("a", "bad", 6)
    assert cache.get("a") == "A"

    # 一次插入连续淘汰多项
    cache.put("d", "D", 5)
    assert list(cache.data) == ["d"]
    assert cache.used == 5

    # 权重必须为正
    expect_value_error(cache.put, "e", "E", 0)

    # 缓存键：kwargs 顺序无关，bool 和 int 不同，tuple 和 list 不同
    assert call_key((1,), {"x": 2, "y": 3}) == call_key((1,), {"y": 3, "x": 2})
    assert call_key((True,), {}) != call_key((1,), {})
    assert call_key(([1],), {}) != call_key(((1,),), {})
    expect_value_error(call_key, (object(),), {})

    # 保存后加载，顺序和总权重一致
    cache = Cache(5)
    cache.put("a", "A", 3)
    cache.put("b", "B", 2)
    cache.get("a")
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "cache.json")
        cache.save(path)
        restored = Cache.load(path)
        assert list(restored.data) == list(cache.data) == ["b", "a"]
        assert restored.used == cache.used


if __name__ == "__main__":
    test()
