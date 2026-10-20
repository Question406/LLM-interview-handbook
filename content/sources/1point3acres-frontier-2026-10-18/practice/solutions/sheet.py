import ast
import re

CELL = re.compile(r"[A-Z]+[1-9][0-9]*")


def check_cell(cell):
    if not isinstance(cell, str) or not CELL.fullmatch(cell):
        raise ValueError(f"invalid cell name: {cell!r}")


def parse_value(value):
    """整数直接存成常量节点；以 = 开头的字符串解析成表达式 AST。"""
    if type(value) is int:  # 排除 bool
        return ast.Constant(value=value)
    if isinstance(value, str) and value.startswith("="):
        try:
            return ast.parse(value[1:], mode="eval").body
        except SyntaxError:
            raise ValueError(f"cannot parse formula: {value!r}") from None
    raise ValueError(f"value must be an int or a formula starting with '=': {value!r}")


def evaluate_all(formulas):
    """计算所有单元格的值；遇到环或白名单之外的语法抛 ValueError。"""
    values = {}
    visiting = set()  # 当前递归路径上的单元格，用来发现环

    def resolve(cell):
        if cell in values:
            return values[cell]
        if cell in visiting:
            raise ValueError(f"cycle through {cell}")
        visiting.add(cell)
        result = evaluate(formulas[cell]) if cell in formulas else 0  # 未赋值的格子是 0
        visiting.remove(cell)
        values[cell] = result
        return result

    def evaluate(node):
        # 只认白名单里的节点，不调用 eval
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.Name) and CELL.fullmatch(node.id):
            return resolve(node.id)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -evaluate(node.operand)
        if isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
        raise ValueError(f"unsupported formula syntax: {ast.dump(node)}")

    for cell in formulas:
        resolve(cell)
    return values


class Sheet:
    """每次 set 都重算整张表，所以 get 是 O(1) 查表。"""

    def __init__(self):
        self.formulas = {}
        self.values = {}

    def set(self, cell, value):
        check_cell(cell)
        trial = dict(self.formulas)
        trial[cell] = parse_value(value)
        values = evaluate_all(trial)  # 失败时直接抛错，旧状态没被动过
        self.formulas = trial
        self.values = values

    def get(self, cell):
        check_cell(cell)
        return self.values.get(cell, 0)


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    sheet = Sheet()
    sheet.set("A1", 2)
    sheet.set("B1", "=A1*3+1")
    assert sheet.get("B1") == 7

    # 引入环的写入被拒绝，旧值保持不变
    expect_value_error(sheet.set, "A1", "=B1")
    assert sheet.get("A1") == 2
    assert sheet.get("B1") == 7

    # 改上游后，下游跟着变
    sheet.set("A1", 4)
    assert sheet.get("B1") == 13

    # 括号、一元负号、未赋值的格子
    sheet.set("C1", "=-(A1 - D9) * 2")
    assert sheet.get("C1") == -8

    # 白名单之外的语法、解析失败、非法格子名
    expect_value_error(sheet.set, "C2", '=__import__("os")')
    expect_value_error(sheet.set, "C2", "=A1/2")
    expect_value_error(sheet.set, "C2", "=A1 +")
    expect_value_error(sheet.set, "a1", 1)
    expect_value_error(sheet.set, "C2", True)
    assert sheet.get("C2") == 0


if __name__ == "__main__":
    test()
