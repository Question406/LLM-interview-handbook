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
            if not inside(square) or sum(square) % 2 != 1 or piece not in (-KING, -MAN, MAN, KING):
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
        legal = self.options(self.turn, captures_only=self.forced is not None, only=self.forced)
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


def test():
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


if __name__ == "__main__":
    test()
