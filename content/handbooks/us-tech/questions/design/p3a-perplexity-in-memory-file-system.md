---
id: p3a-perplexity-in-memory-file-system
section: design
order: 600
level: A
title: "Perplexity：树形文件系统：路径与文件/目录操作"
quick: "目录存子节点映射、文件存内容，先写好公共的路径规范化，区分空目录删除和递归删除，后续阶段都复用同一棵树。"
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Perplexity · in-memory-file-system"
    url: https://www.1point3acres.com/interview/problems/company/perplexity/in-memory-file-system
    type: secondary
---

## 题目

分阶段实现一个内存文件系统：先创建目录和列出内容，再支持读写文件，最后支持删除，包括删除非空目录。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

目录节点用「名字到子节点」的映射，文件节点存内容。第一步先把路径解析和规范化写成一个公共函数，所有接口都走它，后面加功能时就不会出现某个接口对 `..` 的处理和别的不一样。

删除要区分两种情况：空目录和文件可以直接删，非空目录需要显式要求递归删除。文件名冲突（比如在已有文件的位置 `mkdir`）以及各种错误分别抛什么异常，也要先定义清楚。

后续阶段都复用同一棵树。如果每个阶段各写一套遍历，早期接口的语义很容易在改动中悄悄变掉。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `FS()`：内存里的 Unix 风格文件系统，所有路径都必须是绝对路径，否则抛 `ValueError`。路径先规范化：忽略空段和 `.`，`..` 回到上一级，根目录的上一级仍是根。
- `mkdir(path, parents=False)`：创建目录。目录已存在时什么也不做；缺上级目录且 `parents=False` 时抛 `FileNotFoundError`；同名文件已存在时抛 `FileExistsError`。
- `write(path, text, append=False)`：写文件，不存在就创建，`append=True` 时接在原内容后面。上级目录必须存在；目标是目录时抛 `IsADirectoryError`。
- `read(path) -> str`：读文件内容；目标是目录时抛 `IsADirectoryError`。
- `ls(path) -> list[str]`：目标是文件时返回 `[文件名]`，是目录时返回按名字排序的子节点。
- `remove(path, recursive=False)`：删除文件或目录。非空目录必须 `recursive=True`，否则抛 `ValueError`；根目录不能删。
- 路径中途把文件当目录用时抛 `NotADirectoryError`，名字不存在时抛 `FileNotFoundError`。不支持符号链接和权限，节点数不超过 $10^4$。

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

- 追问「加上移动和重命名」：先找到源节点的父目录和目标的父目录，检查目标不是源的子孙（否则会把目录移进自己里面），再把节点从一个 `children` 摘下、挂到另一个上。
- 追问「多线程同时操作」：最简单的是整个文件系统一把锁。要提高并发，可以每个目录一把锁，按从根到叶的顺序加锁以免死锁。
