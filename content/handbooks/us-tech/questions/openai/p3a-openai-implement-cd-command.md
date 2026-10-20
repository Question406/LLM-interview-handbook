---
id: p3a-openai-implement-cd-command
section: openai
order: 623
level: A
title: "OpenAI：实现 cd：路径规范化、符号链接与环检测"
quick: "普通路径规范化用栈处理 . 和 ..；遇到符号链接要逐段展开，把目标插回待处理队列，相对目标以链接所在目录为基准，并限制展开次数来检测环。"
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
  - title: "1Point3Acres · OpenAI · implement-cd-command"
    url: https://www.1point3acres.com/interview/problems/company/openai/implement-cd-command
    type: secondary
---

## 题目

实现 shell 的 `cd`：给当前目录和目标路径，返回切换后的规范绝对路径。题目分几步加功能：相对路径和绝对路径、`.` 与 `..`、家目录 `~`，最后是符号链接以及链接成环的检测。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

没有符号链接时，这就是路径规范化：按 `/` 切开，用栈维护当前路径，遇到空段和 `.` 跳过，遇到 `..` 弹栈（在根目录时保持不动），其他段压栈。

加上符号链接后，不能先在字符串上把 `..` 消掉再解析链接。例如 `/a/link` 指向 `../b`，那么 `/a/link/..` 实际是 `/b/..`，也就是 `/`；如果先按字面消掉 `link/..`，会错误地得到 `/a`。正确做法是逐段处理：每拼出一个新路径，就检查它是不是链接；是的话把链接目标的各段插回待处理队列的最前面，接着解析。

- 绝对目标：清空已解析的路径，从根开始。
- 相对目标：以链接所在的目录为基准，也就是保持当前已解析的路径不变。

链接可能互相指向形成环，所以要给展开次数设上限（Linux 用 40），超过就报错。

面试中还可以顺带解释：`cd` 改变的是 shell 进程自己的工作目录，子进程改不了父进程的目录，所以 `cd` 通常是 shell 内建命令。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `cd(cwd, destination, links, home="/home/u") -> str`：`cwd` 必须是绝对路径，否则抛 `ValueError`。`destination` 支持绝对和相对路径、`.`、`..`、连续斜杠，以及开头的 `~`（展开成 `home`）。
- `links` 把规范的绝对链接路径映射到目标，目标可以是绝对路径，也可以是相对于链接父目录的相对路径。
- 根目录的 `..` 仍是根目录。链接展开总次数超过 40 次抛 `ValueError`。
- 路径总长不超过 $10^4$。只模拟路径解析，不检查目录是否真的存在。

### 输入输出示例

```text
cd("/a", "link/x", {"/a/link": "../b"})  -> "/b/x"
cd("/a", "link/..", {"/a/link": "../b"}) -> "/"
cd("/", "../../x//./", {})              -> "/x"
cd("/a", "~/x", {})                     -> "/home/u/x"
```

### 解题思路与正确性

`resolved` 始终是一条不含链接的真实路径。每处理一段，要么它不是链接，直接追加；要么它是链接，把目标的各段放回队首，等价于把路径里的这一段替换成链接目标。因为替换发生在后续的 `..` 被处理之前，`..` 退回的是链接目标的父目录，和真实文件系统的行为一致。

展开次数有上限，所以即使链接成环，循环也一定会结束。

### 完整参考实现（Python 3）

```python
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
```

### 可执行测试

```python
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
```

### 复杂度与追问

设路径总长为 L。不涉及链接时，每段处理一次，但每段都要用 `join` 拼出候选路径去查表，最坏 O($L^2$)；可以改成边走边维护当前路径字符串来降到线性。链接展开最多 40 次，每次插入的段数受目标长度限制。

真实文件系统还要处理权限不足、路径中间某段不存在，以及检查和使用之间文件被改动（TOCTOU）等问题，这个虚拟练习都没有覆盖。
