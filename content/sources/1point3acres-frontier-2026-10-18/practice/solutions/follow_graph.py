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


def test():
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


if __name__ == "__main__":
    test()
