---
id: p3a-anthropic-coding-q2-file-deduplication
section: anthropic
order: 600
level: A
title: "Anthropic：文件去重：分层筛选、I/O 与分布式扩展"
quick: "分层筛选：先按文件大小分组，只对大小相同的文件流式计算内容哈希，哈希相同的再逐字节确认，这样只读必要的文件，也不会因哈希碰撞误判。"
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
  - title: "1Point3Acres · Anthropic · coding-q2-file-deduplication"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/coding-q2-file-deduplication
    type: secondary
---

## 题目

遍历一个目录树，找出所有内容完全相同的文件，按组返回。写完之后面试官会追问哈希怎么选、I/O 怎么省、文件量很大时怎么扩展到多机。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站收录了这类面经，不代表公司确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

核心是分层筛选，越往后越贵，只对前一层留下的候选做：

1. 按文件大小分组。大小不同一定不重复，这一步只读元数据；
2. 同一大小组里有两个以上文件时，才流式计算内容哈希（如 SHA-256）；
3. 哈希相同只说明「很可能相同」，需要严格正确时再逐字节确认，彻底排除碰撞。

还可以在第 2 步之前加一层「只哈希前几 KB」，很多大小相同、开头就不同的文件在这里就被分开了。

性能上要分清瓶颈：小文件多时，开销主要在打开文件和读元数据；大文件多时，瓶颈是磁盘读带宽。所以并行度不能无限加，超过磁盘能承受的并发后只会更慢。

动手前要和面试官确认这些边界：

- 符号链接跟不跟随（这份练习不跟随，避免目录环和同一文件被数两次）；
- 硬链接指向同一个 inode，算不算重复（这份练习会把它们报成重复；要排除可以按 `(st_dev, st_ino)` 去重）；
- 读到一半文件被修改、没有读权限时怎么处理（这份练习假设执行期间文件不变，错误直接抛给调用者）；
- 空文件算不算互相重复（这份练习算）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `duplicates(root) -> list[list[str]]`：返回内容相同的普通文件路径组。每组至少两个路径，组内排序，组与组之间也排序。
- 递归遍历子目录，不跟随符号链接（指向文件或目录的都跳过）。
- 先按大小分组，再流式计算 SHA-256，最后逐字节确认，哈希碰撞也不会误判。
- 空文件可以互相重复。权限错误和读取错误直接向调用者抛出；假设执行期间文件不被修改。
- 最多 $10^4$ 个文件，每次读 64 KiB。

### 输入输出示例

```text
目录内容：a = "abc", b = "abc", c = "xyz", d = "", e = ""
duplicates(root)   -> [[".../a", ".../b"], [".../d", ".../e"]]
```

c 和 a、b 大小相同，但哈希不同，所以不会并组。

### 解题思路与正确性

大小不同的文件内容一定不同，所以按大小分组不会漏掉重复。同一组内再按哈希细分，哈希不同的内容也一定不同。哈希相同的候选最后逐字节比较；内容相等是等价关系（自反、对称、传递），所以每个文件只需和每个已有组的第一个文件比，就能得到正确分组，哈希碰撞的文件会落进不同的组。

遍历时通过 `subdirs[:] = ...` 原地剪掉指向目录的符号链接，`os.walk` 就不会进入它们，从而避免环和重复走访。

### 完整参考实现（Python 3）

```python
from collections import defaultdict
import hashlib
import os
from pathlib import Path

BLOCK_SIZE = 64 * 1024


def same_content(path_a, path_b):
    """逐块比较两个文件的字节，用来排除哈希碰撞。"""
    with open(path_a, "rb") as file_a, open(path_b, "rb") as file_b:
        while True:
            block_a = file_a.read(BLOCK_SIZE)
            block_b = file_b.read(BLOCK_SIZE)
            if block_a != block_b:
                return False
            if not block_a:
                return True


def sha256_of(path):
    """流式计算 SHA-256，不把整个文件读进内存。"""
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for block in iter(lambda: file.read(BLOCK_SIZE), b""):
            digest.update(block)
    return digest.digest()


def group_by_size(root):
    """递归收集普通文件，按字节数分组；不跟随符号链接（目录和文件都跳过）。"""
    by_size = defaultdict(list)
    for directory, subdirs, files in os.walk(root, followlinks=False):
        subdirs[:] = [name for name in subdirs if not (Path(directory) / name).is_symlink()]
        for name in files:
            path = Path(directory) / name
            if path.is_file() and not path.is_symlink():
                by_size[path.stat().st_size].append(str(path))
    return by_size


def split_by_bytes(candidates):
    """把哈希相同的候选按真实内容分组。内容相等是等价关系，所以只需和每组第一个比。"""
    groups = []
    for path in sorted(candidates):
        for group in groups:
            if same_content(path, group[0]):
                group.append(path)
                break
        else:
            groups.append([path])
    return groups


def duplicates(root):
    """返回内容相同的普通文件路径组：每组至少两个，组内和组间都排序。"""
    result = []
    for paths in group_by_size(root).values():
        if len(paths) < 2:
            continue  # 大小唯一的文件不可能有重复，不用读内容
        by_hash = defaultdict(list)
        for path in paths:
            by_hash[sha256_of(path)].append(path)
        for candidates in by_hash.values():
            result.extend(group for group in split_by_bytes(candidates) if len(group) > 1)
    return sorted(result)
```

### 可执行测试

```python
import tempfile

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    contents = [("a", b"abc"), ("b", b"abc"), ("c", b"xyz"), ("d", b""), ("e", b"")]
    for name, data in contents:
        (root / name).write_bytes(data)

    # 同大小不同内容的 c 不应和 a/b 并组；两个空文件互为重复
    groups = duplicates(directory)
    names = sorted(sorted(Path(path).name for path in group) for group in groups)
    assert names == [["a", "b"], ["d", "e"]]

    # 符号链接不算一份文件
    (root / "link").symlink_to(root / "a")
    assert duplicates(directory) == groups

    # 子目录里的文件也会被找到；指向目录的符号链接不跟随
    (root / "sub").mkdir()
    (root / "sub" / "f").write_bytes(b"xyz")
    (root / "sub_link").symlink_to(root / "sub")
    names = sorted(sorted(Path(path).name for path in group) for group in duplicates(directory))
    assert names == [["a", "b"], ["c", "f"], ["d", "e"]]

# 逐块比较：差异落在第二块里也能发现
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root / "x").write_bytes(b"1" * (BLOCK_SIZE + 1))
    (root / "y").write_bytes(b"1" * BLOCK_SIZE + b"2")
    assert not same_content(root / "x", root / "y")
    assert same_content(root / "x", root / "x")
```

### 复杂度与追问

设文件数为 F。通常时间是 O(候选文件的总字节数 + F log F)：只有大小撞上的文件才会被读，排序是 F log F。如果有人故意构造大量哈希碰撞，逐字节比较最坏是 O(F² × 文件长度)。内存是 O(F) 的路径和哈希，加上一个读缓冲块。

- 执行时文件可能被修改：读之前和读之后各取一次 `mtime` 和大小，不一致就重试；更强的保证需要文件锁或文件系统快照。
- 扩展到多机：先由各节点按大小上报元数据，按大小（或大小加前缀哈希）分片给不同 worker，保证可能重复的文件落在同一个 worker 上；各 worker 本地做哈希和确认，最后汇总结果。
- I/O 调度：按磁盘顺序或目录顺序读，减少随机寻道；每块磁盘设一个并发上限，避免在机械盘上加线程反而变慢。
