---
id: openai-gpu-credits
section: openai
order: 40
level: S
title: OpenAI：GPU credit，调用乱序也要按时间重放
quick: >-
  addCredit、useCredit、getBalance。额度有生效时刻和过期时刻，调用可以晚于它描述的时间到达。
  主日志只追加。查余额时复制一份，只重放时间不超过查询点的事件，先花最快过期的额度。
tags:
  - OpenAI
  - Coding
  - Intervals
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: Targeting OpenAI SWE Roles, r/leetcode
    url: https://www.reddit.com/r/leetcode/comments/1qlzflr/targeting_openai_swe_roles_insights_on_what_to/
    type: candidate-first-hand
  - title: "Openai Tech Phone Screen: GPU Credit Calculator"
    url: https://www.1point3acres.com/interview/thread/1098314
    type: candidate-first-hand
  - title: "FAANG-Coding-Interview-Questions, OpenAI bank"
    url: https://github.com/ombharatiya/FAANG-Coding-Interview-Questions/blob/main/FAANG-Recent-Questions.md
    type: secondary
---

## 真题记录

Reddit 上一篇 2026 年 OpenAI SWE 循环总结把 GPU Credit Calculator 写成最近考过的题，并给了接口。一亩三分地有一条电话面标题就是 Implementing a GPU Credit Calculator，正文要登录。GitHub 上 ombharatiya 的 2025–2026 题单把它列在 OpenAI 核心题里：半开区间，先消耗最快过期的额度，任意时刻能查余额。

公开接口是这三支：

- `addCredit(credit_id, amount, timestamp, expiration)`：额度从 `timestamp` 起可用。`expiration` 在不同转述里有人写成时长，有人写成结束时刻。现场先问。下面按「结束时刻、区间为 `[start, end)`」写，和 GitHub 题单的半开区间一致。
- `useCredit(timestamp, amount)`：在那个时刻扣。余额不够就失败，不能扣成负数。
- `getBalance(timestamp)`：那个时刻扣完、过期处理完之后还剩多少。

调用顺序不等于时间顺序。可以先收到 `useCredit(20, 30)`，后收到 `addCredit(..., 50, start=10, end=50)`。时刻 20 落在额度的有效区间里，这次使用仍然成立。

## 我会怎么写

主结构是一张只追加的事件日志，不在收到调用时改历史余额。`add` 记两条：生效、过期。`use` 记一条。`getBalance(t)` 复制日志，只留下时间不超过 `t` 的事件，排序后重放。

同一时刻的顺序要定死：先过期，再生效，再扣款。否则「刚好在过期点使用」会对不上测试。重放时用一个按结束时刻排序的堆放还活着的额度。扣款每次弹出最快过期的，扣完还有剩就推回去。

```python
RANK = {"expire": 0, "add": 1, "use": 2}

def replay(events, t):
    active = []  # (end, remaining, credit_id)
    chosen = [e for e in events if e[1] <= t]
    chosen.sort(key=lambda e: (e[1], RANK[e[0]]))
    for kind, ts, *rest in chosen:
        if kind == "expire":
            active = [g for g in active if g[2] != rest[0]]
        elif kind == "add":
            amount, end, cid = rest
            active.append([end, amount, cid])
        else:
            need = rest[0]
            active.sort()
            for grant in active:
                if need == 0:
                    break
                take = min(grant[1], need)
                grant[1] -= take
                need -= take
            if need:
                return None
            active = [g for g in active if g[1] > 0]
    return sum(g[1] for g in active)
```

失败的 `use` 不能留在日志里。成功的 `use` 才追加。因为后面的 `add` 可能让早先的 `use` 变合法，不能在调用到达的瞬间就拒绝。有人把「现在余额不够」直接返回失败，乱序的 `add` 一来，历史就错了。

## 追问

**每次查询都重放会不会太慢？** 面试先交正确的重放。若事件很多，按时间建检查点，查询从最近的检查点继续。检查点必须在该时刻之前，不能把更晚才收到、但时间更早的事件漏掉，所以检查点只能盖住「时间戳和到达顺序都已经稳定」的前缀。

**同一笔额度被两笔 use 各扣一部分？** 堆里存剩余量，不存原始面额。过期事件按 `credit_id` 删掉剩余，不要按原始金额再减一次。
