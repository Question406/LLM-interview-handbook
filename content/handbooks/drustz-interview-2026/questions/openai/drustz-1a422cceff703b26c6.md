---
id: drustz-1a422cceff703b26c6
section: openai
order: 127
level: A
title: Social Network Follow/Unfollow With Snapshots
quick: >-
  original-structured-preparation-guide · Social Network Follow/Unfollow With
  Snapshots
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/1e1193de-63cd-4149-97cc-b9b5f229a015
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Follow/Unfollow 与 Snapshot：边版本日志实现

> 内容定位：本地面经直接记录了 `follow`、`unfollow`、`snap`、`is_following(...,snapId)`；以下用事件版本实现，不复制整图，也不是会员原文。

## 精确的数据模型

实现：

```text
follow(a,b) -> bool
unfollow(a,b) -> bool
snap() -> int
is_following(a,b,snap_id) -> bool
```



维护全局 `clock`、`snapshot_cutoff` 和 `changes[(a,b)]`。每次真正改变边状态时先令 `clock += 1`，再追加 `(clock,new_state)`；`snap()` 把当前 clock 加入 `snapshot_cutoff`，返回其数组下标。这样连续拍两个快照也是合法的，它们可指向同一个 cutoff，且都不需要复制任何边。

```python
def is_following(a, b, sid):
    if not 0 <= sid < len(snapshot_cutoff):
        raise IndexError("unknown snapshot")
    h = changes.get((a, b), [])
    cutoff = snapshot_cutoff[sid]
    i = bisect_right(h, (cutoff, True)) - 1
    return i >= 0 and h[i][1]
```



Python 元组比较中 `False < True`；日志同一 clock 只有一条，因此 `(cutoff,True)` 能包含该版本的任一布尔状态。跨语言实现可单独对 version 数组做 upper-bound，再读对应 state，语义更清楚。

## 例子与正确性

```text
follow(A,B)       # clock=1
s0=snap()         # cutoff[0]=1
unfollow(A,B)     # clock=2
s1=snap()         # cutoff[1]=2
follow(A,B)       # clock=3
s2=snap()         # cutoff[2]=3
```



于是 `is_following(A,B,s0)=True`、s1 为 False、s2 又为 True。理由是某个 cutoff 下边的真实状态，恰好等于不晚于 cutoff 的最后一次变更；二分返回的正是该记录。如果找不到记录，说明该边当时尚未创建，结果为 False。

这里的 `snap_id` 是连续的小整数，真正用于历史比较的是它映射到的 cutoff，二者不要混用。特别是两个快照之间可能有很多更新，也可能完全没有更新；直接把 sid 当 mutation version 会在这两种情况下都产生错误答案。

为让重复调用有确定语义，可另存 live state：重复 `follow` 返回 False 且不递增 clock，重复 `unfollow` 同理。self-follow、未知用户是返回 False 还是抛错需按题面统一；关键是不能留下互相矛盾的日志。

## 复杂度与边界

有效更新摊销 `O(1)`，拍快照 `O(1)`，历史查询 `O(log H_e)`，总空间 `O(M+S)`，分别是状态变化和快照数量。相比每次 `deepcopy` 的 `O(U+E)` 时间/空间，这一方案尤其适合快照很多、每次只改少数边的场景。测试必须包含快照前查询、同一边反复开关、空快照、连续空快照、非法 sid，以及“更新后旧 sid 结果不变”。并发下需让 clock 分配、live state 检查和日志追加位于同一锁或事务中。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/1e1193de-63cd-4149-97cc-b9b5f229a015)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
