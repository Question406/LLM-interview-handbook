---
id: p3a-openai-poker-simulation
section: openai
order: 614
level: A
title: "OpenAI：三张牌模拟与可扩展牌型比较"
quick: "每手牌编码成可按字典序比较的 tuple，先放牌型等级，再放该牌型破平局的点数。加同花只扩展评估器，弃牌则在发牌后、比较前过滤。发牌、评估和选赢家分开，规则变化时就不必重写整个模拟。"
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · poker-simulation"
    url: https://www.1point3acres.com/interview/problems/company/openai/poker-simulation
    type: secondary
---

## 题目描述

模拟三张牌的简化扑克比赛，实现牌型排序和确定性发牌，并支持只让对子或三条玩家继续参与比较的规则。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- 牌表示为 `(rank, suit)`，`rank` 取 2 到 14（14 是 A），`suit` 取 0 到 3。每手恰好 3 张不重复的牌。
- `rank_hand(hand, flush=True) -> tuple`：返回可比较的 tuple。等级为三条 3、同花 2、对子 1、高牌 0，同等级内按相关点数降序比较。没有顺子规则，花色不破平局。`flush=False` 时不识别同花，对应第一阶段的规则。
- `deal(players, seed=0, discard=False)`：从 52 张牌中无放回地给每人发 3 张，返回 `(hands, winners, folded)`：各家手牌、赢家下标列表（可能多人并列）、弃牌玩家下标列表（即过程日志）。
- `discard=True` 时只有对子或三条的玩家留下，其余弃牌且不补牌。$1 \le \text{players} \le 17$。
- rank tuple 精确格式：三条 (3,点数)，同花 (2,从大到小三点数)，对子 (1,对子点数,单张点数)，高牌 (0,从大到小三点数)。deal 的 winners/folded 均为0开始的玩家下标升序列表；全部弃牌时 winners=[]。

### 输入输出示例

```text
rank_hand([(2,0), (2,1), (2,2)])   -> (3, 2)              # 三条 2
rank_hand([(14,0), (13,0), (12,0)]) -> (2, 14, 13, 12)    # 同花 A 高，比三条 2 小
rank_hand([(9,0), (9,1), (13,2)])  -> (1, 9, 13)          # 对子 9 带 K，比对子 8 带 A 大
rank_hand([(14,0), (10,1), (5,2)]) == rank_hand([(14,3), (10,2), (5,1)])  -> True  # 只差花色，并列
```

## 解题思路与参考答案

我会用 tuple 编码牌型，把比较规则集中到评估器。比如对子 9 带 K 写成 `(1, 9, 13)`，比对子 8 带 A 时先看对子点数；同花和三条也只要用不同等级即可。发牌与弃牌逻辑分开，后续加规则时改动更局部。

模拟一个三张牌的扑克游戏：给每个玩家发三张牌，记录过程，按三条、对子、高牌比较大小选出赢家。之后面试官会加新规则，比如引入同花牌型、允许没有对子的玩家弃牌。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；网站收录为面经题型不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

关键设计是让「比较两手牌」变成比较两个 tuple。比如三条 2 编码成 `(3, 2)`，对子 9 带 K 编码成 `(1, 9, 13)`，高牌 A、10、5 编码成 `(0, 14, 10, 5)`。Python 的 tuple 按字典序比较：先比牌型等级，相同再依次比后面的点数，正好就是牌型规则。

这样做的好处是扩展规则时改动很小。加同花只要在评估函数里多一个分支，给它一个介于对子和三条之间的等级；发牌、比较、选赢家的代码都不用动。弃牌规则也只是在发牌后、比较前加一步过滤。

需要和面试官确认的规则：

- 同牌型且点数完全一样时是并列，还是用花色破平局；
- 有没有顺子，A 能不能当 1 用；
- 弃牌后是否补牌，所有人都弃牌时怎么算。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- 牌表示为 `(rank, suit)`，`rank` 取 2 到 14（14 是 A），`suit` 取 0 到 3。每手恰好 3 张不重复的牌，否则抛 `ValueError`。
- `rank_hand(hand, flush=True) -> tuple`：返回可比较的 tuple。等级为三条 3、同花 2、对子 1、高牌 0，同等级内按相关点数降序比较。没有顺子规则，花色不破平局。`flush=False` 时不识别同花，对应第一阶段的规则。
- `deal(players, seed=0, discard=False)`：从 52 张牌中无放回地给每人发 3 张，返回 `(hands, winners, folded)`：各家手牌、赢家下标列表（可能多人并列）、弃牌玩家下标列表（即过程日志）。
- `discard=True` 时只有对子或三条的玩家留下，其余弃牌且不补牌。$1 \le \text{players} \le 17$。

### 输入输出示例

```text
rank_hand([(2,0), (2,1), (2,2)])   -> (3, 2)              # 三条 2
rank_hand([(14,0), (13,0), (12,0)]) -> (2, 14, 13, 12)    # 同花 A 高，比三条 2 小
rank_hand([(9,0), (9,1), (13,2)])  -> (1, 9, 13)          # 对子 9 带 K，比对子 8 带 A 大
rank_hand([(14,0), (10,1), (5,2)]) == rank_hand([(14,3), (10,2), (5,1)])  -> True  # 只差花色，并列
```

