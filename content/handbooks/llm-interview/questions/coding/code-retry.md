---
id: code-retry
section: coding
order: 8
level: S
title: 实现 Tool Retry + Idempotency：Timeout 后为什么不能直接重试？
quick: >-
  Timeout 只说明客户端没看到结果，服务端可能已经执行了。有副作用的操作要带 idempotency key 或 transaction ID，超时后先查状态或让 server 去重，再决定要不要重试；retry policy 按 error class 分开定。
tags:
  - Agent
  - Distributed Systems
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources: []
---

## 题目描述

实现一个异步工具调用执行器，在超时后先查询执行状态，并用固定幂等键控制重试，避免把已经成功的操作再次执行。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `async safe_execute(tool,args,client,max_attempts=3)`。client提供异步call(tool,args,`idempotency_key`)、`get_status`(key)、`get_result`(key)；`make_idempotency_key`和异步backoff由环境提供。`max_attempts`≥1。

### 输出与约束

同一次`safe_execute`的所有call使用同一个key。call成功直接返回；TimeoutError后状态SUCCEEDED则取结果返回，RUNNING继续下一轮，`FAILED_RETRYABLE`先backoff再重试；其他状态重新抛出超时。最多调用`max_attempts`次，预算耗尽抛RuntimeError。这里的超时与状态分支属于题目正常业务输入。

### 示例

```text
场景1：首次call超时，get_status返回SUCCEEDED，get_result返回"ok"
结果="ok"，call次数=1。
场景2：首次超时且状态FAILED_RETRYABLE，第二次call返回"ok"
结果="ok"，两次call的幂等键相同。
```

<!-- problem-statement:end -->

<h2>解题思路与参考答案</h2>

<div class="quick"><div class="mini-title">30 秒回答</div><p>Timeout 只说明客户端没看到结果，服务端可能已经执行了。有副作用的操作要带 idempotency key 或 transaction ID，超时后先查状态或让 server 去重，再决定要不要重试；retry policy 按 error class 分开定。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Timeout 之后不能直接重试，因为它只说明客户端没看到结果，服务端可能已经执行完了。比如一次 send_email 超时，直接再发一次，用户就可能收到两封邮件。所以我会给每次调用生成一个 idempotency key，超时后先拿这个 key 去查状态，再决定是取结果、继续等，还是退避重试：</p><pre><code data-lang="python">async def safe_execute(tool, args, client, max_attempts=3):
    key = make_idempotency_key(tool, args)
    for attempt in range(max_attempts):
        try:
            return await client.call(tool, args, idempotency_key=key)
        except TimeoutError:
            status = await client.get_status(key)
            if status == &quot;SUCCEEDED&quot;:
                return await client.get_result(key)
            if status == &quot;RUNNING&quot;:
                continue
            if status == &quot;FAILED_RETRYABLE&quot;:
                await backoff(attempt)
                continue
            raise
    raise RuntimeError(&quot;retry budget exhausted&quot;)</code></pre><p>GET、search 这类幂等的读操作，通常可以放心重试。send_money、send_email、delete 或者 create resource 就可能产生重复的副作用。服务端要按 idempotency key 保存唯一的执行记录，客户端重复请求时拿到的是同一个结果。</p><p>错误至少要分成四类来处理。4xx 的 invalid argument 或 permission，通常不该重试；429、5xx 这类 transient 错误，可以退避后再试；unknown outcome，先查状态；semantic failure 要让模型改 action，把原调用原样再打一遍没有用。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Exactly-once 真能严格做到吗？</summary><div class="follow-answer"><p>跨分布式系统时，所谓 exactly once 常常是靠幂等的 side effect 加上可持久化的 transaction state，做到在可观察的层面上只发生一次。网络层仍然可能是 at-least-once delivery，所以我会把 transport 和业务语义分开讲。</p></div></details></div>

<h2>简单测试怎么写</h2>
<p>先把上面的 safe_execute 函数放进 solution.py，再追加以下测试代码，运行 python3 solution.py。全部使用内存中的假客户端，通过后输出 simple tests passed。</p>
<p>不用连真实服务：假客户端第一次抛超时，状态查询分别返回成功或可重试失败。成功状态要取回原结果，失败可重试时才再次 call；两次 call 必须携带同一幂等键。make_idempotency_key 和 backoff 是参考片段需要的测试桩，实际系统要使用业务约定的幂等键和退避策略。</p>
<pre><code class="language-python">import asyncio

def make_idempotency_key(tool, args):
    return f&quot;{tool}:{args[&#x27;id&#x27;]}&quot;

async def backoff(attempt):
    pass  # 测试不等待真实时间

class FakeClient:
    def __init__(self, status):
        self.status, self.calls, self.keys = status, 0, []

    async def call(self, tool, args, idempotency_key):
        self.calls += 1
        self.keys.append(idempotency_key)
        if self.calls == 1:
            raise TimeoutError()
        return &quot;result&quot;

    async def get_status(self, key):
        return self.status

    async def get_result(self, key):
        return &quot;cached result&quot;

async def test_retry():
    completed = FakeClient(&quot;SUCCEEDED&quot;)
    assert await safe_execute(&quot;create&quot;, {&quot;id&quot;: 1}, completed) == &quot;cached result&quot;
    assert completed.calls == 1
    retryable = FakeClient(&quot;FAILED_RETRYABLE&quot;)
    assert await safe_execute(&quot;create&quot;, {&quot;id&quot;: 1}, retryable) == &quot;result&quot;
    assert retryable.calls == 2 and len(set(retryable.keys)) == 1
    running = FakeClient(&quot;RUNNING&quot;)
    try:
        await safe_execute(&quot;create&quot;, {&quot;id&quot;: 1}, running, max_attempts=1)
    except RuntimeError:
        pass
    else:
        raise AssertionError(&quot;exhausted retry budget must fail&quot;)

asyncio.run(test_retry())
print(&quot;simple tests passed&quot;)
</code></pre>
