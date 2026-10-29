---
id: p3a-openai-distributed-cluster-count-topology
section: openai
order: 606
level: A
title: OpenAI：异步消息树：统计机器数与恢复拓扑
quick: >-
  根节点用 request id 发起子树汇总，节点收齐孩子后再返回自己的计数和拓扑。按 request id、child id
  去重并缓存结果，重复请求直接重发；失联子树标未知，不能当成 0。
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · OpenAI · distributed-cluster-count-topology
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/distributed-cluster-count-topology
    type: secondary
---

## 题目描述

给定树形集群的父子关系，模拟异步请求/回复收集全局节点数和拓扑。消息可能重复投递，重复不能改变最终结果。

以下为手册重构练习约定。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `cluster(children,root,duplicate=False) -> (count,topology)`；children 是节点标识到有序孩子列表的映射，叶子允许省略。
- 输入保证是以 root 为唯一根的有限树，至多1000节点；root 没有父节点，其他节点恰好一个父节点。
- count 是包括根和叶子的总节点数，topology 必须包含每个节点，叶子映射到 []，其余保留孩子顺序。
- 实现需通过模拟父子节点异步请求/回复完成收集，每次查询的 request id 唯一。duplicate=True 时每条消息投递两次，输出仍完全相同。本练习不模拟丢包。

### 输入输出示例

```text
cluster({"a": ["b", "c"], "b": ["d"]}, "a")
  -> (4, {"a": ["b", "c"], "b": ["d"], "c": [], "d": []})
cluster({"a": ["b", "c"], "b": ["d"]}, "a", duplicate=True)
  -> 同上
```

## 解题思路与参考答案

我会让根节点发起带 request id 的查询，沿树向下请求，再由叶子向上汇总。每个节点收到请求后转发给所有孩子，然后等待。等收齐所有孩子的回复，就把「自己 + 各子树」的节点数和拓扑汇总起来，回复给父节点。叶子没有孩子，收到请求就能立刻回复。

## 题目

一组机器组成一棵树，每台机器只能给父节点和子节点发消息。实现 `receiveMessage`，让根节点最终知道整棵树有多少台机器，以及完整的拓扑结构。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

消息是异步的，可能重复投递，所以要做去重：

- 同一个节点对同一个 request id 只初始化一次，重复的请求不再向下转发。
- 每个孩子的回复按（request id，child id）只记一次，重复回复直接忽略。
- 算完的结果缓存下来。父节点重试时，直接把缓存的结果再发一次，不重新计算。

如果消息可能丢失，就要加超时重试。要注意，超时只说明结果未知，不能把失联的子树当成 0 台机器。动手前和面试官确认：超时后是返回部分结果并标明缺失，还是一直等到全部到齐。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `cluster(children, root, duplicate=False)`：`children` 把每个节点映射到它的孩子列表，叶子可以不出现在 key 里。函数模拟父子之间的异步请求和回复，返回 `(节点数, {节点: 孩子列表})`。
- `duplicate=True` 时每条消息都投递两次，结果必须和不重复时一致。
- 每次查询的 request id 唯一。这份练习不模拟消息丢失，只讨论重试协议。
- 输入不是一棵以 `root` 为根的树时抛 `ValueError`：有重复的子边、某个节点有多个父亲、有环，或者有和 `root` 不连通的节点。节点数不超过 1000。

### 输入输出示例

```text
cluster({"a": ["b", "c"], "b": ["d"]}, "a")
  -> (4, {"a": ["b", "c"], "b": ["d"], "c": [], "d": []})
cluster({"a": ["b", "c"], "b": ["d"]}, "a", duplicate=True)
  -> 同上
```

### 解题思路与正确性

每个节点对每个 request id 只初始化一次状态，每个孩子的回复用 `setdefault` 只记一次，所以重复的消息不会让计数变多。节点只有在收齐所有孩子的回复后才汇总，汇总结果就是这棵子树的准确节点数和拓扑；由下往上归纳，根节点得到的就是整棵树。

重复的请求如果到达时结果已经算好，就把缓存的结果再发给父节点；父节点那边已经记过这个孩子的回复，会直接忽略。这样父节点的重试总能拿到同样的结果，根节点也不会因为重复包而重算。

### 完整参考实现（Python 3）

