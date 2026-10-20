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


def test():
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


if __name__ == "__main__":
    test()
