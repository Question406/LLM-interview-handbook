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


def test():
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


if __name__ == "__main__":
    test()
