---
id: p3a-xai-checkers-backend-design
section: xai
order: 606
level: A
title: xAI：跳棋后端：棋盘、合法走子和胜负
quick: >-
  我会先确认强制跳吃、连跳和升王规则，再把 move
  实现成先校验、后整体更新的状态转移。服务端保存权威局面，客户端只提交走法；非法操作不改状态，连跳结束后才换手并检查胜负。
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · xAI · checkers-backend-design
    url: >-
      https://www.1point3acres.com/interview/problems/company/xai/checkers-backend-design
    type: secondary
---

## 题目描述

实现一个明确规则版本的 8×8 美式跳棋后端。维护棋盘、当前行棋方和必须连跳的棋子，接受一步移动后更新棋盘，并在对手没有棋子或没有合法移动时报告胜者。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `Checkers(board, turn=1)`：8×8 棋盘，`board` 是 `{(row, col): piece}`。`±1` 是普通子、`±2` 是王；正方往行号增大的方向走，负方往行号减小的方向走。棋子只能放在深色格，即 $(r + c) \bmod 2 = 1$。
- 普通子只能向前斜走一格或向前斜跳吃；王四个斜向都可以，但每次也只走一格。
- 全局有跳吃时禁止普通步。吃子后同一枚棋子还能继续吃就必须连跳，由 `forced` 记录；普通子到对方底线升王，并结束本回合。
- `move(src, dst)`：合法则更新局面；非法抛 `ValueError`，棋盘不变。对手无子或无合法步时返回本方（`1` 或 `-1`）作为胜者，否则返回 `None`。
- 最多 24 枚棋子。这是一个明确的规则变体，不混用国际跳棋的后吃和飞王规则。

### 示例

```text
Checkers({(2, 1): 1, (3, 2): -1}).move((2, 1), (4, 3))   -> 1      # 跳吃掉负方最后一子
g = Checkers({(2, 1): 1, (3, 2): -1, (5, 4): -1})
g.move((2, 1), (4, 3))   -> None，g.forced == (4, 3)，仍是正方回合
g.move((4, 3), (6, 5))   -> 1
Checkers({(2, 1): 1, (3, 2): -1, (5, 4): -1}).move((2, 1), (3, 0))   -> ValueError（有跳吃必须吃）
```

## 解题思路与参考答案

我会先固定规则变体，再让服务端按「生成合法动作、校验走法、更新局面」执行。比如还有跳吃机会时，玩家提交普通步就要拒绝，棋盘保持原样；吃完还能连跳，则仍由同一枚棋子行动。

## 题目

在限定时间内设计并部分实现一个 checkers（跳棋）游戏的后端：表示棋盘，校验并执行玩家的走子，判断胜负。题目更看重先把核心规则做对、形成可运行的 feedback loop，再讨论服务端架构。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理；`realInterview` 只表示网站把它收录为面经题型。下面的规则变体、接口、约束和测试是手册补的练习约定。

## 思路

先和面试官把规则说清楚，跳棋的变体很多：是美式 8×8 还是国际 10×10；有跳吃时是否必须吃；连跳是否强制；普通子能否后吃；王能否走多格（飞王）；升王后能否继续连跳。规则不同，代码差别很大。

规则确定后，把一步走法当成状态转移：给定当前局面，非法就拒绝，合法才产生新局面。实现顺序是：

1. 生成当前一方的所有合法动作，有任何跳吃就只保留跳吃（强制吃子）；
2. 在合法动作里找玩家提交的那一步，找不到就拒绝，且不改任何状态；
3. 执行后检查升王、是否必须继续连跳，最后换手并判断对方还有没有合法步。

服务端保存权威局面，客户端只提交「我想从哪走到哪」。先把一局棋的规则校验、执行和胜负判断跑通，再扩展房间、断线重连和持久化。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Checkers(board, turn=1)`：8×8 棋盘，`board` 是 `{(row, col): piece}`。`±1` 是普通子、`±2` 是王；正方往行号增大的方向走，负方往行号减小的方向走。棋子只能放在深色格，即 $(r + c) \bmod 2 = 1$，否则抛 `ValueError`。
- 普通子只能向前斜走一格或向前斜跳吃；王四个斜向都可以，但每次也只走一格。
- 全局有跳吃时禁止普通步。吃子后同一枚棋子还能继续吃就必须连跳，由 `forced` 记录；普通子到对方底线升王，并结束本回合。
- `move(src, dst)`：合法则更新局面；非法抛 `ValueError`，棋盘不变。对手无子或无合法步时返回本方（`1` 或 `-1`）作为胜者，否则返回 `None`。
- 最多 24 枚棋子。这是一个明确的规则变体，不混用国际跳棋的后吃和飞王规则。

### 输入输出示例

```text
Checkers({(2, 1): 1, (3, 2): -1}).move((2, 1), (4, 3))   -> 1      # 跳吃掉负方最后一子
g = Checkers({(2, 1): 1, (3, 2): -1, (5, 4): -1})
g.move((2, 1), (4, 3))   -> None，g.forced == (4, 3)，仍是正方回合
g.move((4, 3), (6, 5))   -> 1
Checkers({(2, 1): 1, (3, 2): -1, (5, 4): -1}).move((2, 1), (3, 0))   -> ValueError（有跳吃必须吃）
```

### 解题思路与正确性

`options` 先收集所有跳吃，只要存在就丢弃普通步，强制吃子由此保证。连跳期间用 `only=forced` 只看刚移动的那枚棋子、`captures_only=True` 只允许继续吃，连跳结束才换手。升王结束连跳是这份练习的约定。

`move` 先在完整的合法动作列表里找到这一步，再修改棋盘，所以非法操作不会留下半更新的状态。胜负在换手之后判断：新的一方没有任何合法动作（包括没有棋子）时，刚走完的一方获胜。

### 完整参考实现（Python 3）

```python
MAN, KING = 1, 2  # 棋子值：正为一方、负为另一方；绝对值 1 是普通子，2 是王
SIZE = 8


