from collections import deque

MAX_SYMLINK_EXPANSIONS = 40  # 和 Linux 的 MAXSYMLINKS 一样


def _expand_home(destination, home):
    if destination == "~" or destination.startswith("~/"):
        return home + destination[1:]
    return destination


def cd(cwd, destination, links, home="/home/u"):
    """返回在 cwd 执行 `cd destination` 后的规范绝对路径。

    links 把规范绝对路径映射到链接目标；相对目标以链接所在的目录为基准。
    """
    if not cwd.startswith("/"):
        raise ValueError(f"cwd must be absolute, got {cwd!r}")
    destination = _expand_home(destination, home)

    # resolved 始终是一条已经解析过的真实路径（不含链接），按组件存
    resolved = [] if destination.startswith("/") else [part for part in cwd.split("/") if part]
    pending = deque(destination.split("/"))
    expansions = 0
    while pending:
        part = pending.popleft()
        if part in ("", "."):
            continue
        if part == "..":
            if resolved:  # 根目录的 .. 仍是根目录
                resolved.pop()
            continue

        candidate = "/" + "/".join(resolved + [part])
        if candidate not in links:
            resolved.append(part)
            continue

        expansions += 1
        if expansions > MAX_SYMLINK_EXPANSIONS:
            raise ValueError("too many symlink expansions (loop?)")
        target = links[candidate]
        if target.startswith("/"):
            resolved = []
        # 目标的各段插回队首，先于 destination 剩余部分处理；
        # 相对目标不清空 resolved，正好以链接的父目录为基准
        pending.extendleft(reversed(target.split("/")))
    return "/" + "/".join(resolved)


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    links = {"/a/link": "../b"}

    # 相对链接目标以链接所在目录 /a 为基准
    assert cd("/a", "link/x", links) == "/b/x"

    # 先展开链接再处理 ..：/a/link/.. 是 /b/..，即 /
    assert cd("/a", "link/..", links) == "/"

    # 根目录的 ..、重复斜杠、. 和末尾斜杠
    assert cd("/", "../../x//./", {}) == "/x"

    # 家目录
    assert cd("/a", "~/x", {}) == "/home/u/x"
    assert cd("/a", "~", {}, "/root") == "/root"

    # 绝对链接目标
    assert cd("/", "a/c", {"/a": "/opt/real"}) == "/opt/real/c"

    # 链接环
    expect_value_error(cd, "/", "a", {"/a": "b", "/b": "a"})

    # cwd 不是绝对路径
    expect_value_error(cd, "a", "b", {})


if __name__ == "__main__":
    test()
