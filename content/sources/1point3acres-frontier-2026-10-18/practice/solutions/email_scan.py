import re
from email.utils import parseaddr

ADDRESS = re.compile(r"[A-Za-z0-9._+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+")


def split_records(text):
    """单次扫描：去掉括号注释（可嵌套），只在引号和注释之外的分号处切分记录。"""
    records = []
    current = []
    comment_depth = 0
    in_quotes = False
    escaped = False
    for char in text:
        if escaped:
            # 反斜杠后的字符按字面处理；注释里的内容一律丢弃
            if not comment_depth:
                current.append(char)
            escaped = False
            continue
        if char == "\\":
            if not comment_depth:
                current.append(char)
            escaped = True
            continue
        if comment_depth:
            if char == "(":
                comment_depth += 1
            elif char == ")":
                comment_depth -= 1
            continue
        if char == '"':
            in_quotes = not in_quotes
            current.append(char)
        elif char == "(" and not in_quotes:
            comment_depth = 1
        elif char == ";" and not in_quotes:
            records.append("".join(current))
            current = []
        else:
            current.append(char)
    if comment_depth or in_quotes or escaped:
        raise ValueError("unclosed quote, comment or escape at end of input")
    records.append("".join(current))
    return records


def emails(text):
    """返回合法邮箱地址，按完整地址忽略大小写去重，保留第一次出现时的写法。"""
    seen = set()
    result = []
    for record in split_records(text):
        address = parseaddr(record)[1]  # 处理「显示名 <地址>」和裸地址两种写法
        if not ADDRESS.fullmatch(address):
            continue  # 非法记录直接跳过
        key = address.casefold()
        if key not in seen:
            seen.add(key)
            result.append(address)
    return result


def test():
    # 引号里的分号、注释里的分号都不切分记录；重复地址只保留一次
    assert emails('"A;B" <a@x.com>; a@x.com; C(c;d)<c@y.org>') == ["a@x.com", "c@y.org"]

    # 嵌套注释被整体去掉；非法记录跳过；去重忽略大小写
    assert emails("a@x.com (outer (inner;)); BAD; A@X.COM") == ["a@x.com"]

    # 首次出现的大小写被保留
    assert emails("Bob@Example.com; bob@example.com") == ["Bob@Example.com"]

    # 未闭合的注释或引号报错
    for bad in ["a@x.com (", '"a <a@x.com>']:
        try:
            emails(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{bad!r} should raise ValueError")


if __name__ == "__main__":
    test()
