from copy import deepcopy


class KV:
    """支持嵌套事务和快照分支的 KV。

    layers[0] 是已提交数据，之后每一层是一个打开的事务，保存进入该事务时的完整工作副本。
    所有读写都只看最顶层。
    """

    def __init__(self, data=None):
        self.layers = [deepcopy(data or {})]
        self.snapshots = []

    def _require_transaction(self):
        if len(self.layers) == 1:
            raise ValueError("no active transaction")

    def get(self, key):
        """不存在返回 None；返回深拷贝，调用方改返回值不会影响存储。"""
        return deepcopy(self.layers[-1].get(key))

    def set(self, key, value):
        if value is None:
            raise ValueError("None is reserved for missing keys")
        self.layers[-1][key] = deepcopy(value)

    def delete(self, key):
        """删除成功返回 True，键本来不存在返回 False。"""
        return self.layers[-1].pop(key, None) is not None

    def begin(self):
        self.layers.append(deepcopy(self.layers[-1]))

    def commit(self):
        """只提交最内层事务：用它的工作副本替换父层。"""
        self._require_transaction()
        committed = self.layers.pop()
        self.layers[-1] = committed

    def rollback(self):
        """丢弃最内层事务的全部改动。"""
        self._require_transaction()
        self.layers.pop()

    def snapshot(self):
        """记录当前可见数据（含未提交事务的改动），返回快照 id。"""
        self.snapshots.append(deepcopy(self.layers[-1]))
        return len(self.snapshots) - 1

    def fork(self, snapshot_id):
        """从快照创建一个独立的新 KV，两边后续写入互不影响。"""
        if not 0 <= snapshot_id < len(self.snapshots):
            raise ValueError(f"unknown snapshot id: {snapshot_id}")
        return KV(self.snapshots[snapshot_id])


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 嵌套事务：内层删除，回滚后恢复外层的值
    store = KV()
    store.set("a", 1)
    store.begin()
    store.set("a", 2)
    store.begin()
    store.delete("a")
    assert store.get("a") is None
    store.rollback()
    assert store.get("a") == 2
    store.commit()
    assert store.get("a") == 2

    # 单层事务回滚回到提交前的值
    store.begin()
    store.set("a", 5)
    store.rollback()
    assert store.get("a") == 2

    # fork 出来的分支写入不影响原实例
    snapshot_id = store.snapshot()
    branch = store.fork(snapshot_id)
    branch.set("a", 3)
    assert store.get("a") == 2
    assert branch.get("a") == 3

    # get 返回的可变值是副本
    store.set("a", [1])
    value = store.get("a")
    value.append(2)
    assert store.get("a") == [1]

    # 没有事务时 commit/rollback 报错；None 不能作为值；未知快照报错
    expect_value_error(store.commit)
    expect_value_error(store.rollback)
    expect_value_error(store.set, "b", None)
    expect_value_error(store.fork, 99)
    assert store.delete("missing") is False


if __name__ == "__main__":
    test()