### 解题思路与正确性

评估器的每个分支都输出「等级 + 破平局点数」：三条只需要那个点数；同花和高牌按三张点数降序；对子先放对子的点数，再放单张。因为等级放在 tuple 第一位，不同牌型之间只看等级，同牌型才继续比点数，字典序比较就和规则一致。

发牌用一次 `random.Random(seed).sample` 抽出所有需要的牌，保证全局没有重复，同一个 seed 结果可复现。弃牌只是在比较前把不满足条件的玩家筛掉，和评估逻辑互相独立。所有分数相同的最高者都算赢家，所以并列会返回多个下标。

### 完整参考实现（Python 3）

```python
import random
from collections import Counter

HIGH_CARD, PAIR, FLUSH, TRIPS = 0, 1, 2, 3


def validate_hand(hand):
    if len(hand) != 3 or len(set(hand)) != 3:
        raise ValueError(f"a hand must be 3 distinct cards, got {hand!r}")
    for rank, suit in hand:
        if not 2 <= rank <= 14 or not 0 <= suit < 4:
            raise ValueError(f"invalid card: {(rank, suit)!r}")


def rank_hand(hand, flush=True):
    """把一手牌编码成可直接比较的 tuple：(牌型等级, 用于破平局的点数...)。

    等级：三条 3 > 同花 2 > 对子 1 > 高牌 0。flush=False 时不识别同花（第一阶段规则）。
    """
    validate_hand(hand)
    counts = Counter(rank for rank, _ in hand)
    ranks_desc = sorted((rank for rank, _ in hand), reverse=True)
    if 3 in counts.values():
        return (TRIPS, ranks_desc[0])
    if flush and len({suit for _, suit in hand}) == 1:
        return (FLUSH, *ranks_desc)
    if 2 in counts.values():
        pair = next(rank for rank, count in counts.items() if count == 2)
        kicker = next(rank for rank, count in counts.items() if count == 1)
        return (PAIR, pair, kicker)
    return (HIGH_CARD, *ranks_desc)


def deal(players, seed=0, discard=False):
    """无放回地给每人发 3 张牌。返回 (各家手牌, 赢家下标列表, 弃牌下标列表)。

    discard=True 时只有对子或三条留下，其余弃牌且不补牌；所有人都弃牌时赢家为空。
    """
    if not 1 <= players <= 17:
        raise ValueError(f"players must be in 1..17, got {players}")
    deck = [(rank, suit) for rank in range(2, 15) for suit in range(4)]
    cards = random.Random(seed).sample(deck, players * 3)  # 一次抽样保证全局不重复
    hands = [cards[i * 3:i * 3 + 3] for i in range(players)]

    folded = []
    if discard:
        folded = [i for i, hand in enumerate(hands) if len({rank for rank, _ in hand}) == 3]
    live = [i for i in range(players) if i not in folded]

    scores = {i: rank_hand(hands[i]) for i in live}
    best = max(scores.values(), default=None)
    winners = [i for i in live if scores[i] == best]
    return hands, winners, folded
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert rank_hand([(2, 0), (2, 1), (2, 2)]) > rank_hand([(14, 0), (13, 0), (12, 0)])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
# 三条 > 同花；同为对子时先比对子点数，再比单张
assert rank_hand([(2, 0), (2, 1), (2, 2)]) > rank_hand([(14, 0), (13, 0), (12, 0)])
assert rank_hand([(9, 0), (9, 1), (13, 2)]) > rank_hand([(8, 0), (8, 1), (14, 2)])

# 点数完全相同、花色不同时并列，花色不破平局
assert rank_hand([(14, 0), (10, 1), (5, 2)]) == rank_hand([(14, 3), (10, 2), (5, 1)])

# 关闭同花规则后，同花只算高牌
assert rank_hand([(14, 0), (13, 0), (12, 0)], flush=False)[0] == HIGH_CARD

# 17 人正好发 51 张不重复的牌，且至少有一个赢家
hands, winners, _ = deal(17, 3)
assert len({card for hand in hands for card in hand}) == 51
assert winners

# 同一个 seed 结果可复现
assert deal(3, 8) == deal(3, 8)

# 弃牌规则：留下的人都至少有对子
hands, winners, folded = deal(17, 3, discard=True)
for i in range(17):
    if i not in folded:
        assert rank_hand(hands[i])[0] in (PAIR, TRIPS)
assert set(winners).isdisjoint(folded)
```

### 复杂度与追问

每手牌固定 3 张，评估是 $O(1)$。设玩家数为 $P$，发牌、评估和选赢家都是 $O(P)$，空间 $O(P)$。

- 加顺子：在评估器里加一个等级，并确定 A-2-3 是否算顺子、同花顺是否单独成一档。这些是规则问题，不是往 tuple 里加一位就能自动处理的，要先和面试官定下来。
- 加万能牌（wildcard）：评估时要枚举万能牌可能代表的所有牌，取得分最高的组合。
- 弃牌后补牌：补牌会改变牌堆的剩余顺序，发牌流程要改成按需从牌堆抽，而不是一次性抽样，同时要在日志里记录每一步。
