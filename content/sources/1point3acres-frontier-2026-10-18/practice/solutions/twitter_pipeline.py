import math
import sqlite3
import threading

MAX_ATTEMPTS = 3


def is_valid_record(record):
    """合法记录只有 id 和 text 两个字段：id 是非空字符串，text 是字符串。"""
    return (
        isinstance(record, dict)
        and set(record) == {"id", "text"}
        and isinstance(record["id"], str)
        and record["id"] != ""
        and isinstance(record["text"], str)
    )


class Pipeline:
    """推文入库 + 模型打分的最小流水线，SQLite 持久化，入口和出站分别做固定窗口限流。

    状态机：pending -> running -> done / failed；failed 可以 retry 回 pending。
    """

    def __init__(self, db_path, model, in_limit=100, out_limit=10, width=60):
        if min(in_limit, out_limit, width) < 1:
            raise ValueError("in_limit, out_limit and width must be >= 1")
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self.model = model
        self.closed = False
        self.in_limit = in_limit
        self.out_limit = out_limit
        self.width = width
        self.usage = {}  # (方向, 窗口编号) -> 已用次数；只在内存里，重启后清零

        self.db.execute(
            "CREATE TABLE IF NOT EXISTS tweets ("
            "id TEXT PRIMARY KEY, text TEXT, status TEXT, score REAL, attempts INTEGER)"
        )
        # 上次进程在 running 状态崩溃的任务重新排队：至少一次语义
        self.db.execute("UPDATE tweets SET status = 'pending' WHERE status = 'running'")
        self.db.commit()

    def _ensure_open(self):
        if self.closed:
            raise RuntimeError("pipeline is shut down")

    def _allow(self, direction, now, limit):
        """固定窗口计数；调用方必须持有 self.lock。"""
        if now < 0:
            raise ValueError("time must be non-negative")
        key = (direction, now // self.width)
        used = self.usage.get(key, 0)
        if used >= limit:
            return False
        self.usage[key] = used + 1
        return True

    def ingest(self, records, now):
        """返回 (新插入条数, 被拒绝条数)。重复 id 占用入口额度，但不会重复入库，也不算拒绝。"""
        inserted = 0
        rejected = 0
        with self.lock:
            self._ensure_open()
            for record in records:
                if not is_valid_record(record) or not self._allow("in", now, self.in_limit):
                    rejected += 1
                    continue
                cursor = self.db.execute(
                    "INSERT OR IGNORE INTO tweets VALUES (?, ?, 'pending', NULL, 0)",
                    (record["id"], record["text"]),
                )
                inserted += cursor.rowcount
            self.db.commit()
        return inserted, rejected

    def run_one(self, now):
        """领取一条 pending 任务并调用模型；没有任务或出站额度用完时返回 None。"""
        with self.lock:
            self._ensure_open()
            row = self.db.execute(
                "SELECT id, text FROM tweets WHERE status = 'pending' ORDER BY id LIMIT 1"
            ).fetchone()
            if row is None or not self._allow("out", now, self.out_limit):
                return None
            tweet_id, text = row
            self.db.execute(
                "UPDATE tweets SET status = 'running', attempts = attempts + 1 WHERE id = ?",
                (tweet_id,),
            )
            self.db.commit()

        # 模型调用放在锁外，不阻塞其他 worker；request_id 固定，方便下游做幂等
        try:
            score = float(self.model(text, request_id=tweet_id))
            if not math.isfinite(score) or not 0 <= score <= 1:
                raise ValueError(f"score out of range: {score}")
            status = "done"
        except Exception:
            score = None
            status = "failed"

        with self.lock:
            self.db.execute(
                "UPDATE tweets SET status = ?, score = ? WHERE id = ?",
                (status, score, tweet_id),
            )
            self.db.commit()
        return tweet_id

    def retry(self, tweet_id):
        """failed 且尝试次数不足 MAX_ATTEMPTS 时重新排队，返回是否成功。"""
        with self.lock:
            self._ensure_open()
            cursor = self.db.execute(
                "UPDATE tweets SET status = 'pending' "
                "WHERE id = ? AND status = 'failed' AND attempts < ?",
                (tweet_id, MAX_ATTEMPTS),
            )
            self.db.commit()
            return bool(cursor.rowcount)

    def rows(self):
        with self.lock:
            self._ensure_open()
            return self.db.execute(
                "SELECT id, text, status, score, attempts FROM tweets ORDER BY id"
            ).fetchall()

    def shutdown(self):
        """关闭数据库连接。约定：调用方先等所有正在执行的 run_one 返回，再调用 shutdown。"""
        with self.lock:
            if not self.closed:
                self.closed = True
                self.db.close()


def test():
    import os
    import tempfile

    calls = []

    def model(text, request_id):
        calls.append(request_id)
        return 0.7

    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "db.sqlite")
        pipeline = Pipeline(path, model, out_limit=1)

        # 重复 id 不重复入库；非法记录被拒绝
        records = [{"id": "a", "text": "hello"}, {"id": "a", "text": "again"}, {"id": "b", "text": "world"}, {}]
        assert pipeline.ingest(records, 0) == (2, 1)

        # 出站每个窗口只允许 1 次：同窗口第二次返回 None，下一窗口继续
        assert pipeline.run_one(0) == "a"
        assert pipeline.run_one(1) is None
        assert pipeline.run_one(60) == "b"
        assert calls == ["a", "b"]
        assert all(row[2] == "done" for row in pipeline.rows())

        # 重启后数据还在，没有待处理任务
        pipeline.shutdown()
        pipeline = Pipeline(path, model)
        assert len(pipeline.rows()) == 2
        assert pipeline.run_one(61) is None
        pipeline.shutdown()

        # 关闭后再调用会报错
        try:
            pipeline.rows()
        except RuntimeError:
            pass
        else:
            raise AssertionError("rows() after shutdown should raise RuntimeError")

    # 模型返回越界分数记为 failed，最多重试到第 3 次
    with tempfile.TemporaryDirectory() as directory:
        pipeline = Pipeline(os.path.join(directory, "db.sqlite"), lambda text, request_id: 1.5)
        pipeline.ingest([{"id": "x", "text": "bad"}], 0)
        for attempt in range(1, MAX_ATTEMPTS + 1):
            assert pipeline.run_one(attempt) == "x"
            assert pipeline.rows()[0][2:] == ("failed", None, attempt)
            assert pipeline.retry("x") == (attempt < MAX_ATTEMPTS)
        pipeline.shutdown()


if __name__ == "__main__":
    test()
