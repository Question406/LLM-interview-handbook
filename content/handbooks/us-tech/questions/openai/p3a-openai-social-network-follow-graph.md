---
id: p3a-openai-social-network-follow-graph
section: openai
order: 602
level: A
title: "OpenAI：带时间版本的关注图与好友推荐"
quick: "只存当前邻接集合只能回答「现在」的查询；要按时间查询历史，就得保存事件日志或每条边的有效时间区间，再在对应时刻的图上枚举二跳邻居做推荐。"
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
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · social-network-follow-graph"
    url: https://www.1point3acres.com/interview/problems/company/openai/social-network-follow-graph
    type: secondary
---

## 题目

实现一个社交网络的关注图，支持关注、取消关注、查询某个时刻某人关注了谁，以及基于二度关系（朋友的朋友）的好友推荐。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；网站收录为面经题型不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

如果只需要回答当前状态，每个用户存一个关注集合就够了。但题目要求按时间查询，比如「t = 3 时 a 关注了谁」，而之后的取关不能影响这个答案，所以必须保留历史。两种常见做法：

- 存完整的事件日志，查询时把时间 $\le t$ 的事件按顺序重放一遍；
- 给每条边记录有效区间 $[\text{start}, \text{end})$，查询时只看在 $t$ 时有效的边。

推荐的做法是：在 $t$ 时刻的图上，从用户出发走两步，统计每个候选人被多少个中间人连到，排除自己和已经关注的人，再按规定的规则排序。

动手前要和面试官确认：推荐基于哪个时刻的图；事件是否可能乱序到达，同一时间的多个事件谁先生效；重复关注和取关不存在的边怎么处理；推荐结果按什么排序、并列时怎么定。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `follow(time, follower, followee)`：在 `time` 时刻建立关注。重复关注是幂等的，自己关注自己抛 `ValueError`。
- `unfollow(time, follower, followee)`：在 `time` 时刻取消关注，取关不存在的边直接忽略。
- `following(time, user) -> list`：返回 `time` 时刻 `user` 关注的人，按名字排序。
- `recommend(time, user, k) -> list`：返回 `time` 时刻二跳可达、且 `user` 尚未关注的人，按共同中间人数降序、用户名升序，取前 `k` 个。
- 事件可以乱序调用；查询只重放时间 $\le t$ 的事件，时间相同时按调用先后生效。规模不超过 1000 个事件、100 个用户。

### 输入输出示例

```text
按调用顺序：follow(3, d, c), follow(0, a, b), follow(1, b, c), follow(2, a, d)
recommend(3, a, 1)   -> [c]        # a 经 b 和 d 都能到 c
recommend(0, a, 1)   -> []         # t = 0 时 b 还没关注任何人
unfollow(4, a, b)
following(3, a)      -> [b, d]
following(4, a)      -> [d]
```

### 解题思路与正确性

每个事件记成 `(时间, 调用序号, 是否关注, 关注者, 被关注者)`。查询时按 (时间, 调用序号) 排序重放，直到时间超过 $t$，用每个用户的集合维护当前存在的边。这样得到的就是 $t$ 时刻的准确快照，之后发生的事件不会参与，乱序写入也不影响结果。

推荐时对每个直接关注的中间人，把他关注的人各计一次，最后的计数就是共同中间人数。自己和已关注的人在计数前排除，排序键是 `(-计数, 用户名)`，并列时的顺序完全确定。

### 完整参考实现（Python 3）

```python
from collections import Counter, defaultdict


class Graph:
    """带时间戳的关注图。事件可以乱序到达，查询时只重放时间 <= t 的事件。"""

    def __init__(self):
        self.events = []  # (时间, 调用序号, 是否关注, 关注者, 被关注者)

    def follow(self, time, follower, followee):
        if follower == followee:
            raise ValueError(f"{follower!r} cannot follow themselves")
        self.events.append((time, len(self.events), True, follower, followee))

    def unfollow(self, time, follower, followee):
        self.events.append((time, len(self.events), False, follower, followee))

    def _snapshot(self, time):
        """重放到 time 为止的事件，返回 用户 -> 关注集合。同一时间按调用顺序生效。"""
        graph = defaultdict(set)
        for event_time, _, is_follow, follower, followee in sorted(self.events):
            if event_time > time:
                break
            if is_follow:
                graph[follower].add(followee)  # 重复关注是幂等的
            else:
                graph[follower].discard(followee)  # 取关不存在的边直接忽略
        return graph

    def following(self, time, user):
        return sorted(self._snapshot(time)[user])

    def recommend(self, time, user, k):
        """推荐二跳可达、尚未关注的人：按共同中间人数降序，再按用户名升序，取前 k 个。"""
        graph = self._snapshot(time)
        direct = graph[user]
        counts = Counter(
            candidate
            for middle in direct
            for candidate in graph[middle]
            if candidate != user and candidate not in direct
        )
        ranked = sorted(counts, key=lambda candidate: (-counts[candidate], candidate))
        return ranked[:k]
```

### 可执行测试

```python
# 事件乱序写入：d->c 的时间最晚，却最先调用
graph = Graph()
graph.follow(3, "d", "c")
graph.follow(0, "a", "b")
graph.follow(1, "b", "c")
graph.follow(2, "a", "d")

# t = 3 时 a 经 b、d 两条路都能到 c；t = 0 时 b 还没关注任何人
assert graph.recommend(3, "a", 1) == ["c"]
assert graph.recommend(0, "a", 1) == []

# 取关只影响之后的快照
graph.unfollow(4, "a", "b")
assert graph.following(3, "a") == ["b", "d"]
assert graph.following(4, "a") == ["d"]

# 共同中间人数相同时按用户名排序；已关注的人和自己不推荐
graph = Graph()
graph.follow(0, "a", "b")
graph.follow(0, "b", "z")
graph.follow(0, "b", "y")
graph.follow(0, "b", "a")
assert graph.recommend(0, "a", 5) == ["y", "z"]

try:
    graph.follow(0, "a", "a")
except ValueError:
    pass
else:
    raise AssertionError("self follow should raise ValueError")
```

### 复杂度与追问

设事件数为 $E$。每次查询都要排序并重放，耗时 $O(E \log E)$；推荐还要遍历二跳边，再对 $C$ 个候选排序，额外 $O(\text{二跳边数} + C \log C)$。

- 查询很频繁怎么办？写入时就保持事件有序（或者定期排序一次），避免每次查询都排序。更进一步，给每条边存有效区间，或者每隔一段时间存一个快照，查询时从最近的快照开始重放。
- 用户量很大时推荐怎么做？二跳枚举的代价是「关注数 × 平均关注数」，大 V 会让它爆炸。可以对中间人采样、限制每个中间人贡献的候选数，或者离线预计算推荐列表。
