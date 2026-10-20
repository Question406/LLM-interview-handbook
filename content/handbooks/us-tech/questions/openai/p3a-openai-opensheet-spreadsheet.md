---
id: p3a-openai-opensheet-spreadsheet
section: openai
order: 624
level: A
title: "OpenAI：电子表格：公式、依赖、环与 O(1) 读取"
quick: "解析公式建立正向和反向依赖，写入前在新图上检查环，有环就拒绝并保持原表；要 O(1) 读取，就在写入时按拓扑顺序重算所有受影响的单元格。"
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
  - title: "1Point3Acres · OpenAI · opensheet-spreadsheet"
    url: https://www.1point3acres.com/interview/problems/company/openai/opensheet-spreadsheet
    type: secondary
---

## 题目

实现一个电子表格：单元格可以存整数，也可以存引用其他单元格的公式；写入会造成循环依赖时要拒绝。追问是怎么让 `getCell` 变成 O(1)。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

先解析公式，得到它引用了哪些单元格，建出依赖图：正向边是「我依赖谁」，反向边是「谁依赖我」。写入新公式之前，先在新图上检查有没有环，有环就拒绝，表格保持原样。

求值策略取决于读写比例：

- 懒求值加缓存：写的时候只更新公式、让下游缓存失效，读的时候再算。适合写多读少。
- 写时更新：每次写入后，按拓扑顺序重算所有受影响的单元格，读取直接查表，O(1)。题目追问的就是这种。

替换一个单元格的公式时，要先删掉旧公式留下的依赖边，再加新边，否则会出现「早就不引用了却还在被触发重算」的脏边，甚至误报环。

公式解析不要用 `eval`。用 `ast` 解析后只接受白名单里的节点，其他一律拒绝，否则 `=__import__("os")` 这类输入就能执行任意代码。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Sheet.set(cell, value)`：`cell` 的格式是 `[A-Z]+[1-9][0-9]*`。`value` 是整数，或以 `=` 开头的公式。公式里只允许整数、单元格名、括号、`+`、`-`、`*` 和一元负号；函数调用、除法和其他 Python 语法都抛 `ValueError`。
- 写入如果引入环、公式非法或解析失败，抛 `ValueError` 并保持表格原样。
- `Sheet.get(cell)`：O(1) 返回当前值，未赋值的单元格是 0。
- 已赋值的单元格不超过 100 个。

### 输入输出示例

```text
set("A1", 2)
set("B1", "=A1*3+1")
get("B1")            -> 7
set("A1", "=B1")     -> ValueError（A1 -> B1 -> A1 成环），A1 仍是 2
set("A1", 4)
get("B1")            -> 13
```

### 解题思路与正确性

这份实现选了最简单的写时更新：每次 `set` 都在一份公式副本 `trial` 上重算整张表，算完再整体替换 `self.formulas` 和 `self.values`。任何一步出错都会在替换前抛出，所以非法写入不会留下半更新的状态。

`resolve` 用 `visiting` 记录当前递归路径上的单元格。如果在求值过程中又回到了路径上的某个单元格，说明有环。算完的值放进 `values` 缓存，每个单元格只算一次。

求值只处理白名单里的 AST 节点，碰到函数调用、属性访问、除法等其他节点直接抛错。解析阶段的 `SyntaxError` 也转成 `ValueError`，调用方只需要处理一种异常。

### 完整参考实现（Python 3）

```python
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
```

### 可执行测试

```python
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
```

### 复杂度与追问

设所有公式的 AST 节点总数为 F、引用边数为 E。每次 `set` 重算整张表，O(F + E)；`get` 是 O(1)；空间是线性的。

如果追问规模变大：维护反向依赖表，写入某个单元格后，只从它出发沿反向边找出受影响的子图，在子图里做拓扑排序再重算。替换公式时要先删掉旧的正向和反向边，再在新边上检查环。

如果追问读多写少还是写多读少：读多就用写时更新，读是 O(1)；写多就用懒求值，写入只标记下游失效，读取时再按需计算并缓存。
