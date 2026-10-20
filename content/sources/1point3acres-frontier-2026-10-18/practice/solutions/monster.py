from copy import deepcopy


def compute_damage(attacker, target, effect):
    """伤害 = attack × 属性倍率，向下取整，至少为 1。没配置的属性组合倍率为 1。"""
    multiplier = effect.get((attacker["element"], target["element"]), 1)
    return max(1, int(attacker["attack"] * multiplier))


def choose_target(attacker, targets, effect, smart):
    """普通模式打第一个存活的敌人；smart 模式打这一下伤害最高的，并列取靠前的。"""
    if not smart:
        return targets[0]
    return max(targets, key=lambda target: compute_damage(attacker, target, effect))  # max 并列时返回第一个


def alive(team):
    return [monster for monster in team if monster["hp"] > 0]


def battle(team0, team1, effect=None, smart=False):
    """两队轮流攻击，team0 先手，直到一方全灭。返回 (winner, logs)，不修改输入。

    winner 是 0、1，或两队一开始都为空时的 None；
    logs 每项是 (攻击者, 目标, 伤害, 目标剩余 hp)。
    """
    teams = [deepcopy(team0), deepcopy(team1)]
    effect = effect or {}
    for team in teams:
        for monster in team:
            if monster["hp"] <= 0 or monster["attack"] <= 0:
                raise ValueError(f"hp and attack must be positive: {monster!r}")

    logs = []
    side = 0
    while alive(teams[0]) and alive(teams[1]):
        attacker = alive(teams[side])[0]
        target = choose_target(attacker, alive(teams[1 - side]), effect, smart)
        damage = compute_damage(attacker, target, effect)
        target["hp"] = max(0, target["hp"] - damage)
        logs.append((attacker["name"], target["name"], damage, target["hp"]))
        side = 1 - side

    if alive(teams[0]):
        winner = 0
    elif alive(teams[1]):
        winner = 1
    else:
        winner = None
    return winner, logs


def test():
    def monster(name, hp, attack, element):
        return {"name": name, "hp": hp, "attack": attack, "element": element}

    # 先手一击打死对方，输入不被修改
    team_a = [monster("A", 3, 2, "fire")]
    team_b = [monster("B", 2, 1, "water")]
    assert battle(team_a, team_b) == (0, [("A", "B", 2, 0)])
    assert team_a[0]["hp"] == 3

    # 一方为空，另一方直接获胜；两方都空则没有赢家
    assert battle([], team_b)[0] == 1
    assert battle([], []) == (None, [])

    # smart 模式选伤害最高的目标：火克水，打 D 是 4 点，打 C 是 2 点
    team_c = [monster("C", 1, 1, "wood"), monster("D", 2, 1, "water")]
    winner, logs = battle(team_a, team_c, {("fire", "water"): 2}, smart=True)
    assert logs[0][1] == "D"

    # 普通模式打第一个存活者；倍率很小时伤害至少为 1
    winner, logs = battle(team_a, team_c, {("fire", "wood"): 0.1})
    assert logs[0] == ("A", "C", 1, 0)

    # 非法输入
    try:
        battle([monster("E", 0, 1, "fire")], team_b)
    except ValueError:
        pass
    else:
        raise AssertionError("hp 0 should be rejected")


if __name__ == "__main__":
    test()
