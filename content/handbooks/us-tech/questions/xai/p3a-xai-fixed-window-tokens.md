---
id: p3a-xai-fixed-window-tokens
section: xai
order: 750
level: S
title: "xAI：固定窗口 Token Limiter：乱序时间戳与 RESET"
quick: "我会用 (key, t // width) 定位每个窗口的已用 token，只有不超额才增加计数，刚好用满也允许。这样乱序请求不会覆盖别的窗口；RESET 删除该 key 的所有窗口，包括旧时间戳对应的记录，旧窗口是否能清理要另定乱序范围。"
companies:
  - xai
tags:
  - xAI
  - Coding
  - Frontier-2026-10
  - 完整编程练习
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: 1Point3Acres xAI source
    url: https://www.1point3acres.com/interview/problems/b6025b30-5ff6-5b70-8a92-fa46a1ebc43c
    type: secondary
---

## 题目描述

实现按 key 独立计量的固定窗口 token 限流器。请求时间允许乱序，同一个 key 的不同窗口互不占用配额。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `Limiter(limit, width)`：`limit` 是每个窗口的 token 上限，`width` 是窗口长度，都必须为正。
- `allow(key, cost, t)`：请求落在窗口 `t // width`。已用量加上 `cost` 不超过 `limit` 就扣量并返回 `True`，否则返回 `False` 且不扣量。`cost` 必须为正，`t >= 0`，`t` 可以乱序。
- `reset(key)`：删除这个 key 的全部窗口记录。
- 最多 $2 \times 10^5$ 次操作，旧窗口不自动淘汰。

### 输入输出示例

```text
limiter = Limiter(limit=10, width=60)
allow("a", 3, 0)    -> True    # 窗口 0 用了 3
allow("a", 8, 10)   -> False   # 3 + 8 > 10，不扣量
allow("a", 7, 1)    -> True    # 窗口 0 正好用满
allow("a", 10, 60)  -> True    # 窗口 1 独立计量
allow("a", 1, 59)   -> False   # 乱序回到窗口 0，已满
reset("a")
allow("a", 10, 0)   -> True
```

## 解题思路与参考答案

我会按 key 和窗口编号分别保存计数，接受请求才扣量。例如先收到时间戳 60，再收到 59，后者仍应计入旧窗口，不能把 60 所属窗口的额度重置。RESET 则一次清掉这个 key 的全部窗口。

## 题目

实现一个按 token 计量的固定窗口限流器。每个 key 在每个固定时间窗口里最多消耗一定数量的 token，超额的请求被拒绝，并且不扣量。请求的时间戳可能乱序到达；还要支持 RESET，清掉某个 key 的全部窗口记录。

> 来源：一亩三分地 xAI 题卡（2026-10-18 读取），读到了网站上的题干。下面的函数签名、约束和测试是手册补的练习约定，原帖没写的条件不当作已确认的面试事实。

## 思路

关键是用窗口编号 `t // width` 来定位状态，而不是只记「当前窗口」。如果只保存最近一个窗口，一个时间戳较早的请求晚到时，会把状态切回旧窗口，把新窗口已经用掉的额度弄丢。按 `(key, 窗口编号)` 分别计量，乱序请求只会落到自己所属的窗口里。

扣量时允许正好用满 limit，超额就直接拒绝，保留原有已用量。RESET 后，旧时间戳再次到达也按全新状态计算，因为这个 key 的所有窗口都已经删除。

可以和面试官确认：旧窗口要不要自动清理。这份练习不自动清理，因为乱序请求随时可能落到很早的窗口上。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Limiter(limit, width)`：`limit` 是每个窗口的 token 上限，`width` 是窗口长度，都必须为正。
- `allow(key, cost, t)`：请求落在窗口 `t // width`。已用量加上 `cost` 不超过 `limit` 就扣量并返回 `True`，否则返回 `False` 且不扣量。`cost` 必须为正，`t >= 0`，`t` 可以乱序。
- `reset(key)`：删除这个 key 的全部窗口记录。
- 最多 $2 \times 10^5$ 次操作，旧窗口不自动淘汰。

### 输入输出示例

```text
limiter = Limiter(limit=10, width=60)
allow("a", 3, 0)    -> True    # 窗口 0 用了 3
allow("a", 8, 10)   -> False   # 3 + 8 > 10，不扣量
allow("a", 7, 1)    -> True    # 窗口 0 正好用满
allow("a", 10, 60)  -> True    # 窗口 1 独立计量
allow("a", 1, 59)   -> False   # 乱序回到窗口 0，已满
reset("a")
allow("a", 10, 0)   -> True
```

### 解题思路与正确性

状态是一个两层字典：key 映射到「窗口编号到已用量」的字典。`allow` 先算出窗口编号，读出已用量，判断加上 `cost` 后会不会超过 `limit`，只有不超过时才写回。每个窗口的计数只受落在这个窗口里的请求影响，所以请求的到达顺序不会改变某个窗口能否接受一个请求。被拒绝的请求不写状态，自然不扣量。`reset` 整体删掉这个 key 的字典，下次访问时重新创建。

### 完整参考实现（Python 3）

```python
class Limiter:
    """固定窗口限流：每个 key 在每个窗口 t // width 内最多消耗 limit 个 token。"""

    def __init__(self, limit, width):
        if limit <= 0 or width <= 0:
            raise ValueError("limit and width must be positive")
        self.limit = limit
        self.width = width
        self.usage = {}  # key -> {窗口编号: 已用 token 数}

    def allow(self, key, cost, t):
        """够用就扣量并返回 True；不够返回 False，且不扣量。t 可以乱序到达。"""
        if cost <= 0:
            raise ValueError("cost must be positive")
        if t < 0:
            raise ValueError("timestamp must be non-negative")
        windows = self.usage.setdefault(key, {})
        window = t // self.width
        used = windows.get(window, 0)
        if used + cost > self.limit:
            return False
        windows[window] = used + cost
        return True

    def reset(self, key):
        """清掉这个 key 的所有窗口记录。"""
        self.usage.pop(key, None)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert limiter.allow("a", 3, 0)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")

limiter = Limiter(limit=10, width=60)

# 窗口 0 已用 3，再要 8 会超额，被拒绝且不扣量
assert limiter.allow("a", 3, 0)
assert not limiter.allow("a", 8, 10)

# 正好用满 limit 是允许的；窗口 1 与窗口 0 独立计量
assert limiter.allow("a", 7, 1)
assert limiter.allow("a", 10, 60)

# 乱序回到窗口 0，此时它已经用满
assert not limiter.allow("a", 1, 59)

# reset 清掉所有窗口，旧时间戳也按新状态计算
limiter.reset("a")
assert limiter.allow("a", 10, 0)

# 不同 key 互不影响
assert limiter.allow("b", 10, 0)

# 非法参数
expect_value_error(Limiter, 0, 60)
expect_value_error(limiter.allow, "a", 0, 0)
expect_value_error(limiter.allow, "a", 1, -1)
```

### 复杂度与追问

设某个 key 出现过的窗口数为 $W_k$。`allow` 是 O(1)（字典操作，均摊），`reset` 释放这个 key 的字典是 O($W_k$)，总空间是出现过的 (key, 窗口) 对数。

- 多线程怎么办？「读已用量、判断、写回」必须是一个原子操作，可以按 key 加锁，否则两个并发请求可能都通过检查，合计超过 limit。
- 内存会一直涨，能不能回收旧窗口？如果业务保证乱序只在一个有限的时间范围内，就可以清理比当前时间早超过这个范围的窗口。如果历史时间戳的请求随时可能合法地到达，就不能简单按当前时钟回收。
