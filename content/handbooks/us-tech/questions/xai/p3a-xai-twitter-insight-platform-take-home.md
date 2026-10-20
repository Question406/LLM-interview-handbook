---
id: p3a-xai-twitter-insight-platform-take-home
section: xai
order: 600
level: A
title: "xAI：Twitter 分析平台：数据校验、Grok worker 与限流"
quick: "Twitter 分析 take-home 先交付一条能重跑的端到端流程：按推文 id 去重入库，worker 调模型打分并记录重试和失败，入口限流和调用外部模型的出站限流分开计量。"
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · twitter-insight-platform-take-home"
    url: https://www.1point3acres.com/interview/problems/company/xai/twitter-insight-platform-take-home
    type: secondary
---

## 题目

这是一道 take-home：读取一份推文数据集，校验每条记录后入库，再异步调用 Grok 之类的模型给推文打分。还要加上入口和出站两套限流，并把整个服务容器化。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

先交付一条能从头跑到尾、可以重跑的最小流程，再逐步加功能。几个关键设计：

- 去重：用推文 id 做主键，同一份数据导入两次不会产生重复任务。
- 任务状态：每条推文有 pending、running、done、failed 几种状态，并记录尝试次数。worker 失败要落库，支持有限次数的重试。
- 两套限流分开：入口限流保护自己的服务不被灌爆，出站限流是为了不超过外部模型 API 的额度，两者的数值和计量对象都不同。
- 配置：API key 等敏感信息通过环境变量注入，不写进代码或镜像。
- 测试：用一个 mock 模型服务模拟错误响应和超时，验证失败路径。

允许用哪些工具，以当次任务说明为准。

## 完整编程练习（手册重构版）

这份练习只实现流水线的核心逻辑，不包括 HTTP 服务和 Dockerfile。

### 题面、接口与约束

- `Pipeline(db_path, model, in_limit=100, out_limit=10, width=60)`：用 SQLite 持久化。启动时把上次残留的 running 任务重置成 pending。
- `ingest(records, now)`：只接受 `{"id": 非空字符串, "text": 字符串}` 这种记录。每个长度为 `width` 的固定窗口里，最多 `in_limit` 条合法记录可以进入（重复 id 也占额度）。id 已存在的不会重复入库。返回 `(inserted, rejected)`：新插入的条数、因非法或超额被拒绝的条数。
- `run_one(now)`：原子地领取一条 pending 任务，受全局出站窗口限制，调用 `model(text, request_id=id)`。返回值必须是 [0, 1] 内的有限数，成功记为 done，异常或越界记为 failed。返回任务 id；没有任务或额度用完时返回 `None`。
- `retry(id)`：failed 且尝试次数小于 3 的任务重新排队，返回是否成功。
- `rows()`：按 id 返回所有记录，便于检查。
- `shutdown()`：关闭连接，之后再调用其他方法抛 `RuntimeError`。调用方要先等所有 `run_one` 返回。
- 语义是至少一次：模型适配层必须按 `request_id` 做幂等，不能声称外部调用恰好一次。时间非负，每次 `run_one` 只处理一条，最多 10000 条记录。

### 输入输出示例

```text
pipeline = Pipeline(path, model, out_limit=1)
pipeline.ingest([{"id": "a", ...}, {"id": "a", ...}, {"id": "b", ...}, {}], now=0)  -> (2, 1)
pipeline.run_one(0)   -> "a"
pipeline.run_one(1)   -> None    # 同一窗口出站额度用完，b 保持 pending
pipeline.run_one(60)  -> "b"     # 下一个窗口
```

两条 id 为 `a` 的记录只插入一次；空字典不合法，被拒绝。

### 解题思路与正确性

`ingest` 先校验格式，再扣入口额度，最后用 `INSERT OR IGNORE` 依靠主键去重，所以重复导入不会重复创建任务。

`run_one` 分三段。第一段持锁：查出一条 pending、扣出站额度、把状态改成 running 并提交，这样两个 worker 不会领到同一条。第二段在锁外调用模型，避免一个慢请求阻塞其他 worker。第三段再持锁写回结果。

状态都在数据库里，进程重启后能恢复。但崩溃可能发生在「领取之后、调用之前」，也可能发生在「调用之后、写回之前」，后一种情况重启后会再调一次模型。所以每次调用都带上稳定的 `request_id`（就是推文 id），让下游能识别重复请求。

入口和出站用不同的键计数，互不占用额度。

### 完整参考实现（Python 3）

```python
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
```

### 可执行测试

```python
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
```

### 复杂度与追问

设表中记录数为 N。这个最小版本没有建索引，领取任务时按 status 过滤再按 id 排序，最坏是 O(N)；给 `(status, id)` 建复合索引后可以降到 O(log N)。每次写操作都是一个 SQLite 事务，保证落盘。

- 重启后限流额度会重置，怎么办？现在的计数只在内存里。如果要求重启后额度连续，就把计数表也放进数据库，和领取任务在同一个事务里更新。
- 要扩展到多进程或多台机器呢？领取任务必须由数据库原子完成（比如用条件更新 `UPDATE ... WHERE status = 'pending'` 并检查影响行数），限流配额也要放到共享存储里统一计数。
- 能不能在模型调用进行时关闭服务？这个版本不支持。`shutdown` 之前要先等所有 worker 返回，否则写回结果时连接已经关了。

## 相关题

- [[p3a-xai-rate-limiter-design]]：只讲本题里入口限流和出站限流的设计，以及两者之间怎么用有界队列和背压衔接，不用写代码。
