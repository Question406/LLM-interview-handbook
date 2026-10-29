---
id: p3a-openai-durable-kv-store-serialization
section: openai
order: 616
level: A
title: OpenAI：持久 KV：任意字节编码与 1KB 分文件
quick: >-
  字段先编码成 bytes，再写字节长度和内容，任意分隔符都不会冲突。超过单文件上限就分片，先写完并校验分片，最后原子发布
  manifest；这份实现是快照，每次写都持久还需要 WAL。
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 1Point3Acres · OpenAI · durable-kv-store-serialization
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/durable-kv-store-serialization
    type: secondary
---

## 题目描述

实现任意字节键值的序列化和分块持久化，支持完整性检查及中断写入后的恢复。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`encode(data)` 将 `dict[bytes,bytes]` 编码为 bytes，`decode(payload)` 还原。格式为：4 字节魔数 KVS1、8 字节大端无符号条目数；随后每条依次为 8 字节大端 key 长度、8 字节大端 value 长度、key 原始字节、value 原始字节。键值可含任意字节，不使用 pickle 或 JSON 编码键值。

`dump_chunks(data,directory,limit=1024)` 将完整编码流拆为每文件最多 limit 字节的分块，manifest 记录分块名及整流 SHA-256；最后才发布新 manifest。`load_chunks(directory)` 按 manifest 读取、校验并返回原字典。新写入若中断，旧 manifest 及其引用文件仍应可用；不得提前覆盖旧分块。校验失败不返回静默损坏的数据。数据不超过 10 MB，limit 为正整数。

### 示例

```text
data={b"a\0":b"x\ny"}，decode(encode(data)) 与 data 完全相同。
data={b"k":b"v"}，编码长度为 30 字节。
dump_chunks(data,目录,limit=5) 产生 6 个数据分块，load_chunks 返回 {b"k":b"v"}。
```

## 解题思路与参考答案

序列化用「字节长度 + 原始内容」编码字段，拆文件后再用 manifest 记录分片并原子发布。任意字符里什么都可能出现，选哪个分隔符都会和数据冲突，而「先写长度、再写内容」不需要转义。长度要按字节算：先把字符串统一编码成 bytes（例如 UTF-8），再取长度，否则多字节字符会让偏移错位。

## 题目

不用 JSON 或 pickle，把一个键值可以是任意字符的 KV store 序列化到磁盘再读回来。之后加一个限制：单个文件不能超过一个容量上限（例如 1KB），数据要拆到多个文件里。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理；`realInterview` 只表示网站把它收录为面经题型。下面的接口、约束和测试是手册补的练习约定。

读的一侧同样重要：

- 每次读字段前检查剩余字节够不够，处理短读和被损坏的长度字段；
- 文件开头放魔数或版本号，格式升级时能识别；
- 拆成多文件后，要说清楚分片怎么排序、怎么重组，以及怎么知道一组分片是完整的（这里用 manifest 和整体校验和）。

能 dump 和 load 不等于写入持久可靠。面试官追问崩溃恢复时，要讲原子替换或 WAL。

相关题：[[p3a-xai-durable-kv-cache]]（同一套接口，侧重重启恢复、WAL 和日志清理）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `encode(data) -> bytes` / `decode(payload) -> dict`：`data` 是 `dict[bytes, bytes]`，不能用 JSON 或 pickle，key 和 value 可以是任意字节。格式固定为 4 字节魔数 `KVS1`、8 字节条目数，然后每条是 8 字节 key 长度、8 字节 value 长度和原始字节，最后不能有多余数据。
- `dump_chunks(data, directory, limit=1024)`：把编码结果切成多个文件，每个不超过 `limit` 字节，最后再发布 `manifest.json`（记录分片文件名和整个 payload 的 SHA-256）。
- `load_chunks(directory)`：按 manifest 读回、校验并 decoding。
- 截断、魔数错误、重复 key、尾部多余数据、校验不通过都抛 `ValueError`。写新快照时旧快照的文件保留，写到一半失败不影响当前 manifest。快照不超过 10MB。
- 这份参考实现的是显式快照，不是每次写入都追加 WAL。

### 输入输出示例

```text
decode(encode({b"a\x00": b"x\ny"}))      -> {b"a\x00": b"x\ny"}
decode(encode({b"k": b"v"})[:-1])         -> ValueError（截断）
dump_chunks(data, d, 100); load_chunks(d) -> 与 data 相同，每个 .bin 文件 ≤ 100 字节
```

### 解题思路与正确性

每个字段都带字节长度前缀，decoding 时先读长度再读那么多字节，所以 key 或 value 里出现 `\x00`、换行或任何「分隔符」都不会产生歧义。`decode` 每次取数据前都检查剩余长度，读完声明的条目数后要求正好到达末尾，这样截断和多余数据都能发现。

`dump_chunks` 先写完所有带新版本号的分片并 fsync，再把 manifest 写到临时文件，用 `os.replace` 原子替换。读者要么看到旧 manifest、要么看到新 manifest，不会读到两个版本混在一起的分片。SHA-256 只负责发现损坏，不能修复；旧版本的孤立分片要等没有读者引用后再回收。

