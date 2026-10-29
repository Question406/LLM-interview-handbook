---
id: openai-async-tree-count-idempotency
section: openai
order: 900
level: A
title: "OpenAI：只用 async messages 给整棵树计数"
quick: "我会让每个节点先记下这次 request 的 parent，再向 children 发 COUNT。收到 RESULT 后，以 child ID 为 key 保存；同一 child 的第二份结果不会再加一次。"
companies:
  - openai
tags:
  - "Frontier Coding 2026-10-28"
  - 完整编程练习
  - "候选人报告改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "候选人记录：OpenAI distributed tree counting"
    url: "https://www.screna.ai/experience/aa1b5634-5b22-42a3-9077-5787f791e718"
    type: interview
---

## 题目描述

来源：Screna 的公开候选人记录提到每个节点为独立机器，只能通过 async sendMessage/receiveMessage 让 root 计数。以下为手册定义的消息接口，并加入重复投递与并发 request IDs 作为练习规则。

### 输入、接口与规则

实现 `CountNode(node_id, children)`，每个实例只知道自己的 ID 和直接 children IDs。外部网络调用 `receive(kind, request, sender, count=None)`，返回需要发送的消息列表；每条为 `(destination, kind, request, sender, count)`。kind 为 COUNT 或 RESULT。Root 通过 COUNT、sender=None 发起，RESULT 的 count 为正整数。`result(request)` 在该节点完成聚合前返回 None，完成后返回 subtree 节点数。

输入拓扑为有限、无环、固定的 rooted tree，child 不重复。允许多个唯一 request IDs 并发；同一个消息可重复投递、不同 children 的结果可乱序，但所有已发送消息最终至少送达一次，节点不崩溃。有效 RESULT 来自 COUNT 发出的对应 child；相同 child 的重复结果数值一致。

每个 child 对同一 request 只计一次，节点自身计 1；重复 COUNT 不能重新累加。状态保留到调用方清理，本题无需实现 timeout、网络 socket 或持久化。不允许读取全局 topology 或用阻塞递归直接遍历所有节点。

### 输入输出示例

```text
0 的 children=[1,2]，1 的 children=[3,4]，其他为 leaves。
Root 发起 request="A"；即使每条 RESULT 被送两次且乱序，root.result("A") 最终返回 5。
```

## 回答思路

> **输入与任务：** 每个节点只能知道局部 children，消息会重复、乱序。  
> **做法与原因：** 按 request ID 保存状态，再按 child ID 去重，收齐后返回 1+子树之和。  
> **正确性检查：** 随机打乱并复制消息，同时运行两个 request，核对 root 和内部节点结果。

## 解题思路与参考答案

我会让每个节点先记下这次 request 的 parent，再向 children 发 COUNT。收到 RESULT 后，以 child ID 为 key 保存；同一 child 的第二份结果不会再加一次。

所有 children 都回复后，把总数加上自己这个节点，再回给 parent。不同 request 分开保存状态，重复 COUNT 完成后可以重发缓存结果。这个实现依赖最终送达与节点持续运行。

### 完整参考实现

```python
class CountNode:
    def __init__(self, node_id, children):
        self.node_id = node_id
        self.children = tuple(children)
        self.runs = {}

    def receive(self, kind, request, sender, count=None):
        outgoing = []
        if kind == "COUNT":
            if request in self.runs:
                run = self.runs[request]
                if run["parent"] != sender:
                    raise ValueError("same request arrived from a different parent")
                if run["done"] and sender is not None:
                    outgoing.append(
                        (sender, "RESULT", request, self.node_id, run["total"])
                    )
                return outgoing
            run = {"parent": sender, "received": {}, "total": 1, "done": False}
            self.runs[request] = run
            for child in self.children:
                outgoing.append((child, "COUNT", request, self.node_id, None))
        elif kind == "RESULT":
            run = self.runs[request]
            if sender not in self.children or type(count) is not int or count < 1:
                raise ValueError("invalid child result")
            if sender in run["received"]:
                if run["received"][sender] != count:
                    raise ValueError("conflicting duplicate result")
                return outgoing
            run["received"][sender] = count
            run["total"] += count
        else:
            raise ValueError("unknown message")
        if len(run["received"]) == len(self.children):
            run["done"] = True
            if run["parent"] is not None:
                outgoing.append(
                    (run["parent"], "RESULT", request, self.node_id, run["total"])
                )
        return outgoing

    def result(self, request):
        run = self.runs.get(request)
        return run["total"] if run and run["done"] else None
```

## 简单测试怎么写

将实现与下面测试按顺序保存为 `solution.py`，使用安装 NumPy/PyTorch 的 Python 运行 `python solution.py`。先核对题面的手算输出，再执行下列 assertions。

```python
import random

children = {0: [1, 2], 1: [3, 4], 2: [], 3: [], 4: []}
for seed in range(20):
    nodes = {i: CountNode(i, sub) for i, sub in children.items()}
    rng = random.Random(seed)
    queue = [(0, "COUNT", request, None, None) for request in ("A", "B")]
    processed = 0
    while queue:
        index = rng.randrange(len(queue))
        destination, kind, request, sender, count = queue.pop(index)
        outputs = nodes[destination].receive(kind, request, sender, count)
        for message in outputs:
            queue.extend([message, message])  # Duplicated delivery, arbitrary order.
        processed += 1
        assert processed < 10000
    assert nodes[0].result("A") == 5 and nodes[0].result("B") == 5
    assert nodes[1].result("A") == 3
    assert nodes[4].result("A") == 1
    assert nodes[0].receive("COUNT", "A", None) == []
    assert nodes[0].result("A") == 5
single = CountNode(7, [])
assert single.result("new") is None
assert single.receive("COUNT", "new", None) == []
assert single.result("new") == 1
print("OpenAI async tree count: passed")
```

## 复杂度与追问

无重复时每条 edge 一次 COUNT、一次 RESULT，消息量 `O(N)`；没有时间上界时不对 latency 作固定承诺。每个 request 的全网状态约 `O(N)`。丢包重试、节点重启、run cleanup 与拓扑变化需要独立协议。
