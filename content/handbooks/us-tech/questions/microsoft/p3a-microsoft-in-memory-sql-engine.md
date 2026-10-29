---
id: p3a-microsoft-in-memory-sql-engine
section: microsoft
order: 601
level: A
title: Microsoft AI / Copilot：CSV 初始化的内存 SQL 引擎
quick: >-
  我会先确认 CSV 的引号、转义和字段类型，再把查询拆成筛选、排序、投影。这里用 csv.reader 解析，所有值按字符串比较，所以 "10" 会排在
  "2" 前；投影放最后，避免提前丢掉排序所需的列。
companies:
  - microsoft
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Microsoft AI
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 1Point3Acres · Microsoft AI / Copilot · in-memory-sql-engine
    url: >-
      https://www.1point3acres.com/interview/problems/company/microsoft/in-memory-sql-engine
    type: secondary
---

## 题目描述

实现一个面向 CSV 字符串的简化内存表查询器，不需要解析完整 SQL。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`Table(csv_text)` 读取标准 CSV：首行为唯一列名，数据行列数一致，双引号允许字段内包含逗号及转义引号。所有单元格都是字符串，不做数字类型推断。`insert(row)` 接收恰含全部列名的字符串值字典并追加一行。

`query(columns,where=(),order=())` 返回投影后的行字典列表。columns 是要返回的列名；where 是 `(列名,比较符,比较值)` 列表，以 AND 连接，支持 `==`、`!=`、`<`、`>`；比较均按字符串字典序。order 是 `(列名,descending)` 列表，前面的列优先，完全同键时保留插入顺序。最多 10000 行、100 列。

### 示例

```text
CSV 内容：
name,score
a,2
b,10
query(["name"],order=[("score",False)]) = [{"name":"b"},{"name":"a"}]
query(["name"],where=[("score",">","1")]) = [{"name":"a"},{"name":"b"}]
```

## 解题思路与参考答案

我会先按约定正确解析 CSV，再依次执行筛选、排序和投影。例如字段里有 `"x,y"` 时，直接按逗号切分就会把一列拆成两列，因此解析交给 `csv.reader`。

## 题目

用一段 CSV 文本初始化一张内存表，然后分阶段支持 SELECT、WHERE 和 ORDER BY。

> 来源：一亩三分地 Microsoft 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理；`realInterview` 只表示网站把它收录为面经题型。下面的接口、约束和测试是手册补的练习约定。

## 思路

先和面试官确认 CSV 的规则：字段里能不能有引号和逗号，怎么转义，所有字段是不是都当字符串，还是要推断类型。这些规则定下来之后再建表结构。如果题目给的是简化的 CSV 契约，就按契约处理，不要自己扩成一个完整数据库。

查询的执行顺序是先筛选、再排序、最后投影。多个条件用 AND 连接，排序键越靠前优先级越高；这些规则先固定下来，后续扩展才不会改变已有查询的含义。

相关题：[[p3a-openai-in-memory-database-sql]]（同一份练习代码，那道题更关注分阶段扩展和索引优化）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Table(csv_text)`：首行是列名，列名不能重复；每行宽度必须和表头一致。CSV 支持标准的双引号转义，引号里可以有逗号。
- `insert(row)`：`row` 是字典，列必须和表头完全一致，值必须是字符串。
- `query(columns, where=(), order=())`：返回字典列表。`where` 是一组用 AND 连接的 `(column, op, value)`，`op` 只能是 `==`、`!=`、`<`、`>`；`order` 是 `(column, descending)` 列表，越靠前优先级越高；最后只保留 `columns` 里的列。
- 引用不存在的列或不支持的运算符，抛 `ValueError`。
- 所有单元格都按字符串比较，所以 `"10"` 排在 `"2"` 前面；数值语义留给带类型的扩展版本。不支持 LIMIT、JOIN，也不解析 SQL 文本。最多 $10^4$ 行、100 列。

### 输入输出示例

```text
table = Table("name,score\na,2\nb,10\n")
table.query(["name"], order=[("score", False)])    -> [{"name": "b"}, {"name": "a"}]
table.query(["name"], where=[("score", ">", "1")]) -> [{"name": "a"}, {"name": "b"}]
```

按字符串比较，`"10" < "2"`，所以升序时 b 排在前面；`"2"` 和 `"10"` 都大于 `"1"`，筛选后两行都在。

### 解题思路与正确性

CSV 的引号和转义交给标准库 `csv.reader` 处理，自己按逗号切分会在 `"x,y"` 这种字段上出错。

`query` 先校验所有列名和运算符，再按固定顺序执行：筛选、排序、投影。投影放在最后，这样即使排序列不在输出列里也能排序。

多键排序利用了 Python 排序的稳定性：从优先级最低的键开始，依次对每个键排一遍。后排的键决定主顺序，前面排好的顺序在相等时被保留下来，结果就是指定的优先级。

运算符通过一张固定的映射表查到 `operator.eq` 等函数，不调用 `eval`，所以查询参数不可能变成任意 Python 代码执行。

### 完整参考实现（Python 3）

```python
import csv
import io
import operator

OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    ">": operator.gt,
}


class Table:
    """用 CSV 文本初始化的内存表；所有单元格都按字符串存储和比较。"""

    def __init__(self, csv_text):
        rows = list(csv.reader(io.StringIO(csv_text)))
        if not rows or not rows[0]:
            raise ValueError("missing header")
        header = rows[0]
        if len(set(header)) != len(header):
            raise ValueError("duplicate column names")
        self.columns = header
        self.rows = []
        for row in rows[1:]:
            if len(row) != len(self.columns):
                raise ValueError(f"row width {len(row)} != {len(self.columns)}")
            self.insert(dict(zip(self.columns, row)))

    def insert(self, row):
        """插入一行；row 的列必须和表头完全一致，值必须是字符串。"""
        if set(row) != set(self.columns):
            raise ValueError("row columns must match the header")
        if not all(isinstance(value, str) for value in row.values()):
            raise ValueError("cell values must be str")
        self.rows.append(dict(row))

    def _check_column(self, column):
        if column not in self.columns:
            raise ValueError(f"unknown column: {column!r}")

    def query(self, columns, where=(), order=()):
        """where 是 AND 连接的 (column, op, value)；order 是 (column, descending) 列表，越靠前优先级越高。

        执行顺序：先筛选，再排序，最后投影，所以可以按不在 columns 里的列排序。
        """
        for column in columns:
            self._check_column(column)
        for column, op, _ in where:
            self._check_column(column)
            if op not in OPERATORS:
                raise ValueError(f"unsupported operator: {op!r}")
        for column, _ in order:
            self._check_column(column)

        matched = [
            row
            for row in self.rows
            if all(OPERATORS[op](row[column], value) for column, op, value in where)
        ]
        # Python 排序是稳定的：从优先级最低的键开始排，最后一次排序的键优先级最高
        for column, descending in reversed(order):
            matched.sort(key=lambda row: row[column], reverse=descending)
        return [{column: row[column] for column in columns} for row in matched]
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert table.query(["name"], order=[("score", False)]) == [{"name": "b"}, {"name": "a"}]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


# 字符串比较："10" < "2"，所以升序时 b 在前；排序列不在投影里也可以
table = Table("name,score\na,2\nb,10\n")
assert table.query(["name"], order=[("score", False)]) == [{"name": "b"}, {"name": "a"}]
assert table.query(["name"], where=[("score", ">", "1")]) == [
    {"name": "a"},
    {"name": "b"},
]

# 带引号的字段里可以有逗号
table = Table('name,note\na,"x,y"\n')
assert table.query(["note"]) == [{"note": "x,y"}]

# 插入后可以按等值条件查到
table.insert({"name": "b", "note": "z"})
assert table.query(["name"], [("note", "==", "z")]) == [{"name": "b"}]

# 多键排序：先按 team 升序，同队再按 name 降序
table = Table("name,team\na,x\nb,y\nc,x\n")
assert table.query(["name"], order=[("team", False), ("name", True)]) == [
    {"name": "c"},
    {"name": "a"},
    {"name": "b"},
]

# 非法输入
expect_value_error(Table, "a,a\n1,2\n")
expect_value_error(Table, "a,b\n1\n")
expect_value_error(table.insert, {"name": "d"})
expect_value_error(table.query, ["missing"])
expect_value_error(table.query, ["name"], [("team", "LIKE", "x")])
```

### 复杂度与追问

设行数为 N、表的列数为 C、条件数为 P、排序键数为 K、输出列数为 $C_{out}$。筛选是 O(NP)，排序是 O(K · N log N)，投影是 O(N · $C_{out}$)，存储占 O(NC)。

- 怎么加索引？对常用的等值条件列建哈希索引（值到行号列表），等值查询可以从 O(N) 降到 O(命中行数)。代价是每次插入都要更新索引；如果有范围查询，可以改用有序结构。索引里的比较方式要和表的比较语义一致，比如都按字符串比较。
- 要支持数值列怎么办？在表头或单独的 schema 里声明列类型，建表和插入时转换并校验，比较时按类型比较。
