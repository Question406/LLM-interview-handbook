def to_signed_int(digits, negative):
    """把去掉若干位后的数字串转回整数；串为空时视为 0。"""
    value = int(digits or "0")
    return -value if negative else value


def remove_all_fives(n):
    """删除 n 的十进制表示（不含负号）中所有的 5，保留符号。"""
    digits = str(abs(n)).replace("5", "")
    return to_signed_int(digits, n < 0)


def remove_one_five(n):
    """恰好删除一个 5，返回能得到的最大整数；n 中没有 5 时抛 ValueError。"""
    digits = str(abs(n))
    candidates = [
        to_signed_int(digits[:i] + digits[i + 1:], n < 0)
        for i, digit in enumerate(digits)
        if digit == "5"
    ]
    if not candidates:
        raise ValueError(f"{n} contains no digit 5")
    # 每个候选都转成带符号整数再比较，负数时自然选出绝对值最小的那个
    return max(candidates)


def test():
    # 删全部和删一个的区别
    assert remove_all_fives(515) == 1
    assert remove_one_five(515) == 51

    # 负数：删一个时要让绝对值尽量小
    assert remove_one_five(-515) == -15
    assert remove_all_fives(-55) == 0

    # 删完为空的情况视为 0
    assert remove_one_five(5) == 0
    assert remove_all_fives(0) == 0

    # 没有 5 时删一个报错
    try:
        remove_one_five(123)
    except ValueError:
        pass
    else:
        raise AssertionError("remove_one_five(123) should raise ValueError")


if __name__ == "__main__":
    test()