### 完整参考实现（Python 3）

```python
import hashlib
import json
import os
import struct
import uuid
from pathlib import Path

MAGIC = b"KVS1"
COUNT = struct.Struct(">Q")  # 条目数，8 字节大端
LENGTHS = struct.Struct(">QQ")  # 每条的 key 长度、value 长度


def encode(data):
    """把 dict[bytes, bytes] 编码成 MAGIC + 条目数 + (key 长, value 长, key, value)*。"""
    parts = [MAGIC, COUNT.pack(len(data))]
    for key, value in data.items():
        if not isinstance(key, bytes) or not isinstance(value, bytes):
            raise ValueError("keys and values must be bytes")
        parts.extend([LENGTHS.pack(len(key), len(value)), key, value])
    return b"".join(parts)


def decode(data):
    """encode 的逆操作；截断、魔数错误、重复 key 或尾部多余数据都抛 ValueError。"""
    pos = 0

    def take(size):
        nonlocal pos
        if pos + size > len(data):
            raise ValueError("truncated payload")
        chunk = data[pos : pos + size]
        pos += size
        return chunk

    if take(len(MAGIC)) != MAGIC:
        raise ValueError("bad magic")
    (count,) = COUNT.unpack(take(COUNT.size))
    result = {}
    for _ in range(count):
        key_len, value_len = LENGTHS.unpack(take(LENGTHS.size))
        key = take(key_len)
        value = take(value_len)
        if key in result:
            raise ValueError(f"duplicate key: {key!r}")
        result[key] = value
    if pos != len(data):
        raise ValueError("trailing bytes after last entry")
    return result


def write_durably(path, content):
    """写入并 fsync，保证返回时内容已落盘。"""
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(path, mode) as file:
        file.write(content)
        file.flush()
        os.fsync(file.fileno())


def dump_chunks(data, directory, limit=1024):
    """把快照切成每个不超过 limit 字节的文件，最后原子替换 manifest.json 来发布。"""
    if limit <= 0:
        raise ValueError("limit must be positive")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    payload = encode(data)
    version = uuid.uuid4().hex  # 新快照的文件名带版本号，不会覆盖旧快照
    names = []
    for start in range(0, len(payload), limit):
        name = f"{version}-{start // limit}.bin"
        write_durably(directory / name, payload[start : start + limit])
        names.append(name)

    manifest = {"files": names, "sha": hashlib.sha256(payload).hexdigest()}
    tmp = directory / f"{version}.manifest"
    write_durably(tmp, json.dumps(manifest))
    os.replace(tmp, directory / "manifest.json")  # 发布点：之前失败则旧 manifest 不变


def load_chunks(directory):
    """按 manifest 拼回 payload，校验 SHA-256 后 decoding。"""
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    if any(Path(name).name != name for name in manifest["files"]):
        raise ValueError("manifest file names must not contain paths")
    payload = b"".join((directory / name).read_bytes() for name in manifest["files"])
    if hashlib.sha256(payload).hexdigest() != manifest["sha"]:
        raise ValueError("checksum mismatch")
    return decode(payload)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert decode(encode(sample)) == sample` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
import tempfile


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


# 任意字节都能往返，包括空 key、\x00 和换行
sample = {b"a\x00": b"x\ny", b"": bytes(range(256)) * 8}
assert decode(encode(sample)) == sample
assert decode(encode({})) == {}

# 损坏的输入
encoded = encode(sample)
expect_value_error(decode, encoded[:-1])  # 截断
expect_value_error(decode, encoded + b"\x00")  # 尾部多余数据
expect_value_error(decode, b"XXXX" + encoded[4:])  # 魔数错误
expect_value_error(encode, {"text": b"v"})  # key 不是 bytes

# 分片落盘：每个数据文件不超过 limit，加载后完全一致
with tempfile.TemporaryDirectory() as tmp:
    dump_chunks(sample, tmp, 100)
    assert load_chunks(tmp) == sample
    assert all(path.stat().st_size <= 100 for path in Path(tmp).glob("*.bin"))

    # 再发布一版，读者只会看到新版本
    dump_chunks({b"k": b"v2"}, tmp, 100)
    assert load_chunks(tmp) == {b"k": b"v2"}

    # 分片被篡改时校验失败
    manifest = json.loads((Path(tmp) / "manifest.json").read_text())
    (Path(tmp) / manifest["files"][0]).write_bytes(b"corrupt")
    expect_value_error(load_chunks, tmp)
```

### 复杂度与追问

设 payload 大小为 B 字节。编码、decoding、分片写入和加载都是 O(B) 时间、O(B) 空间。

- `limit` 只约束数据分片，manifest 不计入。如果面试官要求 manifest 也受限，可以把文件列表改成「版本号 + 分片数」，文件名按规则推出来。
- 严格的断电持久性还需要在 `os.replace` 之后 fsync 父目录，否则目录项的更新可能丢失。
- 每次写入都要持久（而不是定期快照）就得加 WAL：每条记录带长度和校验和追加写，恢复时从最新快照开始重放，遇到长度不够或校验失败的尾部记录就截掉。快照实现本身不能当作 WAL 用。
