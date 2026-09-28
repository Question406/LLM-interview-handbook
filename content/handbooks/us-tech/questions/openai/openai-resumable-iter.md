---
id: openai-resumable-iter
section: openai
order: 41
level: A
title: OpenAI：可恢复迭代器，getState 之后还能接着 next
quick: >-
  next、getState、setState。状态要能回到某一次 next 之前的位置，空文件和迭代结束都要能往前走。
  公开题单把它写成从单列表加到多文件、异步、二维。完整函数表没有一份逐字帖。
tags:
  - OpenAI
  - Coding
  - Iterator
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: Targeting OpenAI SWE Roles, r/leetcode
    url: https://www.reddit.com/r/leetcode/comments/1qlzflr/targeting_openai_swe_roles_insights_on_what_to/
    type: secondary
  - title: "FAANG-Coding-Interview-Questions, OpenAI bank"
    url: https://github.com/ombharatiya/FAANG-Coding-Interview-Questions/blob/main/FAANG-Recent-Questions.md
    type: secondary
---

## 题怎么来的

同一篇 Reddit 的 OpenAI SWE 题单里有一句：实现一个能在遍历中途停下、再从原位置继续的迭代器。GitHub 题单写成最多六段：列表、多文件、异步、二维、三维，接口是 `getState` / `setState`。没有一份公开帖贴出完整签名和测试。`realInterview: false`。下面按这两份清单里重复出现的行为写，现场以面试官的测试为准。

## 列表

`next` 返回当前元素并前进。用完抛一个明确的结束，不要返回 `None` 当哨兵，因为数据里可以有 `None`。

`getState` 返回的是「下一次 `next` 会读的位置」，不是上一次已经交出的那个。列表 `[1, 2, 3, 4]`：两次 `next` 得到 1 和 2，此时状态指向 3。再 `next` 得到 3 之后 `setState` 回刚才的状态，下一次仍应得到 3。

状态做成不可变的小对象或元组。调用方改自己的拷贝，不能改迭代器内部。`setState` 收到别的迭代器的状态要拒绝。

```python
class ListIter:
    def __init__(self, data):
        self.data = data
        self.i = 0

    def next(self):
        if self.i >= len(self.data):
            raise StopIteration
        value = self.data[self.i]
        self.i += 1
        return value

    def get_state(self):
        return self.i

    def set_state(self, state):
        if not isinstance(state, int) or not 0 <= state <= len(self.data):
            raise ValueError(state)
        self.i = state
```

## 多文件

外层状态是 `(file_index, inner_state)`。空文件不能让外层停住：当前文件的 `next` 结束，就打开下一个，直到有元素或文件都用完。只存文件下标、不存文件内下标，恢复后会从头再读这一文件。

异步那一档不要在 `getState` 里等在途的读完成再返回。状态要么是「这一笔读还没开始」，要么是「字节已经拿到、位置已经前进」。停在半次 `read` 上，恢复时会重复或丢掉一块。

二维是把内层迭代器的状态嵌进外层。不要假设内层状态是一个整数。接口从第一档就收一个不透明状态，后面几档不用改外层协议。

## 追问

**状态能不能是迭代器自己？** 不能。调用方会留着它，你继续 `next` 之后那份状态也跟着变，就无法回到过去。返回时复制下标。

**文件在 setState 之后被改了？** 题面通常假设文件不变。若面试官加上，状态里要带长度或校验，对不上就报错，不要静默读到别的记录。
