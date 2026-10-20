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
        if node_state["reply"] is None and len(node_state["received"]) == len(tree[dst]):
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


def test():
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
    expect_value_error(cluster, {"a": ["b"], "b": ["a"]}, "a")      # 环
    expect_value_error(cluster, {"a": ["b", "b"]}, "a")             # 重复边
    expect_value_error(cluster, {"a": ["c"], "b": ["c"]}, "a")      # 多个父亲
    expect_value_error(cluster, {"a": ["b"], "x": ["y"]}, "a")      # 不连通


if __name__ == "__main__":
    test()
