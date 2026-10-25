---
id: p3a-perplexity-embedding-model-batching-service
section: design
order: 612
level: S
title: "Perplexity：Embedding 批服务：并发、容量与 shutdown"
quick: "用队列连接 submit 和后台 worker：每个请求带着自己的 Future 入队，worker 按条数与 token 预算组批，再把结果逐个写回。shutdown 停止接收请求并把哨兵放到队尾，已有请求处理完才退出，模型异常则传给整批 Future。"
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

## 题目描述

实现一个线程安全的模型批处理服务。调用者逐条提交 token 序列并立即拿到 Future，后台 worker 将请求组成满足条数和 token 预算的批次调用模型，再把每个结果交回对应请求。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `BatchService(model, max_batch, max_tokens)`：启动一个后台 worker。`model(list_of_sequences)` 返回等长的结果列表，元素可以是任意对象。
- `submit(tokens) -> Future`：可以被多个线程并发调用。假定单条请求的 token 数不超过 `max_tokens`；shutdown 之后的新提交被拒绝。
- 每批的序列条数不超过 `max_batch`，token 总数不超过 `max_tokens`，请求不拆分。
- `shutdown()`：停止接收新请求，排空所有已接收的请求后结束 worker。
- 模型抛出的异常传给本批每个 `Future`。最多 1000 个请求，结果不能串位。

### 示例

```text
model = 对每条序列求和；max_batch=2，max_tokens=4
submit([1, 2]), submit([3]), submit([4, 5, 6]), submit([])
shutdown() 后结果依次为   -> 3, 3, 15, 0
组批大致是 [[1, 2], [3]]、[[4, 5, 6], []]（具体分组取决于 worker 取队列的时机）
模型抛 ValueError         -> 本批每个 future.result() 都抛 ValueError
```

## 解题思路与参考答案

## 题目

给定一个能一次处理一批序列的 embedding 模型，把它包装成一个服务：多个调用方并发提交单条请求，服务在后台把请求攒成批送进模型，再把结果分别还给各自的调用方。变体要求每批同时受「序列条数」和「token 总数」两个上限约束，并且要能干净地 shutdown。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

我会用生产者-消费者结构，把每条请求和它的 `Future` 一起入队。`submit` 立刻返回 `Future`，后台 worker 取请求组批、调用模型，再把结果逐个写回。请求从入队起就和返回位置绑定，所以并发提交也不会串结果。

每批同时检查条数和 token 总数。下一条放不下时，整条留作下一批开头；单条就超过 token 预算的，在 `submit` 直接拒绝。模型抛异常或返回条数不对时，本批所有 `Future` 都必须收到异常，避免调用方一直等待。

shutdown 要先约定排空还是取消。这份实现选择排空：停止接收后，把哨兵排在所有已接收请求之后，worker 处理到哨兵再退出。`closed` 检查和入队共用一把锁，才能保证没有请求落在哨兵后面。

上线后，把排队等待和模型执行时间分别统计，就能判断延迟来自组批策略，还是模型本身。

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

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert len(batch) <= 2` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

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