def inside(square):
    return len(square) == 2 and 0 <= square[0] < SIZE and 0 <= square[1] < SIZE


class Checkers:
    """8x8 跳棋。board: {(row, col): piece}；正方往行号增大的方向走，负方往行号减小的方向走。"""

    def __init__(self, board, turn=1):
        if turn not in (-1, 1):
            raise ValueError("turn must be 1 or -1")
        for square, piece in board.items():
            if (
                not inside(square)
                or sum(square) % 2 != 1
                or piece not in (-KING, -MAN, MAN, KING)
            ):
                raise ValueError(f"invalid piece {piece!r} at {square!r}")
        self.board = dict(board)
        self.turn = turn
        self.forced = None  # 连跳中必须继续行动的那枚棋子的位置

    def options(self, side, captures_only=False, only=None):
        """返回 side 的合法动作 (src, dst, captured)。有任何跳吃时只返回跳吃。

        only 限定只看某一枚棋子；captures_only 表示没有跳吃时也不返回普通步。
        """
        captures = []
        simple = []
        for src, piece in self.board.items():
            if piece * side <= 0 or (only is not None and src != only):
                continue
            row_steps = (-1, 1) if abs(piece) == KING else (side,)  # 普通子只能向前
            for dr in row_steps:
                for dc in (-1, 1):
                    near = (src[0] + dr, src[1] + dc)
                    far = (src[0] + 2 * dr, src[1] + 2 * dc)
                    jumps_enemy = self.board.get(near, 0) * side < 0
                    if inside(far) and jumps_enemy and far not in self.board:
                        captures.append((src, far, near))
                    if inside(near) and near not in self.board:
                        simple.append((src, near, None))
        if captures or captures_only:
            return captures
        return simple

    def move(self, src, dst):
        """执行一步；非法时抛 ValueError 且不改棋盘。返回胜者（1 或 -1），未分胜负返回 None。"""
        legal = self.options(
            self.turn, captures_only=self.forced is not None, only=self.forced
        )
        choice = next((action for action in legal if action[:2] == (src, dst)), None)
        if choice is None:
            raise ValueError(f"illegal move {src} -> {dst}")

        captured = choice[2]
        piece = self.board.pop(src)
        self.board[dst] = piece
        if captured is not None:
            del self.board[captured]

        last_row = SIZE - 1 if piece > 0 else 0
        promoted = abs(piece) == MAN and dst[0] == last_row
        if promoted:
            self.board[dst] = KING * self.turn

        # 吃子后同一枚棋子还能继续吃，就必须连跳，回合不结束；升王会结束连跳
        if captured is not None and not promoted and self.options(self.turn, True, dst):
            self.forced = dst
            return None

        self.forced = None
        mover = self.turn
        self.turn = -mover
        if not self.options(self.turn):  # 对手无子或无合法步
            return mover
        return None
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert game.board == before  # 非法操作不留下半更新的状态` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_illegal(game, src, dst):
    before = dict(game.board)
    try:
        game.move(src, dst)
    except ValueError:
        assert game.board == before  # 非法操作不留下半更新的状态
        return
    raise AssertionError(f"{src} -> {dst} should be illegal")


# 跳吃掉对方最后一枚子，正方获胜
game = Checkers({(2, 1): 1, (3, 2): -1})
assert game.move((2, 1), (4, 3)) == 1
assert (3, 2) not in game.board

# 连跳：第一跳后回合不切换，必须由同一枚棋子继续
board = {(2, 1): 1, (3, 2): -1, (5, 4): -1}
game = Checkers(board)
assert game.move((2, 1), (4, 3)) is None
assert game.forced == (4, 3)
assert game.turn == 1
assert game.move((4, 3), (6, 5)) == 1

# 有跳吃时不能走普通步
expect_illegal(Checkers(board), (2, 1), (3, 0))

# 走到末排升王，王可以后退
game = Checkers({(6, 1): 1, (3, 0): -1})
assert game.move((6, 1), (7, 2)) is None
assert game.board[(7, 2)] == KING
game.move((3, 0), (2, 1))
game.move((7, 2), (6, 1))
assert game.board[(6, 1)] == KING

# 普通子不能后退；棋盘必须放在深色格
expect_illegal(Checkers({(3, 2): 1, (7, 0): -1}), (3, 2), (2, 1))
try:
    Checkers({(0, 0): 1})
except ValueError:
    pass
else:
    raise AssertionError("light square should be rejected")
```

### 复杂度与追问

设棋子数为 n（不超过 24）。生成合法动作要看每枚棋子的最多 4 个方向，O(n)；`move` 也是 O(n)。空间就是棋盘本身，O(n)。

- 多个客户端同时操作：服务端为每局维护一个版本号，客户端提交走法时带上它看到的版本，版本不一致就拒绝并下发最新局面，避免重复提交或乱序。
- 持久化和重连：每局保存初始局面加走子日志，重连时下发当前局面和版本即可；日志还能用来回放。
- 和棋：需要额外规则，例如一定步数内无吃子也无普通子前进，或者同一局面重复出现。
- AI 选最优走法是另一个问题，需要 minimax / alpha-beta 搜索，不属于后端的规则校验。
