---
id: lc-71-simplify-path
section: stack
order: 2
level: A
title: LC 71 · 简化路径
quick: >-
  先按 `/` 切开再用栈：`..` 弹栈，`.` 和空段忽略，其余当目录名入栈，最后拼成 `"/" + join`。比逐字符解析斜杠更不容易写错，时间
  $O(n)$。
tags:
  - Stack
  - String
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 71. 简化路径
    url: 'https://leetcode.cn/problems/simplify-path/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定 Unix 风格的绝对路径，返回等价的规范路径。连续多个斜杠视为一个分隔符；单独的 "." 表示当前目录，".." 表示父目录，在根目录再向上仍留在根目录。其他目录名必须原样保留，包括 "..." 这样的名字。

### 输入与输出

实现 `simplifyPath(path) -> str`。返回以单个 "/" 开头、目录之间只用单个 "/" 分隔、没有 "." 或 ".." 分量的路径；除根目录 "/" 外，末尾不能有斜杠。

### 约束与约定

- `1 <= len(path) <= 3000`。
- 输入是合法绝对路径，只含英文字母、数字、点、斜杠或下划线。
- 本题只做字符串路径规范化，不读取文件系统或解析符号链接。

### 示例

```text
输入：path = "/home/"
输出："/home"
```

示例只需去掉目录 home 后多余的尾部分隔符。

[官方原题与完整题面](https://leetcode.com/problems/simplify-path/description/)。

## 解题思路与参考答案

## 题意

把 Unix 风格绝对路径化简：多个 `/` 合成一个，`.` 表示当前目录，`..` 返回上一级（已在根则停），目录名原样保留。结果以 `/` 开头、不以 `/` 结尾（根除外）。

## 思路

我会先 `path.split("/")`，再用栈处理每一段，比自己逐字符解析斜杠更不容易写错。空串来自开头、结尾或连续的斜杠，丢掉；`.` 也丢掉；`..` 在栈非空时弹出一层；其余都是合法目录名，压栈。最后返回 `"/" + "/".join(stack)`，栈空时结果正好是 `"/"`。

拿 `/home/user/Documents/../Pictures` 走一下。切开后依次压入 `home`、`user`、`Documents`，遇到 `..` 弹掉 `Documents`，再压 `Pictures`，结果是 `/home/user/Pictures`。

有个容易看错的点：`...` 是目录名，和 `..` 没关系。

## 参考代码

```python
def simplifyPath(path: str) -> str:
    st = []
    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if st:
                st.pop()
        else:
            st.append(part)
    return "/" + "/".join(st)


if __name__ == "__main__":
    assert simplifyPath("/home/") == "/home"
    assert simplifyPath("/home//foo/") == "/home/foo"
    assert simplifyPath("/home/user/Documents/../Pictures") == "/home/user/Pictures"
    assert simplifyPath("/../") == "/"
    assert simplifyPath("/.../a/../b/c/../d/./") == "/.../b/d"
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert simplifyPath("/home/") == "/home"
assert simplifyPath("/home//foo/") == "/home/foo"
assert simplifyPath("/home/user/Documents/../Pictures") == "/home/user/Pictures"
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。$n$ 为路径长度。

## Edge Cases

已经在根还遇到 `..`，栈空不弹，结果仍是 `/`。

连续的 `///` 会被 `split` 切出空段，直接跳过。

目录名里带 `.` 的，比如 `...`、`..a`，都是合法名字，和 `..` 不一样。

结尾多一个 `/` 只会多切出一个空段，被跳过；只有 `/` 时栈空，返回 `"/"`。

## 追问

**相对路径怎么化简？**
没有开头的 `/`，栈空时遇到 `..` 要保留下来，因为还能再往上走。栈顶是普通目录名就弹出；栈空或者栈顶已经是 `..`，就再压一个 `..`。`.` 和空段照样忽略。结果用 `/` 拼接，栈空返回 `"."`，不要加根斜杠。比如 `a/../../b` 得到 `../b`。绝对路径就绝不能把 `..` 留在栈里。

```python
def simplifyRelative(path):
    st = []
    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if st and st[-1] != "..":
                st.pop()
            else:
                st.append("..")
        else:
            st.append(part)
    return "/".join(st) if st else "."
```

**要还原成段列表交给文件系统呢？**
直接返回栈，不用 `"/" + join`，调用方自己拿当前工作目录去拼。绝对路径化简后，栈里是从根往下的各级名字，空栈表示根，`""`、`"."` 别留在列表里。如果还要做权限检查或 inode 查找，按这个列表逐级 walk 就行，化简已经去掉了无用的 `..` 和重复斜杠。

```python
def simplifyPathParts(path):
    st = []
    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if st:
                st.pop()
        else:
            st.append(part)
    return st
```