```python
from collections import deque


def build_tree(children, root):
    """把 children 映射补全成 {节点: 孩子列表}，并检查它是以 root 为根的一棵树。返回 (tree, parent)。"""
    nodes = {root} | set(children)
    for kids in children.values():
        nodes |= set(kids)
    tree = {node: list(children.get(node, [])) for node in nodes}

    parent = {}
    for node, kids in tree.items():
        if len(kids) != len(set(kids)):
            raise ValueError(f"duplicate child edge under {node!r}")
        for kid in kids:
            if kid in parent:
                raise ValueError(f"{kid!r} has multiple parents")
            parent[kid] = node

    # 每个节点至多一个父亲，所以从 root 出发再次碰到已访问节点只能是环
    seen = set()
    stack = [root]
    while stack:
        node = stack.pop()
        if node in seen:
            raise ValueError(f"cycle through {node!r}")
        seen.add(node)
        stack.extend(tree[node])
    if seen != nodes or root in parent:
        raise ValueError("children do not form a tree rooted at root")
    return tree, parent


def cluster(children, root, duplicate=False):
    """模拟父子节点之间的异步请求和回复，返回 (节点数, {节点: 孩子列表})。

    duplicate=True 时每条消息都投递两次，用来检查去重逻辑。
    """
    tree, parent = build_tree(children, root)

    # 消息格式：(kind, src, dst, qid, payload)
    messages = deque([("request", None, root, 1, None)])
    state = {}  # (节点, qid) -> {"received": {孩子: 回复}, "reply": 本节点的汇总或 None}
    result = None

    def send(message):
        messages.append(message)
        if duplicate:
            messages.append(message)

    while messages:
        kind, src, dst, qid, payload = messages.popleft()
        key = (dst, qid)
        if kind == "request":
            if key in state:
                # 重复请求：已经算完就把缓存的结果再发一次，没算完就忽略
                cached = state[key]["reply"]
                if cached is not None and src is not None:
                    send(("reply", dst, src, qid, cached))
                continue
            state[key] = {"received": {}, "reply": None}
            for kid in tree[dst]:
                send(("request", dst, kid, qid, None))
        else:
            if src not in tree[dst]:
                raise ValueError(f"unexpected reply from {src!r} to {dst!r}")
            state[key]["received"].setdefault(src, payload)  # 同一个孩子只记一次

        node_state = state[key]
        if node_state["reply"] is None and len(node_state["received"]) == len(
            tree[dst]
        ):
            # 收齐所有孩子（叶子在收到请求时就满足）后汇总，再交给父节点
            count = 1
            topology = {dst: list(tree[dst])}
            for kid in tree[dst]:
                kid_count, kid_topology = node_state["received"][kid]
                count += kid_count
                topology.update(kid_topology)
            node_state["reply"] = (count, topology)
            if dst == root:
                result = node_state["reply"]
            else:
                send(("reply", dst, parent[dst], qid, node_state["reply"]))
    return result
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert count == 4` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


tree = {"a": ["b", "c"], "b": ["d"]}
count, topology = cluster(tree, "a")
assert count == 4
assert topology == {"a": ["b", "c"], "b": ["d"], "c": [], "d": []}

# 每条消息投递两次，结果不变
assert cluster(tree, "a", True) == (count, topology)

# 只有根节点
assert cluster({}, "a") == (1, {"a": []})

# 不是树的输入
expect_value_error(cluster, {"a": ["b"], "b": ["a"]}, "a")  # 环
expect_value_error(cluster, {"a": ["b", "b"]}, "a")  # 重复边
expect_value_error(cluster, {"a": ["c"], "b": ["c"]}, "a")  # 多个父亲
expect_value_error(cluster, {"a": ["b"], "x": ["y"]}, "a")  # 不连通
```

### 复杂度与追问

设节点数为 N。请求和回复各 O(N) 条消息（重复投递只多一个常数倍）。只统计节点数时，载荷是 O(1)，总量 O(N)；要传完整拓扑时，每一层都把整棵子树的结构往上带，链状树的载荷总量是 $O(N^2)$。

如果追问怎么减少拓扑的传输量：每个节点只上报自己的孩子列表，由根节点按节点 ID 拼起来；或者让每个节点直接把自己那条边写到一个公共存储。

如果追问某个节点永久失联：这时拿不到全部结果，根节点超时后只能返回「未知」或者带缺失标记的部分结果，不能默认失联的子树是 0。
