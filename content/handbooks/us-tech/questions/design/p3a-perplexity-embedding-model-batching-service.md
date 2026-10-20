---
id: p3a-perplexity-embedding-model-batching-service
section: design
order: 612
level: S
title: "Perplexity：Embedding 批服务：并发、容量与 shutdown"
quick: "submit 把请求和 Future 一起入队，后台 worker 按条数和 token 预算组批、把结果按位置写回各自的 Future；shutdown 用排在最后的哨兵排空队列，模型异常传给整批。"
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Perplexity · embedding-model-batching-service"
    url: https://www.1point3acres.com/interview/problems/company/perplexity/embedding-model-batching-service
    type: secondary
---

## 题目

给定一个能一次处理一批序列的 embedding 模型，把它包装成一个服务：多个调用方并发提交单条请求，服务在后台把请求攒成批送进模型，再把结果分别还给各自的调用方。变体要求每批同时受「序列条数」和「token 总数」两个上限约束，并且要能干净地 shutdown。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

结构是「生产者-消费者」：`submit` 把请求和一个新建的 `Future` 一起放进队列并立刻返回 `Future`；一个后台 worker 从队列里取请求组批、调用模型，再把结果逐个写回对应的 `Future`。请求和 `Future` 从入队起就绑在一起，所以结果不会串位。

组批时有三个细节：

- 两个上限都要检查。下一条请求加进来会超 token 预算时，不能拆开它，也不能丢掉它，要留到下一批的开头。
- 单条请求本身就超过 token 上限时，任何一批都装不下，应该在 `submit` 时直接拒绝。
- 模型抛异常或返回的结果条数不对时，本批每个 `Future` 都要收到异常，不能有调用方永远等下去。

shutdown 要先和面试官约定是「排空」（处理完已接收的请求再停）还是「取消」（未开始的直接失败）。排空的常见写法是往队列里放一个哨兵，worker 读到哨兵就退出；哨兵排在所有已接收请求之后，自然就排空了。`closed` 标志的检查和入队要在同一把锁里，否则可能有请求排在哨兵后面，永远没人处理。

上线时还应该把排队等待时间和模型执行时间分开度量，才能判断瓶颈在组批策略还是模型本身。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `BatchService(model, max_batch, max_tokens)`：启动一个后台 worker。`model(list_of_sequences)` 返回等长的结果列表，元素可以是任意对象。
- `submit(tokens) -> Future`：可以被多个线程并发调用。单条请求超过 `max_tokens` 时立即抛 `ValueError`；shutdown 之后调用抛 `RuntimeError`。
- 每批的序列条数不超过 `max_batch`，token 总数不超过 `max_tokens`，请求不拆分。
- `shutdown()`：停止接收新请求，排空所有已接收的请求后结束 worker。
- 模型抛出的异常传给本批每个 `Future`。最多 1000 个请求，结果不能串位。

### 输入输出示例

```text
model = 对每条序列求和；max_batch=2，max_tokens=4
submit([1, 2]), submit([3]), submit([4, 5, 6]), submit([])
shutdown() 后结果依次为   -> 3, 3, 15, 0
组批大致是 [[1, 2], [3]]、[[4, 5, 6], []]（具体分组取决于 worker 取队列的时机）
模型抛 ValueError         -> 本批每个 future.result() 都抛 ValueError
```

### 解题思路与正确性

worker 只搬运 `(tokens, future)` 对，模型输出按位置 `zip` 回本批的 `Future`，所以结果一定落到发起它的请求上。组批时装不下的下一条请求放进 `held`，作为下一批的第一条，不会丢。

shutdown 的哨兵是在锁内、`closed` 置位的同时入队的，之后再没有请求能入队，所以哨兵前面就是全部已接收的请求，worker 处理完它们才退出。调用方提前取消的 `Future` 会在送进模型前被 `set_running_or_notify_cancel` 过滤掉；已经开始运行的请求无法再取消。

### 完整参考实现（Python 3）

