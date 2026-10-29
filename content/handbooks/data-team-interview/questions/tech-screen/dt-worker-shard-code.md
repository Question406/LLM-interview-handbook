---
id: dt-worker-shard-code
section: tech-screen
order: 42
level: S
title: CoderPad：IterableDataset 多进程读取，怎样避免每个 worker 都读一遍？
quick: >-
  先把 rank 与 worker 映射成全局消费者编号，再按稳定分片编号取模分配。必须说明 worker 数固定的假设；重新洗牌、弹性扩容和
  checkpoint 恢复不能靠这个映射自动解决。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - AFM 加练第二批
  - 完整编程练习
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: PyTorch Dataset and DataLoader
    url: 'https://docs.pytorch.org/docs/2.14/data.html'
    type: primary
---

## 题目描述

原创练习；建议限时 15 分钟。多个训练 rank 各自运行相同数量的数据读取 worker，所有消费者获得同一份、同顺序的不可变分片清单。

### 输入与接口

实现 `assign_shards(shards, rank, world_size, worker_id, workers_per_rank)`。shards 为互不重复的字符串列表，可为空。world_size 与 workers_per_rank 为正整数，rank 和 worker_id 分别为各自合法的零基编号。

### 输出与约束

全局消费者编号为 `rank * workers_per_rank + worker_id`，总数为 `world_size * workers_per_rank`。返回所有原始下标对总数取模等于该编号的分片名，保留清单顺序，不修改输入。一个 epoch 内每片必须恰好分配一次；分片数可小于消费者数。

### 示例

```text
shards=['a','b','c','d','e','f','g']
world_size=2, workers_per_rank=2
rank=1, worker_id=0 -> ['c','g']
```

## 解题思路与参考答案

每个 IterableDataset worker 拥有自己的数据集实例，若不做分片会重复读取。这里将所有 rank 的 worker 视为同一个编号空间，避免只按本地 worker_id 分片造成跨 rank 重复。

```python
def assign_shards(shards, rank, world_size, worker_id, workers_per_rank):
    consumer = rank * workers_per_rank + worker_id
    consumers = world_size * workers_per_rank
    return [shards[i] for i in range(consumer, len(shards), consumers)]
```

每个消费者读取其分片的编号，时间为 $O(1+N/C)$，C 为消费者数，不包含数据实际读取。它按分片数分配，不保证字节、token 或读取耗时均衡。

## 简单测试怎么写

将实现与测试保存为 `solution.py`，运行 `python3 solution.py`。将四个消费者的结果合起来，检查没有丢失和重复，并测试空分配。

```python
shards = list('abcdefg')
assert assign_shards(shards, 1, 2, 0, 2) == ['c', 'g']
parts = [assign_shards(shards, r, 2, w, 2) for r in range(2) for w in range(2)]
flat = [s for part in parts for s in part]
assert sorted(flat) == sorted(shards)
assert len(flat) == len(set(flat))
assert assign_shards(['a'], 1, 2, 1, 2) == []
assert assign_shards([], 0, 1, 0, 1) == []
assert shards == list('abcdefg')
```

## 面试追问

**每个 worker 先独立 shuffle 再分配可以吗？** 若排列不同，会漏片或重复。先用共享 seed 得到同一排列再分配，之后才做消费者内的局部随机化。

**增加 rank 后从旧 offset 恢复行吗？** 不能直接保证正确。映射发生变化，需用稳定的已消费分片状态或重新分配协议处理，明确重新分配时是否允许重复。

**一片极大怎么办？** 预先按工作量切分，或采用可追踪领取的动态任务分配；需要另行处理重试和消费一致性。
