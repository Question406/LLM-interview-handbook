---
id: p3a-anthropic-oa-file-systems
section: anthropic
order: 614
level: A
title: "Anthropic：文件系统 OA：路径操作与未公开扩展"
quick: "我会用目录树表示文件系统，让所有接口共用路径规范化和遍历规则。先确定文件与目录冲突、根目录、重复创建的行为，再实现操作；题卡没有给出 LLM 末级细节，这部分不补写。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · oa-file-systems"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/oa-file-systems
    type: secondary
---

## 题目描述

实现一个简化的内存文件系统，支持目录、文本文件和路径规范化。

以下接口和边界行为是本手册重构练习的约定。假定输入满足所述合法范围。

`FS()` 初始仅有根目录 `/`。路径均为绝对 Unix 路径；忽略重复 `/` 与 `.`，`..` 返回父目录，在根目录继续向上仍为根。无符号链接和权限机制，节点总数不超过 10000。

实现 `mkdir(path, parents=False)`：创建目录，已有目录时无操作；parents=True 时可创建缺失祖先。`write(path, text, append=False)` 创建或覆盖文本文件，append=True 时在原内容末尾追加；`read(path)` 返回完整字符串。`ls(path)` 对文件返回仅含其 basename 的列表，对目录返回按名称排序的直接子节点列表。`remove(path, recursive=False)` 删除文件或目录；非空目录只有 recursive=True 才允许删除，根目录不被删除。假定其他操作的父目录存在、目标类型匹配，不要求补充异常输入处理。

### 示例

```text
mkdir("/a"); write("/a/f", "hi"); write("/a/f", "!", append=True)
read("/a/f") = "hi!"；ls("/a") = ["f"]
mkdir("/b/c", parents=True); write("/b/c/../x", "z")
read("/b/x") = "z"
remove("/a", recursive=True); ls("/") = ["b"]
```

## 解题思路与参考答案

## 题目

CodeSignal 风格的 OA，逐级实现一个简化的文件系统：先是创建目录、读写文件、列目录和删除，后面的级别会在同一棵目录树上继续加功能。题卡提到最后一级有和 LLM 相关的扩展，但没给出细节。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。最后一级的 LLM 扩展细节不足，下面不重构它；接口、约束和测试是手册补的练习约定，不是原题。

## 思路

我会用一棵目录树管理路径，目录节点存子节点，文件节点存内容。所有操作共享路径规则，边界行为先约定清楚，才不会出现同一路径在不同接口里含义不同：

- 文件和目录同名冲突时报什么错；
- 根目录能不能删、能不能当文件写；
- 重复创建同一个目录是报错还是什么也不做；
- `.` 和 `..` 怎么处理，`..` 越过根目录时怎么办。

OA 一般会给 helper 函数和题面契约，现场先读清楚它们，再为路径规范化写几个边界例子跑一下。后续级别的题面没有读到，不要先猜着实现。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `FS()`：内存里的 Unix 风格文件系统，所有路径都必须是绝对路径，否则抛 `ValueError`。路径先规范化：忽略空段和 `.`，`..` 回到上一级，根目录的上一级仍是根。
- `mkdir(path, parents=False)`：创建目录。目录已存在时什么也不做；缺上级目录且 `parents=False` 时抛 `FileNotFoundError`；同名文件已存在时抛 `FileExistsError`。
- `write(path, text, append=False)`：写文件，不存在就创建，`append=True` 时接在原内容后面。上级目录必须存在；目标是目录时抛 `IsADirectoryError`。
- `read(path) -> str`：读文件内容；目标是目录时抛 `IsADirectoryError`。
- `ls(path) -> list[str]`：目标是文件时返回 `[文件名]`，是目录时返回按名字排序的子节点。
- `remove(path, recursive=False)`：删除文件或目录。非空目录必须 `recursive=True`，否则抛 `ValueError`；根目录不能删。
- 路径中途把文件当目录用时抛 `NotADirectoryError`，名字不存在时抛 `FileNotFoundError`。不支持符号链接和权限，节点数不超过 $10^4$。
- 题卡里没有披露细节的 LLM 末级不在练习范围内。

### 输入输出示例

```text
mkdir("/a")
write("/a/f", "hi")
write("/a/f", "!", append=True)
read("/a/./f")       -> "hi!"
ls("/a")             -> ["f"]
remove("/a")         -> ValueError（目录非空）
mkdir("/b/c", parents=True)
write("/b/c/../x", "z")
read("/b/x")         -> "z"
```

### 解题思路与正确性

整个文件系统是一棵树，节点的 `text` 为 `None` 表示目录，否则是文件。用 `None` 而不是空字符串做标记，空文件 `""` 才不会被误判成空目录。

所有接口都先经过同一个 `_parts` 做路径规范化，再用同一个 `_walk` 往下走。`_walk` 每走一步都检查当前节点是不是文件，所以任何接口都没法「穿过」一个文件继续往下找。`mkdir` 和 `write` 需要在缺失时创建节点，才各自写了遍历，但用的是同样的检查。

删除时只把目标节点从父目录的 `children` 里摘掉，整棵子树随之不可达，其他路径不受影响。

### 完整参考实现（Python 3）