```python
from concurrent.futures import Future
from queue import Empty, Queue
from threading import Lock, Thread

STOP = None  # 队列里的哨兵：排在它之前的请求都会被处理完


class BatchService:
    """把并发提交的 token 序列攒成批交给 model；每个请求拿到自己的 Future。"""

    def __init__(self, model, max_batch=8, max_tokens=100):
        if max_batch < 1 or max_tokens < 1:
            raise ValueError("max_batch and max_tokens must be positive")
        self.model = model
        self.max_batch = max_batch
        self.max_tokens = max_tokens
        self.queue = Queue()  # 元素是 (tokens, future) 或 STOP
        self.lock = Lock()    # 保证 closed 检查和入队是原子的
        self.closed = False
        self.worker = Thread(target=self._run)
        self.worker.start()

    def submit(self, tokens):
        tokens = list(tokens)
        if len(tokens) > self.max_tokens:
            raise ValueError(f"request has {len(tokens)} tokens, limit is {self.max_tokens}")
        with self.lock:
            if self.closed:
                raise RuntimeError("service is shut down")
            future = Future()
            self.queue.put((tokens, future))
            return future

    def shutdown(self):
        """停止接收新请求，排空已接收的请求后结束 worker。"""
        with self.lock:
            if not self.closed:
                self.closed = True
                self.queue.put(STOP)
        self.worker.join()

    def _run(self):
        held = None  # 上一批装不下、留给下一批开头的请求
        while True:
            first = held if held is not None else self.queue.get()
            if first is STOP:
                return
            batch, held, stopping = self._collect_batch(first)
            self._run_batch(batch)
            if stopping:
                return

    def _collect_batch(self, first):
        """以 first 开头，不等待地取出队列里能装下的请求。返回 (batch, held, stopping)。"""
        batch = [first]
        total_tokens = len(first[0])
        while len(batch) < self.max_batch:
            try:
                item = self.queue.get_nowait()
            except Empty:
                break
            if item is STOP:
                return batch, None, True
            if total_tokens + len(item[0]) > self.max_tokens:
                return batch, item, False  # 不拆请求，也不丢弃，留到下一批
            batch.append(item)
            total_tokens += len(item[0])
        return batch, None, False

    def _run_batch(self, batch):
        # 已被调用方取消的请求不送进模型
        live = [(tokens, future) for tokens, future in batch if future.set_running_or_notify_cancel()]
        if not live:
            return
        try:
            outputs = list(self.model([tokens for tokens, _ in live]))
            if len(outputs) != len(live):
                raise ValueError(f"model returned {len(outputs)} results for {len(live)} inputs")
        except Exception as error:
            for _, future in live:
                future.set_exception(error)  # 整批失败，但每个 Future 都会完成
        else:
            for (_, future), output in zip(live, outputs):
                future.set_result(output)
```

### 可执行测试

```python
# 每批最多 2 条、4 个 token；结果按原请求对应
batches = []

def sum_model(batch):
    assert len(batch) <= 2
    assert sum(map(len, batch)) <= 4
    batches.append(batch)
    return [sum(tokens) for tokens in batch]

service = BatchService(sum_model, max_batch=2, max_tokens=4)
futures = [service.submit(tokens) for tokens in ([1, 2], [3], [4, 5, 6], [])]
service.shutdown()
assert [future.result(timeout=1) for future in futures] == [3, 3, 15, 0]

# shutdown 之后拒绝新请求；单个请求超过 token 上限直接拒绝
try:
    service.submit([1])
except RuntimeError:
    pass
else:
    raise AssertionError("submit after shutdown should raise RuntimeError")
service = BatchService(sum_model, max_batch=2, max_tokens=4)
try:
    service.submit([1, 2, 3, 4, 5])
except ValueError:
    pass
else:
    raise AssertionError("oversized request should raise ValueError")
service.shutdown()

# 模型抛错时，本批每个 Future 都收到同一个异常
def failing_model(batch):
    raise ValueError("model failed")

service = BatchService(failing_model, max_batch=2, max_tokens=4)
future = service.submit([1])
service.shutdown()
try:
    future.result(timeout=1)
except ValueError:
    pass
else:
    raise AssertionError("model error should propagate to the future")

# 模型返回数量不对，也当作整批失败
service = BatchService(lambda batch: [], max_batch=2, max_tokens=4)
future = service.submit([1])
service.shutdown()
assert isinstance(future.exception(timeout=1), ValueError)
```

### 复杂度与追问

设请求数为 R、token 总数为 T。worker 的调度开销是 O(R + T)（主要是复制 token 列表），队列空间与未完成请求的 token 数成正比。这份参考用的是无界队列，没有背压。

- 背压：把 `Queue` 换成有界队列，满了以后 `submit` 是阻塞、超时还是直接拒绝，要和调用方约定。
- 吞吐和延迟的取舍：现在 worker 只取「此刻已经在队列里」的请求，低负载时批会很小。可以在拿到第一条后再最多等几毫秒凑批，用一点延迟换更大的批。
- 超时和取消：调用方可以 `future.cancel()`，但只在请求还没送进模型前有效。
- 多个 worker 或多张 GPU：每个 worker 各自取队列组批即可，但要确认模型对象是否线程安全。
