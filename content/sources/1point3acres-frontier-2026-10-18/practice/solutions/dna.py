from collections import Counter, defaultdict


def build_adjacency(edges):
    adjacency = defaultdict(list)  # 标签 -> 还没用过的出边终点；平行边重复出现
    for start_tag, end_tag in edges:
        adjacency[start_tag].append(end_tag)
    return adjacency


def euler_chain(edges):
    """返回恰好用每条有向边一次的标签序列；不存在这样的单链时返回 None。"""
    if not edges:
        return []
    adjacency = build_adjacency(edges)
    out_degree = Counter(start_tag for start_tag, _ in edges)
    in_degree = Counter(end_tag for _, end_tag in edges)
    nodes = set(out_degree) | set(in_degree)

    # 度数条件：其余点出入度相等，最多一个起点「出度多 1」、一个终点「入度多 1」
    if any(abs(out_degree[node] - in_degree[node]) > 1 for node in nodes):
        return None
    starts = [node for node in nodes if out_degree[node] - in_degree[node] == 1]
    ends = [node for node in nodes if in_degree[node] - out_degree[node] == 1]
    if (len(starts), len(ends)) not in ((0, 0), (1, 1)):
        return None
    start = starts[0] if starts else min(node for node in nodes if out_degree[node])

    # Hierholzer：沿未用的边一直走，走不动的点出栈加入路线，最后反转
    stack = [start]
    route = []
    while stack:
        node = stack[-1]
        if adjacency[node]:
            stack.append(adjacency[node].pop())
        else:
            route.append(stack.pop())
    route.reverse()

    # 度数条件不检查连通性：如果有边在别的连通分量里，路线会比边数 + 1 短
    if len(route) != len(edges) + 1:
        return None
    return route


def chains(edges):
    """把边集拆成若干条有向链（trail），每条边恰好用一次；不保证链数最少。"""
    adjacency = build_adjacency(edges)
    result = []
    for start in sorted(adjacency):
        while adjacency[start]:
            path = [start]
            node = start
            while adjacency[node]:
                node = adjacency[node].pop()
                path.append(node)
            result.append(path)
    return result


def test():
    def used_edges(paths):
        return Counter(pair for path in paths for pair in zip(path, path[1:]))

    # 单链：a -> b -> a -> c，每条边恰好用一次
    edges = [("a", "b"), ("b", "a"), ("a", "c")]
    route = euler_chain(edges)
    assert Counter(zip(route, route[1:])) == Counter(edges)
    assert route[0] == "a"
    assert route[-1] == "c"

    # 空输入返回空序列
    assert euler_chain([]) == []

    # 两个不连通的片段：度数条件不满足，无单链
    assert euler_chain([("a", "b"), ("c", "d")]) is None

    # 度数平衡但不连通：靠长度检查发现
    assert euler_chain([("a", "b"), ("b", "a"), ("c", "d"), ("d", "c")]) is None

    # 多链：每条边恰好用一次，包括平行边
    for case in ([], [("a", "b"), ("a", "b"), ("b", "a")], [("a", "b"), ("c", "d")]):
        assert used_edges(chains(case)) == Counter(case)


if __name__ == "__main__":
    test()
