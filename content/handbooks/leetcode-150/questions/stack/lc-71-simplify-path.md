---
id: lc-71-simplify-path
section: stack
order: 2
level: A
title: LC 71 · 简化路径
quick: >-
  按 `/` 切开。`..` 弹栈，`.` 与空段忽略，其余当目录名入栈。最后 `"/" + join`。时间
  $O(n)$。
tags:
  - Stack
  - String
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 71. 简化路径
    url: https://leetcode.cn/problems/simplify-path/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

把 Unix 风格绝对路径化简：多个 `/` 合成一个，`.` 表示当前目录，`..` 返回上一级（已在根则停），目录名原样保留。结果以 `/` 开头、不以 `/` 结尾（根除外）。

## 思路

`path.split("/")` 后用栈。空串来自开头、结尾或连续斜杠，丢掉。`.` 丢掉。`..` 若栈非空则弹出。其他分段是合法目录名，加入栈中。最后 `"/" + "/".join(stack)`；栈空则返回 `"/"`。

别自己逐字符解析斜杠，先 split 更不容易写错。`...` 是目录名，不是 `..`。

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

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。$n$ 为路径长度。

## 边界

- 根上再 `..`：栈空不弹，结果仍是 `/`。
- 连续 `///`：`split` 产生空段，直接跳过。
- 目录名含 `.`：`...`、`..a` 都是合法名字，不是 `..`。
- 结尾 `/`、只有 `/`：栈空返回 `"/"`。

## 追问

- **相对路径怎么化简？** 没有强制开头的 `/`，栈空时 `..` 要保留（还能再往上走）。若栈顶是普通目录名则弹出；若栈空或栈顶已是 `..` 则再压一个 `..`。`.` 与空段仍忽略。结果用 `/` 拼接，栈空返回 `"."`，不要加根斜杠。`a/../../b` 得到 `../b`。绝对路径绝不能把 `..` 留在栈里。

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

- **还原成段列表给文件系统？** 直接返回栈，不必 `"/" + join`。调用方自己用当前工作目录拼接。绝对路径化简后栈里从根往下的各级名字，空栈表示根。别把 `""`、`"."` 留在列表里。若还要做权限检查或 inode 查找，按这段列表逐级 walk 即可，化简已经去掉了无用的 `..` 与重复斜杠。

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