```python
class Node:
    """文件或目录节点。text 为 None 表示目录；文件的 text 是字符串（空文件是 ""）。"""

    def __init__(self, text=None):
        self.text = text
        self.children = {}  # 只有目录使用：名字 -> Node

    @property
    def is_file(self):
        return self.text is not None


class FS:
    """内存里的 Unix 风格文件系统，只接受绝对路径，不支持链接和权限。"""

    def __init__(self):
        self.root = Node()

    def _parts(self, path):
        """把绝对路径规范化成名字列表：去掉空段和 "."，".." 回到上一级，根的上一级还是根。"""
        if not path.startswith("/"):
            raise ValueError(f"path must be absolute: {path!r}")
        parts = []
        for name in path.split("/"):
            if name in ("", "."):
                continue
            if name == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(name)
        return parts

    def _walk(self, parts):
        """沿 parts 走到目标节点；中途遇到文件或缺失的名字就报错。"""
        node = self.root
        for name in parts:
            if node.is_file:
                raise NotADirectoryError(name)
            if name not in node.children:
                raise FileNotFoundError(name)
            node = node.children[name]
        return node

    def mkdir(self, path, parents=False):
        """创建目录；目录已存在时什么也不做。parents=True 时顺带创建缺失的上级目录。"""
        parts = self._parts(path)
        node = self.root
        for depth, name in enumerate(parts):
            if node.is_file:
                raise NotADirectoryError(name)
            if name not in node.children:
                is_last = depth == len(parts) - 1
                if not is_last and not parents:
                    raise FileNotFoundError(name)
                node.children[name] = Node()
            node = node.children[name]
        if node.is_file:
            raise FileExistsError(path)

    def write(self, path, text, append=False):
        """写文件；文件不存在就创建。append=True 时接在原内容后面。上级目录必须已存在。"""
        parts = self._parts(path)
        if not parts:
            raise IsADirectoryError(path)
        parent = self._walk(parts[:-1])
        if parent.is_file:
            raise NotADirectoryError(path)
        name = parts[-1]
        old = parent.children.get(name)
        if old is not None and not old.is_file:
            raise IsADirectoryError(path)
        prefix = old.text if append and old is not None else ""
        parent.children[name] = Node(prefix + text)

    def read(self, path):
        node = self._walk(self._parts(path))
        if not node.is_file:
            raise IsADirectoryError(path)
        return node.text

    def ls(self, path):
        """文件返回 [自身名字]，目录返回排好序的子节点名字。"""
        parts = self._parts(path)
        node = self._walk(parts)
        if node.is_file:
            return [parts[-1]]
        return sorted(node.children)

    def remove(self, path, recursive=False):
        """删除文件或目录。非空目录必须 recursive=True；根目录不能删。"""
        parts = self._parts(path)
        if not parts:
            raise ValueError("cannot remove root")
        parent = self._walk(parts[:-1])
        node = self._walk(parts)
        if not node.is_file and node.children and not recursive:
            raise ValueError(f"directory not empty: {path}")
        # 从父目录断开整棵子树即可，子节点随之不可达
        del parent.children[parts[-1]]
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert fs.read("/a/./f") == "hi!"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_error(error, fn, *args):
    try:
        fn(*args)
    except error:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise {error.__name__}")

# 写入、追加、带 "." 的路径
fs = FS()
fs.mkdir("/a")
fs.write("/a/f", "hi")
fs.write("/a/f", "!", True)
assert fs.read("/a/./f") == "hi!"
assert fs.ls("/a") == ["f"]
assert fs.ls("/a/f") == ["f"]

# 非空目录必须递归删除
expect_error(ValueError, fs.remove, "/a")

fs.mkdir("/b/c", True)
fs.remove("/a", True)
assert fs.ls("/") == ["b"]

# ".." 回到上一级
fs.write("/b/c/../x", "z")
assert fs.read("/b/x") == "z"

# 重复 mkdir 是幂等的；空文件仍然是文件
fs.mkdir("/b/c")
fs.write("/b/empty", "")
assert fs.read("/b/empty") == ""
assert fs.ls("/b") == ["c", "empty", "x"]

expect_error(FileNotFoundError, fs.mkdir, "/p/q")      # 缺上级且没给 parents
expect_error(FileExistsError, fs.mkdir, "/b/x")        # 同名文件已存在
expect_error(NotADirectoryError, fs.read, "/b/x/y")    # 把文件当目录
expect_error(IsADirectoryError, fs.write, "/b/c", "t")  # 往目录里写内容
expect_error(ValueError, fs.remove, "/")               # 根目录不能删
expect_error(ValueError, fs.ls, "b")                   # 只接受绝对路径
```

### 复杂度与追问

设路径段数为 L，目录的子节点数为 k，被删子树的节点数为 s。路径解析和查找是 O(L)，`ls` 排序是 O(k log k)，递归删除只需 O(L) 把子树从父目录断开，之后由 Python 回收这 s 个节点。空间是 O(节点数 + 文件内容总长)。

- 追问「支持符号链接怎么办」：不能先整体规范化再查找，因为 `..` 要相对链接展开后的真实位置计算。要逐段解析，遇到链接就把它的目标拼进剩余路径，再继续处理 `..`，并限制展开次数防止链接成环。
- 追问「文件很多、`ls` 很频繁」：每个目录维护有序的子节点集合，插入时保持有序，`ls` 就不用每次排序。
