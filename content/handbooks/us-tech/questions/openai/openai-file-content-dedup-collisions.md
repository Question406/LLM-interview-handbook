---
id: openai-file-content-dedup-collisions
section: openai
order: 931
level: A
title: "OpenAI 文件题扩展：content deduplication 与 hash collision 校验"
quick: "我会把 hash 当成快速定位候选的方法，真正的相等条件仍然是 bytes 相同。这样测试可以故意让所有文件的 digest 一样，结果也必须正确。"
companies:
  - openai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：OpenAI 文件题扩展：content deduplication 与 hash collision 校验"
    url: "https://aceoffer.app/interviews/oai_file_folder_deduplication_and_navigation"
    type: secondary
---

## 题目描述

来源：AceOffer 公开目录列出 file/folder deduplication and navigation。这里练习其 content grouping 模块；路径合法性、hash collision 检查与输出顺序由手册设定。

### 输入、接口与规则

实现 `duplicate_files(files, digest=None) -> list[list[str]]`。files 是只能遍历一次的 `(path, content)` iterable；path 为唯一的非空 absolute POSIX path，已规范化，content 为 bytes，包括空 bytes。相同 content 的不同 paths 视为重复，path 名字或 folder 不影响内容相等的定义。

返回所有含至少两个 paths 的重复组。每组 paths 按字符串升序，组列表也按组的 lexicographic order 升序；不返回 singleton。默认 digest 为 SHA-256；测试可注入 `digest(bytes)->hashable`，即使不同 content 得到同一个 digest 也不能被错误合并。出现重复 path 抛 ValueError。输入规模能放入内存；不读真实文件，不修改输入。

### 输入输出示例

```text
files=[("/a",b"x"),("/b",b"x"),("/c",b"y"),("/d",b"")]
返回 [["/a","/b"]]。
若 digest 对所有内容都返回 0，结果仍然相同。
```

## 回答思路

> **Situation / Task：** 要按 bytes 内容分组，hash 相同只是候选。  
> **Approach / Why：** 先按 digest 分桶，再以 bytes 精确比较分组，最后排序。  
> **Result / Check：** 注入恒定 digest 强制碰撞，检查空文件和重复 path。

## 解题思路与参考答案

我会把 hash 当成快速定位候选的方法，真正的相等条件仍然是 bytes 相同。这样测试可以故意让所有文件的 digest 一样，结果也必须正确。

参考实现每个 digest bucket 里再用 bytes 作为 dict key。Python dict 对 key 相等会做精确比较，所以不会因为外层 digest 碰撞就把不同文件并起来。这里只返回重复组，navigation 是来源题型中的另一部分。

### 完整参考实现

```python
import hashlib


def duplicate_files(files, digest=None):
    if digest is None:
        digest = lambda data: hashlib.sha256(data).digest()
    buckets = {}
    paths = set()
    for path, content in files:
        if path in paths:
            raise ValueError('duplicate path')
        paths.add(path)
        bucket = buckets.setdefault(digest(content), {})
        bucket.setdefault(content, []).append(path)
    return sorted(
        sorted(group)
        for bucket in buckets.values()
        for group in bucket.values()
        if len(group) > 1
    )
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
files = [('/a', b'x'), ('/b', b'x'), ('/c', b'y'), ('/d', b'')]
assert duplicate_files(iter(files)) == [['/a', '/b']]
assert duplicate_files(iter(files), lambda _: 0) == [['/a', '/b']]
assert duplicate_files([('/a', b''), ('/z', b'')]) == [['/a', '/z']]
assert duplicate_files([]) == []
try:
    duplicate_files([('/a', b'x'), ('/a', b'x')])
except ValueError:
    pass
else:
    raise AssertionError('duplicate path accepted')
print('file dedup tests passed')
```

## 复杂度与追问

设总内容长度 B、文件数 F，正常 hash 分布下期望时间约 `O(B+F*log F)`；输入内容与结果相关空间 `O(B+F)`。Python bytes 自身 hash 若被对抗性碰撞，dict 最坏性能仍可能下降；外层 digest collision 不影响正确性。大文件应改为 size/hash 分组后流式 byte comparison。
