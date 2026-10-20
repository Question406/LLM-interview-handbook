from bisect import bisect_right
from copy import deepcopy


class DB:
    """带历史版本、TTL 和备份恢复的 key/field 数据库。

    每个 (key, field) 按写入时间保存一串版本。版本的 value 为 None 表示删除标记，
    expires_at 为 None 表示永不过期。写入时间全局单调不减，查询可以回看任意历史时刻。
    """

    def __init__(self):
        self.times = {}     # (key, field) -> [写入时间, ...]，单调不减，供二分查找
        self.versions = {}  # (key, field) -> [(value, expires_at), ...]，与 times 一一对应
        self.clock = float("-inf")  # 最近一次写入的时间
        self.backups = []

    def _advance_clock(self, t):
        if t < self.clock:
            raise ValueError(f"write time {t} is earlier than last write {self.clock}")
        self.clock = t

    def _append(self, t, key, field, value, expires_at):
        self.times.setdefault((key, field), []).append(t)
        self.versions.setdefault((key, field), []).append((value, expires_at))

    def _at(self, t, key, field):
        """返回 t 时刻生效的 (value, expires_at)；不存在、已删除或已过期都返回 (None, None)。"""
        times = self.times.get((key, field), [])
        # 最后一个写入时间 <= t 的版本；同一时刻有多次写入时取最后一次
        index = bisect_right(times, t) - 1
        if index < 0:
            return None, None
        value, expires_at = self.versions[(key, field)][index]
        if expires_at is not None and t >= expires_at:
            return None, None  # 最新版本已过期时不能退回更早的旧值
        return value, expires_at

    def set(self, t, key, field, value, ttl=None):
        """在 t 时刻写入 value；有 ttl 时有效期是 [t, t + ttl)。"""
        if value is None:
            raise ValueError("value must not be None")
        if ttl is not None and ttl <= 0:
            raise ValueError(f"ttl must be positive, got {ttl}")
        self._advance_clock(t)
        expires_at = None if ttl is None else t + ttl
        self._append(t, key, field, deepcopy(value), expires_at)

    def delete(self, t, key, field):
        """在 t 时刻写入删除标记，返回删除前该字段是否有效。"""
        self._advance_clock(t)
        existed = self._at(t, key, field)[0] is not None
        self._append(t, key, field, None, None)
        return existed

    def get(self, t, key, field):
        return deepcopy(self._at(t, key, field)[0])

    def scan(self, t, key, prefix=""):
        """返回 t 时刻 key 下字段名以 prefix 开头的有效字段 [(field, value)]，按字段名升序。"""
        fields = sorted(f for k, f in self.times if k == key and f.startswith(prefix))
        result = []
        for field in fields:
            value = self.get(t, key, field)
            if value is not None:
                result.append((field, value))
        return result

    def backup(self, t):
        """保存 t 时刻所有有效字段的值和剩余 TTL，返回备份 id。备份只读，不推进时钟。"""
        snapshot = {}
        for key, field in self.times:
            value, expires_at = self._at(t, key, field)
            if value is None:
                continue
            remaining = None if expires_at is None else expires_at - t
            snapshot[(key, field)] = (deepcopy(value), remaining)
        self.backups.append(snapshot)
        return len(self.backups) - 1

    def restore(self, now, backup_id):
        """在 now 时刻用备份覆盖当前全部状态。更早的历史不变，TTL 从 now 重新计时。"""
        if not isinstance(backup_id, int) or not 0 <= backup_id < len(self.backups):
            raise ValueError(f"unknown backup id: {backup_id!r}")
        self._advance_clock(now)
        for key, field in list(self.times):
            self.delete(now, key, field)
        # 同一时刻后写覆盖先写，所以先删全部、再写回备份内容
        for (key, field), (value, remaining) in self.backups[backup_id].items():
            self.set(now, key, field, value, remaining)


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # TTL 有效期是左闭右开区间 [0, 5)
    db = DB()
    db.set(0, "a", "x", 7, 5)
    backup_id = db.backup(2)
    assert db.get(4, "a", "x") == 7
    assert db.get(5, "a", "x") is None

    # 备份时剩余 3，恢复后从 10 重新计时，有效到 13 之前
    db.restore(10, backup_id)
    assert db.get(12, "a", "x") == 7
    assert db.get(13, "a", "x") is None

    # restore 不改更早的历史
    assert db.get(1, "a", "x") == 7

    # 同一时刻后写覆盖先写
    db.set(14, "a", "z", 8)
    db.set(14, "a", "z", 9)
    assert db.scan(14, "a") == [("z", 9)]

    # 删除只影响删除时刻及以后
    assert db.delete(15, "a", "z") is True
    assert db.get(14, "a", "z") == 9
    assert db.get(15, "a", "z") is None
    assert db.delete(16, "a", "z") is False

    # scan 按字段名升序并按前缀过滤
    db.set(20, "u", "task-2", "b")
    db.set(20, "u", "task-1", "a")
    db.set(20, "u", "note", "c")
    assert db.scan(20, "u", "task") == [("task-1", "a"), ("task-2", "b")]

    # 存进去的可变值被深复制，外部修改不影响历史
    payload = {"n": 1}
    db.set(21, "u", "obj", payload)
    payload["n"] = 2
    assert db.get(21, "u", "obj") == {"n": 1}

    expect_value_error(db.set, 19, "a", "x", 1)      # 写入时间倒退
    expect_value_error(db.set, 22, "a", "x", 1, 0)   # ttl 必须为正
    expect_value_error(db.set, 22, "a", "x", None)   # None 留给删除标记
    expect_value_error(db.restore, 22, 99)           # 不存在的备份 id
    expect_value_error(db.restore, 22, -1)           # 负数 id 不能当成「最后一个」


if __name__ == "__main__":
    test()
